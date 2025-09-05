#!/usr/bin/env python3
"""
Complete Web Application for Student Math Performance Prediction
Includes both the ML API and web interface
"""

import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Global variables for models and data
regression_model = None
classification_model = None
scaler = None
feature_columns = None
training_data = None

def load_models():
    """Load trained models and setup data"""
    global regression_model, classification_model, scaler, feature_columns, training_data
    
    try:
        # Load models
        with open('regression_model.pkl', 'rb') as f:
            regression_model = pickle.load(f)
        
        with open('classification_model.pkl', 'rb') as f:
            classification_model = pickle.load(f)
        
        # Load training data for scaler setup
        csv_file_path = "attached_assets/cleaned-mat-data_1756443115411.csv"
        training_data = pd.read_csv(csv_file_path)
        
        # Setup feature columns and scaler
        feature_columns = [col for col in training_data.columns if col != 'G3']
        X_original = training_data[feature_columns]
        
        scaler = StandardScaler()
        scaler.fit(X_original)
        
        return True
        
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        return False

# HTML Templates
main_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Predictor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f6fa; color: #2c3e50; line-height: 1.6;
        }
        .header { 
            background: #2c3e50; color: white; padding: 1rem 0; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav { 
            max-width: 1200px; margin: 0 auto; display: flex; 
            justify-content: space-between; align-items: center; padding: 0 2rem;
        }
        .nav h1 { font-size: 1.5rem; font-weight: 600; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-link { 
            color: white; text-decoration: none; padding: 0.5rem 1rem;
            border-radius: 4px; transition: background 0.3s;
        }
        .nav-link:hover { background: rgba(255,255,255,0.1); }
        .nav-link.active { background: #3498db; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { 
            background: white; border-radius: 8px; padding: 2rem; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem;
        }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
        .form-group { display: flex; flex-direction: column; margin-bottom: 1rem; }
        .form-group label { font-weight: 500; margin-bottom: 0.5rem; color: #555; }
        .form-group input, .form-group select { 
            padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;
            transition: border-color 0.3s;
        }
        .form-group input:focus, .form-group select:focus { 
            outline: none; border-color: #3498db; 
            box-shadow: 0 0 0 2px rgba(52,152,219,0.1);
        }
        .btn { 
            padding: 1rem 2rem; background: #3498db; color: white; 
            border: none; border-radius: 4px; cursor: pointer; 
            font-size: 1.1rem; font-weight: 600; transition: background 0.3s;
        }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .result-card { 
            background: #f8f9fa; border-radius: 6px; padding: 1.5rem; 
            border-left: 4px solid #3498db; margin-bottom: 1rem;
        }
        .grade-display { font-size: 2rem; font-weight: bold; margin: 1rem 0; }
        .pass { color: #27ae60; }
        .fail { color: #e74c3c; }
        .section-title { 
            color: #2c3e50; margin-bottom: 1.5rem; 
            border-bottom: 2px solid #3498db; padding-bottom: 0.5rem;
        }
        .stats-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; margin-bottom: 2rem;
        }
        .stat-card { 
            background: #f8f9fa; border-radius: 6px; padding: 1.5rem; 
            text-align: center; border-left: 4px solid #3498db;
        }
        .stat-value { font-size: 2rem; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9rem; text-transform: uppercase; }
        .error { background: #e74c3c; color: white; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .success { background: #27ae60; color: white; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .loading { text-align: center; padding: 2rem; color: #7f8c8d; }
        @media (max-width: 768px) { 
            .container { padding: 0 1rem; }
            .form-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <h1>Student Performance Predictor</h1>
            <div class="nav-links">
                <a href="/" class="nav-link {{ 'active' if page == 'predict' else '' }}">Prediction</a>
                <a href="/admin" class="nav-link {{ 'active' if page == 'admin' else '' }}">Admin Panel</a>
            </div>
        </nav>
    </header>
    
    <main class="container">
        {% if page == 'predict' %}
            <div class="card">
                <h2 class="section-title">Student Information Form</h2>
                
                <form id="predictionForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Gender</label>
                            <select name="sex" required>
                                <option value="0">Female</option>
                                <option value="1">Male</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Age</label>
                            <input type="number" name="age" min="15" max="22" value="17" required>
                        </div>
                        <div class="form-group">
                            <label>Family Size</label>
                            <select name="famsize" required>
                                <option value="0">≤ 3 members</option>
                                <option value="1">> 3 members</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Parent Status</label>
                            <select name="Pstatus" required>
                                <option value="0">Apart</option>
                                <option value="1">Together</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Mother's Education</label>
                            <select name="Medu" required>
                                <option value="0">None</option>
                                <option value="1">Primary</option>
                                <option value="2">Secondary</option>
                                <option value="3">Higher Secondary</option>
                                <option value="4">Higher Education</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Father's Education</label>
                            <select name="Fedu" required>
                                <option value="0">None</option>
                                <option value="1">Primary</option>
                                <option value="2">Secondary</option>
                                <option value="3">Higher Secondary</option>
                                <option value="4">Higher Education</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Travel Time to School</label>
                            <select name="traveltime" required>
                                <option value="1">< 15 min</option>
                                <option value="2">15-30 min</option>
                                <option value="3">30min-1hr</option>
                                <option value="4">> 1hr</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Weekly Study Time</label>
                            <select name="studytime" required>
                                <option value="1">< 2 hours</option>
                                <option value="2">2-5 hours</option>
                                <option value="3">5-10 hours</option>
                                <option value="4">> 10 hours</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Past Failures</label>
                            <input type="number" name="failures" min="0" max="4" value="0" required>
                        </div>
                        <div class="form-group">
                            <label>School Support</label>
                            <select name="schoolsup" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Family Support</label>
                            <select name="famsup" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Paid Classes</label>
                            <select name="paid" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Wants Higher Education</label>
                            <select name="higher" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Internet Access</label>
                            <select name="internet" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Romantic Relationship</label>
                            <select name="romantic" required>
                                <option value="0">No</option>
                                <option value="1">Yes</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Family Relationships (1-5)</label>
                            <select name="famrel" required>
                                <option value="1">Very Bad</option>
                                <option value="2">Bad</option>
                                <option value="3">Average</option>
                                <option value="4">Good</option>
                                <option value="5">Excellent</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Free Time (1-5)</label>
                            <select name="freetime" required>
                                <option value="1">Very Low</option>
                                <option value="2">Low</option>
                                <option value="3">Average</option>
                                <option value="4">High</option>
                                <option value="5">Very High</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Going Out (1-5)</label>
                            <select name="goout" required>
                                <option value="1">Very Low</option>
                                <option value="2">Low</option>
                                <option value="3">Average</option>
                                <option value="4">High</option>
                                <option value="5">Very High</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Health Status (1-5)</label>
                            <select name="health" required>
                                <option value="1">Very Bad</option>
                                <option value="2">Bad</option>
                                <option value="3">Average</option>
                                <option value="4">Good</option>
                                <option value="5">Very Good</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>School Absences</label>
                            <input type="number" name="absences" min="0" max="93" value="0" required>
                        </div>
                        <div class="form-group">
                            <label>Mother's Job</label>
                            <select name="mother_job" required>
                                <option value="at_home">At Home</option>
                                <option value="health">Healthcare</option>
                                <option value="other">Other</option>
                                <option value="services">Services</option>
                                <option value="teacher">Teacher</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Father's Job</label>
                            <select name="father_job" required>
                                <option value="at_home">At Home</option>
                                <option value="health">Healthcare</option>
                                <option value="other">Other</option>
                                <option value="services">Services</option>
                                <option value="teacher">Teacher</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Guardian</label>
                            <select name="guardian" required>
                                <option value="father">Father</option>
                                <option value="mother">Mother</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">Get Prediction</button>
                </form>
            </div>
            
            <div id="results" style="display: none;">
                <div class="card">
                    <h2 class="section-title">Prediction Results</h2>
                    <div id="prediction-content"></div>
                </div>
            </div>
            
        {% elif page == 'admin' %}
            <div class="card">
                <h2 class="section-title">Dataset Statistics</h2>
                <div class="stats-grid" id="datasetStats">
                    <div class="loading">Loading statistics...</div>
                </div>
            </div>
            
            <div class="card">
                <h2 class="section-title">Model Retraining</h2>
                <form id="retrainForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Number of Trees: <span id="n_estimators_val">100</span></label>
                            <input type="range" name="n_estimators" min="10" max="500" step="10" value="100" 
                                   onchange="document.getElementById('n_estimators_val').textContent = this.value">
                        </div>
                        <div class="form-group">
                            <label>Max Depth: <span id="max_depth_val">10</span></label>
                            <input type="range" name="max_depth" min="3" max="50" step="1" value="10"
                                   onchange="document.getElementById('max_depth_val').textContent = this.value">
                        </div>
                        <div class="form-group">
                            <label>Min Samples Split: <span id="min_samples_split_val">5</span></label>
                            <input type="range" name="min_samples_split" min="2" max="20" step="1" value="5"
                                   onchange="document.getElementById('min_samples_split_val').textContent = this.value">
                        </div>
                        <div class="form-group">
                            <label>Min Samples Leaf: <span id="min_samples_leaf_val">2</span></label>
                            <input type="range" name="min_samples_leaf" min="1" max="10" step="1" value="2"
                                   onchange="document.getElementById('min_samples_leaf_val').textContent = this.value">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-danger">Retrain Models</button>
                </form>
            </div>
            
            <div class="card">
                <h2 class="section-title">Current Model Information</h2>
                <div id="modelInfo">
                    <div class="loading">Loading model information...</div>
                </div>
            </div>
        {% endif %}
    </main>
    
    <script>
        // Prediction form handling
        document.addEventListener('DOMContentLoaded', function() {
            const predictionForm = document.getElementById('predictionForm');
            const retrainForm = document.getElementById('retrainForm');
            
            if (predictionForm) {
                predictionForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(predictionForm);
                    const data = {};
                    
                    // Convert form data to API format
                    for (let [key, value] of formData.entries()) {
                        if (['sex', 'age', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'traveltime', 
                             'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'higher', 
                             'internet', 'romantic', 'famrel', 'freetime', 'goout', 'health', 
                             'absences'].includes(key)) {
                            data[key] = parseInt(value);
                        }
                    }
                    
                    // Convert job and guardian info to one-hot encoding
                    const motherJob = formData.get('mother_job');
                    const fatherJob = formData.get('father_job');
                    const guardian = formData.get('guardian');
                    
                    data.Mjob_at_home = motherJob === 'at_home' ? 1 : 0;
                    data.Mjob_health = motherJob === 'health' ? 1 : 0;
                    data.Mjob_other = motherJob === 'other' ? 1 : 0;
                    data.Mjob_services = motherJob === 'services' ? 1 : 0;
                    data.Mjob_teacher = motherJob === 'teacher' ? 1 : 0;
                    
                    data.Fjob_at_home = fatherJob === 'at_home' ? 1 : 0;
                    data.Fjob_health = fatherJob === 'health' ? 1 : 0;
                    data.Fjob_other = fatherJob === 'other' ? 1 : 0;
                    data.Fjob_services = fatherJob === 'services' ? 1 : 0;
                    data.Fjob_teacher = fatherJob === 'teacher' ? 1 : 0;
                    
                    data.guardian_father = guardian === 'father' ? 1 : 0;
                    data.guardian_mother = guardian === 'mother' ? 1 : 0;
                    data.guardian_other = guardian === 'other' ? 1 : 0;
                    
                    try {
                        const response = await fetch('/api/predict', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            displayResults(result);
                        } else {
                            showError(result.error || 'Prediction failed');
                        }
                    } catch (error) {
                        showError('Network error occurred');
                    }
                });
            }
            
            if (retrainForm) {
                // Load admin data
                loadDatasetStats();
                loadModelInfo();
                
                retrainForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(retrainForm);
                    const data = {};
                    
                    for (let [key, value] of formData.entries()) {
                        data[key] = parseInt(value);
                    }
                    
                    try {
                        const response = await fetch('/api/admin/retrain', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            showSuccess('Models retrained successfully! R² Score: ' + result.performance.regression_r2.toFixed(4) + ', Accuracy: ' + result.performance.classification_accuracy.toFixed(4));
                            loadModelInfo();
                        } else {
                            showError(result.error || 'Retraining failed');
                        }
                    } catch (error) {
                        showError('Network error occurred');
                    }
                });
            }
        });
        
        function displayResults(result) {
            const resultsDiv = document.getElementById('results');
            const contentDiv = document.getElementById('prediction-content');
            
            const gradeClass = result.pass_fail === 'pass' ? 'pass' : 'fail';
            
            contentDiv.innerHTML = `
                <div class="result-card">
                    <h3>Predicted Grade</h3>
                    <div class="grade-display ${gradeClass}">${result.predicted_grade}/20</div>
                    <p><strong>Status:</strong> <span class="${gradeClass}">${result.pass_fail.toUpperCase()}</span></p>
                    <p><strong>Confidence:</strong> ${result.confidence.toUpperCase()}</p>
                    <p><strong>Pass Probability:</strong> ${(result.probability_pass * 100).toFixed(1)}%</p>
                    <p><strong>Fail Probability:</strong> ${(result.probability_fail * 100).toFixed(1)}%</p>
                </div>
                <div class="result-card">
                    <h3>Interpretation</h3>
                    <p>${result.predicted_grade >= 10 ? 
                        '✅ The student is predicted to <strong>pass</strong> with a grade of ' + result.predicted_grade.toFixed(1) + '/20.' :
                        '❌ The student is predicted to <strong>fail</strong> with a grade of ' + result.predicted_grade.toFixed(1) + '/20.'
                    }</p>
                </div>
            `;
            
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function loadDatasetStats() {
            try {
                const response = await fetch('/api/admin/dataset/stats');
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('datasetStats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${data.total_samples}</div>
                            <div class="stat-label">Total Samples</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.total_features}</div>
                            <div class="stat-label">Features</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.target_stats.mean_grade}</div>
                            <div class="stat-label">Mean Grade</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.target_stats.pass_rate}%</div>
                            <div class="stat-label">Pass Rate</div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading dataset stats:', error);
            }
        }
        
        async function loadModelInfo() {
            try {
                const response = await fetch('/api/model/info');
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('modelInfo').innerHTML = `
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                            <div>
                                <h3>Regression Model</h3>
                                <p><strong>Type:</strong> ${data.regression_model.type}</p>
                                <p><strong>Trees:</strong> ${data.regression_model.n_estimators}</p>
                                <p><strong>Max Depth:</strong> ${data.regression_model.max_depth}</p>
                                <h4>Top Features:</h4>
                                <ul>
                                    ${data.regression_model.feature_importance.slice(0, 5).map(([feature, importance]) => 
                                        `<li>${feature}: ${(importance * 100).toFixed(1)}%</li>`
                                    ).join('')}
                                </ul>
                            </div>
                            <div>
                                <h3>Classification Model</h3>
                                <p><strong>Type:</strong> ${data.classification_model.type}</p>
                                <p><strong>Trees:</strong> ${data.classification_model.n_estimators}</p>
                                <p><strong>Max Depth:</strong> ${data.classification_model.max_depth}</p>
                                <h4>Top Features:</h4>
                                <ul>
                                    ${data.classification_model.feature_importance.slice(0, 5).map(([feature, importance]) => 
                                        `<li>${feature}: ${(importance * 100).toFixed(1)}%</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading model info:', error);
            }
        }
        
        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = message;
            document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.container').firstChild);
            setTimeout(() => errorDiv.remove(), 5000);
        }
        
        function showSuccess(message) {
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.innerHTML = message;
            document.querySelector('.container').insertBefore(successDiv, document.querySelector('.container').firstChild);
            setTimeout(() => successDiv.remove(), 10000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main prediction page"""
    return render_template_string(main_template, page='predict')

@app.route('/admin')
def admin():
    """Admin panel page"""
    return render_template_string(main_template, page='admin')

# API Endpoints (keeping the same ones from app.py)
def prepare_input_for_prediction(student_data):
    """Prepare student data for model prediction"""
    try:
        # Create DataFrame with correct column order
        df = pd.DataFrame([student_data], columns=feature_columns)
        
        # Scale the data
        X_scaled = scaler.transform(df)
        
        return X_scaled
    except Exception as e:
        raise Exception(f"Error preparing input data: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': regression_model is not None and classification_model is not None
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions for a student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = feature_columns
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400
        
        # Prepare data for prediction
        X_scaled = prepare_input_for_prediction(data)
        
        # Make predictions
        predicted_grade = float(regression_model.predict(X_scaled)[0])
        predicted_class = int(classification_model.predict(X_scaled)[0])
        predicted_prob = classification_model.predict_proba(X_scaled)[0].tolist()
        
        # Prepare response
        result = {
            'predicted_grade': round(predicted_grade, 2),
            'pass_fail': 'pass' if predicted_class == 1 else 'fail',
            'probability_fail': round(predicted_prob[0], 3),
            'probability_pass': round(predicted_prob[1], 3),
            'confidence': 'high' if max(predicted_prob) > 0.7 else 'moderate' if max(predicted_prob) > 0.5 else 'low'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get information about current models"""
    try:
        if not regression_model or not classification_model:
            return jsonify({'error': 'Models not loaded'}), 500
        
        # Get feature importance
        reg_importance = list(zip(feature_columns, regression_model.feature_importances_))
        reg_importance.sort(key=lambda x: x[1], reverse=True)
        
        cls_importance = list(zip(feature_columns, classification_model.feature_importances_))
        cls_importance.sort(key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'regression_model': {
                'type': 'RandomForestRegressor',
                'n_estimators': regression_model.n_estimators,
                'max_depth': regression_model.max_depth,
                'feature_importance': reg_importance[:10]
            },
            'classification_model': {
                'type': 'RandomForestClassifier',
                'n_estimators': classification_model.n_estimators,
                'max_depth': classification_model.max_depth,
                'feature_importance': cls_importance[:10]
            },
            'feature_columns': feature_columns
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/retrain', methods=['POST'])
def retrain_models():
    """Retrain models with new parameters (Admin only)"""
    try:
        global regression_model, classification_model
        
        data = request.get_json()
        
        # Get parameters with defaults
        n_estimators = data.get('n_estimators', 100)
        max_depth = data.get('max_depth', 10)
        min_samples_split = data.get('min_samples_split', 5)
        min_samples_leaf = data.get('min_samples_leaf', 2)
        
        # Validate parameters
        if not (10 <= n_estimators <= 500):
            return jsonify({'error': 'n_estimators must be between 10 and 500'}), 400
        
        if not (3 <= max_depth <= 50):
            return jsonify({'error': 'max_depth must be between 3 and 50'}), 400
        
        # Prepare training data
        X = training_data[feature_columns]
        y_regression = training_data['G3']
        y_classification = (training_data['G3'] >= 10).astype(int)
        
        # Scale features
        X_scaled = scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=feature_columns)
        
        # Split data
        X_train, X_test, y_reg_train, y_reg_test = train_test_split(
            X_scaled, y_regression, test_size=0.2, random_state=42
        )
        X_train_cls, X_test_cls, y_cls_train, y_cls_test = train_test_split(
            X_scaled, y_classification, test_size=0.2, random_state=42, stratify=y_classification
        )
        
        # Train regression model
        regression_model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42,
            n_jobs=-1
        )
        regression_model.fit(X_train, y_reg_train)
        
        # Train classification model
        classification_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        classification_model.fit(X_train_cls, y_cls_train)
        
        # Calculate performance metrics
        reg_score = regression_model.score(X_test, y_reg_test)
        cls_score = classification_model.score(X_test_cls, y_cls_test)
        
        # Save new models
        with open('regression_model.pkl', 'wb') as f:
            pickle.dump(regression_model, f)
        
        with open('classification_model.pkl', 'wb') as f:
            pickle.dump(classification_model, f)
        
        return jsonify({
            'message': 'Models retrained successfully',
            'parameters': {
                'n_estimators': n_estimators,
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf
            },
            'performance': {
                'regression_r2': round(reg_score, 4),
                'classification_accuracy': round(cls_score, 4)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/dataset/stats', methods=['GET'])
def dataset_stats():
    """Get dataset statistics for admin dashboard"""
    try:
        if training_data is None:
            return jsonify({'error': 'Training data not loaded'}), 500
        
        stats = {
            'total_samples': len(training_data),
            'total_features': len(feature_columns),
            'target_stats': {
                'mean_grade': round(training_data['G3'].mean(), 2),
                'std_grade': round(training_data['G3'].std(), 2),
                'min_grade': int(training_data['G3'].min()),
                'max_grade': int(training_data['G3'].max()),
                'pass_rate': round((training_data['G3'] >= 10).sum() / len(training_data) * 100, 1)
            },
            'feature_stats': {
                'numerical_features': len(training_data.select_dtypes(include=[np.number]).columns) - 1,
                'categorical_features': len(training_data.select_dtypes(exclude=[np.number]).columns)
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize models on startup
if __name__ == '__main__':
    print("Loading models...")
    if load_models():
        print("Models loaded successfully!")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to load models. Please train models first.")