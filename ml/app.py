#!/usr/bin/env python3
"""
Flask API Backend for Student Math Performance Prediction
Provides REST endpoints for predictions and admin model management
"""

import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import warnings 
import json
import requests
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173"
        ]
    }
})
# Setup
# Global variables for models and data
regression_model = None
classification_model = None
scaler = None
feature_columns = None
feature_columns_higher = None
training_data = None

def load_models():
    """Load trained models and setup data"""
    global regression_model, classification_model, scaler, feature_columns, feature_columns_higher, training_data

    try:
        # Load models
        with open('regression_model.pkl', 'rb') as f:
            regression_model = pickle.load(f)
        
        with open('classification_model.pkl', 'rb') as f:
            classification_model = pickle.load(f)
        
        # Load training data for scaler setup
        csv_file_path = "attached_assets/cleaned-por-data-withG12.csv"
        training_data = pd.read_csv(csv_file_path)
        
        # Setup feature columns and scaler
        feature_columns = [col for col in training_data.columns if col != 'G3']
        X_original = training_data[feature_columns]

        feature_columns_higher = training_data.columns.tolist()
        scaler = StandardScaler()
        scaler.fit(X_original)
        
        return True
        
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        return False

def prepare_input_for_prediction(student_data):
    """Prepare student data for model prediction"""
    try:
        # Create DataFrame with correct column order
        df = pd.DataFrame([student_data], columns=feature_columns)
        
        # Scale the data
        X_scaled = scaler.transform(df)
        
        return X_scaled
    except Exception as e:
        print(f"Error preparing input data: {str(e)}")
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
    # print(json.dumps(request.get_json(), indent=2, ensure_ascii=False))
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = feature_columns
        missing_fields = [field for field in required_fields if field not in data]
        print(missing_fields)
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400
        print('abc')
        # Prepare data for prediction
        X_scaled = prepare_input_for_prediction(data)
        
        # Make predictions
        predicted_grade = float(regression_model.predict(X_scaled)[0])
        predicted_class = int(classification_model.predict(X_scaled)[0])
        predicted_prob = classification_model.predict_proba(X_scaled)[0].tolist()
        data['G3'] = round(predicted_grade, 2)
        # reorder columns
        ordered_data = {col: data[col] for col in feature_columns_higher if col in data}
        print(json.dumps(ordered_data, indent=2, ensure_ascii=False))
        with open('./StudentUplift/student_education_model.pkl', 'rb') as f:
            higher_model = pickle.load(f)

        # Load metrics (optional)
        with open('./StudentUplift/model_metrics.pkl', 'rb') as f:
            higher_metrics = pickle.load(f)

        higher_X_new = pd.DataFrame([ordered_data])
        higher_predictions = higher_model.predict(higher_X_new)
        higher_metrics = higher_model.predict_proba(higher_X_new)
        print("Higher Predictions:", higher_predictions)
        print("Higher Probabilities:", higher_metrics)
        threadhole = 0.65
        higher_predictions = [1 if prob[1] > threadhole else 0 for prob in higher_metrics]
        print("Higher Predictions:", higher_predictions)    
        result = {
            'predicted_grade': round(predicted_grade, 2),
            'pass_fail': 'pass' if predicted_class == 1 else 'fail',
            'probability_fail': round(predicted_prob[0], 3),
            'probability_pass': round(predicted_prob[1], 3),
            'confidence': 'high' if max(predicted_prob) > 0.7 else 'moderate' if max(predicted_prob) > 0.5 else 'low',
            'higher_education': 'yes' if higher_predictions[0] == 1 else 'no',
            'higher_education_yes': round(higher_metrics[0][1] * 100, 3),
            'higher_education_no': round(higher_metrics[0][0] * 100, 3)
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
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
        difficulty = data.get('difficulty', 0.5)  # Not used in current logic
        basedScore = data.get('basedScore', 20)  # Not used in current logic
        
        # Validate parameters
        if not (10 <= n_estimators <= 500):
            return jsonify({'error': 'n_estimators must be between 10 and 500'}), 400
        
        if not (3 <= max_depth <= 50):
            return jsonify({'error': 'max_depth must be between 3 and 50'}), 400
        # if difficulty is 0.5 passScored would be 10
        passScored = basedScore * difficulty

        print("passScored:", passScored, "difficulty:", difficulty, "basedScore:", basedScore)
        # Prepare training data
        X = training_data[feature_columns]
        X['G1'] = training_data['G1'] * (basedScore / 20)
        X['G2'] = training_data['G2'] * (basedScore / 20)
        print(X[['G1', 'G2']].head(5))
        Y = training_data['G3'] * (basedScore / 20)
        y_regression = Y * (1 - (difficulty - 0.5))
        y_classification = (Y >= passScored).astype(int)
        print(y_regression.head(5))
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
        
        try:
            response = requests.get('http://localhost:3000/api/config/model-config')
            if response.status_code == 200:
                config_data = response.json()
                print("Config Data:", json.dumps(config_data, indent=2, ensure_ascii=False))
            else:
                print(f"Failed to fetch model config: {response.status_code}")
                return jsonify({'error': 'Failed to fetch model config'}), 500
        except Exception as e:
            print(f"Error fetching model config: {str(e)}")
            return jsonify({'error': 'Error fetching model config'}), 500
        basedScore = config_data["config"].get('basedScore', 20)
        difficulty = config_data["config"].get('difficulty', 0.5)

        stats = {
            'total_samples': len(training_data),
            'total_features': len(feature_columns),
            'target_stats': {
                'mean_grade': round(training_data['G3'].mean(), 2) * (basedScore / 20),
                'std_grade': round(training_data['G3'].std(), 2) * (basedScore / 20),
                'min_grade': int(training_data['G3'].min()) * (basedScore / 20),
                'max_grade': int(training_data['G3'].max()) * (basedScore / 20),
                'pass_rate': round((( (training_data['G3'] * (basedScore / 20)) >= (basedScore * difficulty) ).sum() / len(training_data)) * 100, 1)
                },
            'feature_stats': {
                'numerical_features': len(training_data.select_dtypes(include=[np.number]).columns) - 1,
                'categorical_features': len(training_data.select_dtypes(exclude=[np.number]).columns)
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error fetching dataset stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/form/structure', methods=['GET'])
def form_structure():
    """Get form structure for frontend"""
    # fetch data from localhost:3000/api/ml/model-config
    try:
        response = requests.get('http://localhost:3000/api/config/model-config')
        if response.status_code == 200:
            config_data = response.json()
            print("Config Data:", json.dumps(config_data, indent=2, ensure_ascii=False))
        else:
            print(f"Failed to fetch model config: {response.status_code}")
            return jsonify({'error': 'Failed to fetch model config'}), 500
    except Exception as e:
        print(f"Error fetching model config: {str(e)}")
        return jsonify({'error': 'Error fetching model config'}), 500
    form_fields = [
        {'name': 'sex', 'type': 'select', 'label': 'Gender', 'options': [
            {'value': 0, 'label': 'Female'}, {'value': 1, 'label': 'Male'}
        ]},
        {'name': 'age', 'type': 'number', 'label': 'Age', 'min': 15, 'max': 22},
        {'name': 'famsize', 'type': 'select', 'label': 'Family Size', 'options': [
            {'value': 0, 'label': '≤ 3 members'}, {'value': 1, 'label': '> 3 members'}
        ]},
        {'name': 'Pstatus', 'type': 'select', 'label': 'Parent Status', 'options': [
            {'value': 0, 'label': 'Apart'}, {'value': 1, 'label': 'Together'}
        ]},
        {'name': 'Medu', 'type': 'select', 'label': "Mother's Education", 'options': [
            {'value': 0, 'label': 'None'}, {'value': 1, 'label': 'Primary'}, 
            {'value': 2, 'label': 'Secondary'}, {'value': 3, 'label': 'Higher Secondary'}, 
            {'value': 4, 'label': 'Higher Education'}
        ]},
        {'name': 'Fedu', 'type': 'select', 'label': "Father's Education", 'options': [
            {'value': 0, 'label': 'None'}, {'value': 1, 'label': 'Primary'}, 
            {'value': 2, 'label': 'Secondary'}, {'value': 3, 'label': 'Higher Secondary'}, 
            {'value': 4, 'label': 'Higher Education'}
        ]},
        {'name': 'traveltime', 'type': 'select', 'label': 'Travel Time to School', 'options': [
            {'value': 1, 'label': '< 15 min'}, {'value': 2, 'label': '15-30 min'}, 
            {'value': 3, 'label': '30min-1hr'}, {'value': 4, 'label': '> 1hr'}
        ]},
        {'name': 'studytime', 'type': 'select', 'label': 'Weekly Study Time', 'options': [
            {'value': 1, 'label': '< 2 hours'}, {'value': 2, 'label': '2-5 hours'}, 
            {'value': 3, 'label': '5-10 hours'}, {'value': 4, 'label': '> 10 hours'}
        ]},
        {'name': 'failures', 'type': 'select', 'label': 'Past Class Failures', 'options': [
            {'value': 0, 'label': '0 (None)'},
            {'value': 1, 'label': '1'},
            {'value': 2, 'label': '2'},
            {'value': 3, 'label': '3'},
            {'value': 4, 'label': '4 or more'}
        ]},
        # {'name': 'failures', 'type': 'number', 'label': 'Past Class Failures', 'min': 0, 'max': 4},
        {'name': 'schoolsup', 'type': 'select', 'label': 'School Support', 'options': [
            {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        ]},
        {'name': 'famsup', 'type': 'select', 'label': 'Family Support', 'options': [
            {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        ]},
        {'name': 'paid', 'type': 'select', 'label': 'Paid Classes', 'options': [
            {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        ]},
        # {'name': 'higher', 'type': 'select', 'label': 'Wants Higher Education', 'options': [
        #     {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        # ]},
        {'name': 'internet', 'type': 'select', 'label': 'Internet Access', 'options': [
            {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        ]},
        {'name': 'romantic', 'type': 'select', 'label': 'Romantic Relationship', 'options': [
            {'value': 0, 'label': 'No'}, {'value': 1, 'label': 'Yes'}
        ]},
        {'name': 'famrel', 'type': 'select', 'label': 'Family Relationships', 'options': [
            {'value': 1, 'label': 'Very Bad'}, {'value': 2, 'label': 'Bad'}, 
            {'value': 3, 'label': 'Average'}, {'value': 4, 'label': 'Good'}, {'value': 5, 'label': 'Excellent'}
        ]},
        {'name': 'freetime', 'type': 'select', 'label': 'Free Time', 'options': [
            {'value': 1, 'label': 'Very Low'}, {'value': 2, 'label': 'Low'}, 
            {'value': 3, 'label': 'Average'}, {'value': 4, 'label': 'High'}, {'value': 5, 'label': 'Very High'}
        ]},
        {'name': 'goout', 'type': 'select', 'label': 'Going Out', 'options': [
            {'value': 1, 'label': 'Very Low'}, {'value': 2, 'label': 'Low'}, 
            {'value': 3, 'label': 'Average'}, {'value': 4, 'label': 'High'}, {'value': 5, 'label': 'Very High'}
        ]},
        {'name': 'health', 'type': 'select', 'label': 'Health Status', 'options': [
            {'value': 1, 'label': 'Very Bad'}, {'value': 2, 'label': 'Bad'}, 
            {'value': 3, 'label': 'Average'}, {'value': 4, 'label': 'Good'}, {'value': 5, 'label': 'Very Good'}
        ]},
        {'name': 'absences', 'type': 'number', 'label': 'School Absences (0 - 93)', 'min': 0, 'max': 93},
    ]
    
    # Add job fields
    job_options = [
        {'value': 'at_home', 'label': 'At Home'},
        {'value': 'health', 'label': 'Healthcare'},
        {'value': 'other', 'label': 'Other'},
        {'value': 'services', 'label': 'Services'},
        {'value': 'teacher', 'label': 'Teacher'}
    ]
    
    form_fields.extend([
        {'name': 'mother_job', 'type': 'select', 'label': "Mother's Job", 'options': job_options},
        {'name': 'father_job', 'type': 'select', 'label': "Father's Job", 'options': job_options},
        {'name': 'guardian', 'type': 'select', 'label': 'Guardian', 'options': [
            {'value': 'father', 'label': 'Father'},
            {'value': 'mother', 'label': 'Mother'},
            {'value': 'other', 'label': 'Other'}
        ]}
    ])

    if(True):
        # For testing, add G1 and G2 fields
        form_fields.extend([
            {'name': 'G1', 'type': 'number', 'label': f'First Period Grade(0-{config_data["config"].get("basedScore", 20)})', 'min': 0, 'max': config_data["config"].get('basedScore', 20)},
            {'name': 'G2', 'type': 'number', 'label': f'Second Period Grade(0-{config_data["config"].get("basedScore", 20)})', 'min': 0, 'max': config_data["config"].get('basedScore', 20)}
        ])

    return jsonify({'fields': form_fields})

# Initialize models on startup
if __name__ == '__main__':
    print("Loading models...")
    if load_models():
        print("Models loaded successfully!")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to load models. Please train models first.")