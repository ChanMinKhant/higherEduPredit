import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import json

def create_synthetic_dataset(n_samples=2000):
    """Create a comprehensive synthetic dataset for matriculation exam prediction"""
    np.random.seed(42)
    
    # Generate features
    data = {
        'age': np.random.randint(15, 26, n_samples),
        'gender': np.random.choice(['male', 'female', 'other'], n_samples, p=[0.48, 0.48, 0.04]),
        'grade_average': np.random.normal(75, 12, n_samples),
        'attendance_rate': np.random.normal(88, 8, n_samples),
        'study_hours': np.random.poisson(20, n_samples),
        'family_income': np.random.choice(['low', 'middle', 'high'], n_samples, p=[0.3, 0.5, 0.2]),
        'parental_education': np.random.choice(['primary', 'secondary', 'tertiary', 'postgraduate'], 
                                             n_samples, p=[0.2, 0.4, 0.3, 0.1]),
        'school_type': np.random.choice(['public', 'private', 'charter'], n_samples, p=[0.7, 0.25, 0.05]),
        'extracurricular_hours': np.random.poisson(5, n_samples),
        'tutoring_hours': np.random.poisson(3, n_samples),
        'motivation_score': np.random.randint(1, 11, n_samples),
        'health_status': np.random.choice(['excellent', 'good', 'fair', 'poor'], 
                                        n_samples, p=[0.3, 0.5, 0.15, 0.05]),
        'sleep_hours': np.random.normal(7, 1.2, n_samples)
    }
    
    # Clip values to realistic ranges
    data['grade_average'] = np.clip(data['grade_average'], 0, 100)
    data['attendance_rate'] = np.clip(data['attendance_rate'], 0, 100)
    data['study_hours'] = np.clip(data['study_hours'], 0, 80)
    data['extracurricular_hours'] = np.clip(data['extracurricular_hours'], 0, 30)
    data['tutoring_hours'] = np.clip(data['tutoring_hours'], 0, 20)
    data['sleep_hours'] = np.clip(data['sleep_hours'], 4, 12)
    
    df = pd.DataFrame(data)
    
    # Create target variable based on realistic relationships
    pass_probability = (
        0.3 * (df['grade_average'] / 100) +
        0.2 * (df['attendance_rate'] / 100) +
        0.15 * (df['study_hours'] / 80) +
        0.1 * (df['motivation_score'] / 10) +
        0.05 * (df['tutoring_hours'] / 20) +
        0.05 * (df['sleep_hours'] / 12) +
        0.05 * df['family_income'].map({'low': 0.3, 'middle': 0.6, 'high': 0.9}) +
        0.05 * df['parental_education'].map({'primary': 0.2, 'secondary': 0.5, 'tertiary': 0.8, 'postgraduate': 0.9}) +
        0.05 * df['health_status'].map({'poor': 0.2, 'fair': 0.5, 'good': 0.8, 'excellent': 0.9}) +
        np.random.normal(0, 0.1, n_samples)  # Add some noise
    )
    
    # Convert to binary outcome
    df['pass'] = (pass_probability > 0.6).astype(int)
    
    return df

def encode_categorical_features(df):
    """Encode categorical features for machine learning"""
    df_encoded = df.copy()
    
    # Label encoding for categorical variables
    categorical_columns = ['gender', 'family_income', 'parental_education', 'school_type', 'health_status']
    label_encoders = {}
    
    for col in categorical_columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        label_encoders[col] = le
    
    return df_encoded, label_encoders

def train_models(df):
    """Train multiple machine learning models"""
    
    # Prepare features and target
    X = df.drop(['pass'], axis=1)
    y = df['pass']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features for SVM and Logistic Regression
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42, probability=True, kernel='rbf')
    }
    
    # Train and evaluate models
    results = {}
    
    # Random Forest (doesn't need scaling)
    rf_model = models['Random Forest']
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    results['Random Forest'] = {
        'model': rf_model,
        'accuracy': rf_accuracy,
        'scaler': None
    }
    
    # Logistic Regression (needs scaling)
    lr_model = models['Logistic Regression']
    lr_model.fit(X_train_scaled, y_train)
    lr_pred = lr_model.predict(X_test_scaled)
    lr_accuracy = accuracy_score(y_test, lr_pred)
    results['Logistic Regression'] = {
        'model': lr_model,
        'accuracy': lr_accuracy,
        'scaler': scaler
    }
    
    # SVM (needs scaling)
    svm_model = models['SVM']
    svm_model.fit(X_train_scaled, y_train)
    svm_pred = svm_model.predict(X_test_scaled)
    svm_accuracy = accuracy_score(y_test, svm_pred)
    results['SVM'] = {
        'model': svm_model,
        'accuracy': svm_accuracy,
        'scaler': scaler  # Using same scaler for both scaled models
    }
    
    return results, label_encoders

def save_models(results, label_encoders):
    """Save trained models and encoders"""
    
    # Create models directory if it doesn't exist
    models_dir = 'python/models'
    os.makedirs(models_dir, exist_ok=True)
    
    # Save each model
    for model_name, model_data in results.items():
        model_filename = model_name.lower().replace(' ', '_') + '.joblib'
        model_path = os.path.join(models_dir, model_filename)
        
        # Save model with its scaler if needed
        joblib.dump({
            'model': model_data['model'],
            'scaler': model_data['scaler'],
            'accuracy': model_data['accuracy']
        }, model_path)
        
        print(f"Saved {model_name} to {model_path} (Accuracy: {model_data['accuracy']:.3f})")
    
    # Save label encoders
    encoders_path = os.path.join(models_dir, 'label_encoders.joblib')
    joblib.dump(label_encoders, encoders_path)
    print(f"Saved label encoders to {encoders_path}")
    
    # Save feature names for consistency
    feature_names = ['age', 'gender', 'grade_average', 'attendance_rate', 'study_hours',
                    'family_income', 'parental_education', 'school_type', 'extracurricular_hours',
                    'tutoring_hours', 'motivation_score', 'health_status', 'sleep_hours']
    
    features_path = os.path.join(models_dir, 'feature_names.json')
    with open(features_path, 'w') as f:
        json.dump(feature_names, f)
    print(f"Saved feature names to {features_path}")

def main():
    """Main training pipeline"""
    print("Starting model training pipeline...")
    
    # Create synthetic dataset
    print("Creating synthetic dataset...")
    df = create_synthetic_dataset(2000)
    print(f"Created dataset with {len(df)} samples")
    print(f"Pass rate: {df['pass'].mean():.3f}")
    
    # Encode categorical features
    print("Encoding categorical features...")
    df_encoded, label_encoders = encode_categorical_features(df)
    
    # Train models
    print("Training models...")
    results, label_encoders = train_models(df_encoded)
    
    # Print results
    print("\nModel Performance:")
    for model_name, model_data in results.items():
        print(f"{model_name}: {model_data['accuracy']:.3f}")
    
    # Save models
    print("\nSaving models...")
    save_models(results, label_encoders)
    
    print("Training complete!")

if __name__ == "__main__":
    main()
