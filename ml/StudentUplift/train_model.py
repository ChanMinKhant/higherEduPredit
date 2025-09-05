#!/usr/bin/env python3
"""
Student Higher Education Prediction Model Training

This script trains machine learning models to predict student higher education intentions
using the provided student dataset. It preprocesses the data, trains multiple models,
evaluates their performance, and saves the best model as a pickle file.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    classification_report, confusion_matrix
)
from sklearn.feature_selection import SelectKBest, f_classif
import warnings
warnings.filterwarnings('ignore')

class StudentEducationPredictor:
    """
    A class to handle the complete machine learning pipeline for predicting
    student higher education intentions.
    """
    
    def __init__(self, data_path):
        """
        Initialize the predictor with the dataset path.
        
        Args:
            data_path (str): Path to the CSV dataset
        """
        self.data_path = data_path
        self.data = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.best_model = None
        self.best_score = 0
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.models = {}
        
    def load_data(self):
        """Load and perform initial data exploration."""
        print("=" * 60)
        print("STUDENT HIGHER EDUCATION PREDICTION MODEL TRAINING")
        print("=" * 60)
        
        try:
            self.data = pd.read_csv(self.data_path)
            print(f"✓ Dataset loaded successfully!")
            print(f"  - Shape: {self.data.shape}")
            print(f"  - Features: {self.data.shape[1] - 1}")
            print(f"  - Samples: {self.data.shape[0]}")
            
            # Check for missing values
            missing_values = self.data.isnull().sum().sum()
            print(f"  - Missing values: {missing_values}")
            
            # Check target variable distribution
            target_dist = self.data['higher'].value_counts()
            print(f"\n📊 Target Variable Distribution (higher education intention):")
            print(f"  - Want higher education (1): {target_dist.get(1, 0)} ({target_dist.get(1, 0)/len(self.data)*100:.1f}%)")
            print(f"  - Don't want higher education (0): {target_dist.get(0, 0)} ({target_dist.get(0, 0)/len(self.data)*100:.1f}%)")
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Error: Dataset file '{self.data_path}' not found!")
            return False
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            return False
    
    def preprocess_data(self):
        """Preprocess the data for machine learning."""
        print("\n🔧 PREPROCESSING DATA")
        print("-" * 30)
        
        # Separate features and target
        self.X = self.data.drop('higher', axis=1)
        self.y = self.data['higher']
        
        print(f"✓ Features extracted: {self.X.shape[1]} features")
        print(f"✓ Target variable extracted: {len(self.y)} samples")
        
        # Handle any remaining missing values
        if self.X.isnull().sum().sum() > 0:
            print("⚠️  Handling missing values...")
            # Fill numeric columns with median
            numeric_cols = self.X.select_dtypes(include=[np.number]).columns
            self.X[numeric_cols] = self.X[numeric_cols].fillna(self.X[numeric_cols].median())
            
            # Fill categorical columns with mode
            categorical_cols = self.X.select_dtypes(include=['object', 'bool']).columns
            for col in categorical_cols:
                self.X[col] = self.X[col].fillna(self.X[col].mode()[0])
            print("✓ Missing values handled")
        
        # Display feature information
        print(f"\n📋 Feature Summary:")
        print(f"  - Numeric features: {len(self.X.select_dtypes(include=[np.number]).columns)}")
        print(f"  - Boolean features: {len(self.X.select_dtypes(include=['bool']).columns)}")
        print(f"  - Object features: {len(self.X.select_dtypes(include=['object']).columns)}")
        
        # Convert boolean columns to int
        bool_cols = self.X.select_dtypes(include=['bool']).columns
        if len(bool_cols) > 0:
            self.X[bool_cols] = self.X[bool_cols].astype(int)
            print(f"✓ Converted {len(bool_cols)} boolean features to numeric")
        
        # Encode any remaining categorical variables
        categorical_cols = self.X.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            print(f"⚠️  Encoding {len(categorical_cols)} categorical features...")
            le = LabelEncoder()
            for col in categorical_cols:
                self.X[col] = le.fit_transform(self.X[col].astype(str))
            print("✓ Categorical features encoded")
        
        return True
    
    def split_data(self, test_size=0.2, random_state=42):
        """Split data into training and testing sets."""
        print(f"\n📊 SPLITTING DATA")
        print("-" * 20)
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=random_state, 
            stratify=self.y
        )
        
        print(f"✓ Training set: {self.X_train.shape[0]} samples ({(1-test_size)*100:.0f}%)")
        print(f"✓ Testing set: {self.X_test.shape[0]} samples ({test_size*100:.0f}%)")
        print(f"✓ Stratified split maintains class distribution")
        
        return True
    
    def feature_selection(self, k=20):
        """Perform feature selection to identify most important features."""
        print(f"\n🎯 FEATURE SELECTION")
        print("-" * 25)
        
        # Use SelectKBest with f_classif for feature selection
        self.feature_selector = SelectKBest(score_func=f_classif, k=min(k, self.X_train.shape[1]))
        X_train_selected = self.feature_selector.fit_transform(self.X_train, self.y_train)
        
        # Get selected feature names
        feature_mask = self.feature_selector.get_support()
        selected_features = self.X.columns[feature_mask].tolist()
        
        print(f"✓ Selected top {len(selected_features)} features:")
        for i, feature in enumerate(selected_features[:10], 1):
            score = self.feature_selector.scores_[self.X.columns.get_loc(feature)]
            print(f"  {i:2d}. {feature:<15} (score: {score:.2f})")
        
        if len(selected_features) > 10:
            print(f"     ... and {len(selected_features) - 10} more features")
        
        return True
    
    def train_models(self):
        """Train multiple machine learning models."""
        print(f"\n🤖 TRAINING MACHINE LEARNING MODELS")
        print("-" * 40)
        
        # Define models to train
        models_config = {
            'Random Forest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'classifier__n_estimators': [100, 200],
                    'classifier__max_depth': [10, 20, None],
                    'classifier__min_samples_split': [2, 5]
                }
            },
            'Logistic Regression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'classifier__C': [0.1, 1, 10],
                    'classifier__penalty': ['l1', 'l2'],
                    'classifier__solver': ['liblinear']
                }
            },
            'Support Vector Machine': {
                'model': SVC(random_state=42, probability=True),
                'params': {
                    'classifier__C': [0.1, 1, 10],
                    'classifier__kernel': ['rbf', 'linear'],
                    'classifier__gamma': ['scale', 'auto']
                }
            }
        }
        
        best_model_name = None
        
        for model_name, config in models_config.items():
            print(f"\n🔄 Training {model_name}...")
            
            # Create pipeline with preprocessing and model
            pipeline = Pipeline([
                ('feature_selector', self.feature_selector),
                ('scaler', StandardScaler()),
                ('classifier', config['model'])
            ])
            
            # Perform grid search with cross-validation
            grid_search = GridSearchCV(
                pipeline, 
                config['params'], 
                cv=5, 
                scoring='accuracy',
                n_jobs=-1,
                verbose=0
            )
            
            # Fit the model
            grid_search.fit(self.X_train, self.y_train)
            
            # Store the best model
            self.models[model_name] = grid_search.best_estimator_
            
            # Evaluate the model
            cv_scores = cross_val_score(grid_search.best_estimator_, self.X_train, self.y_train, cv=5)
            mean_cv_score = cv_scores.mean()
            
            print(f"  ✓ Best CV Accuracy: {mean_cv_score:.4f} (±{cv_scores.std()*2:.4f})")
            print(f"  ✓ Best Parameters: {grid_search.best_params_}")
            
            # Update best model if this one is better
            if mean_cv_score > self.best_score:
                self.best_score = mean_cv_score
                self.best_model = grid_search.best_estimator_
                best_model_name = model_name
        
        print(f"\n🏆 Best Model: {best_model_name} (CV Accuracy: {self.best_score:.4f})")
        
        return True
    
    def evaluate_model(self):
        """Evaluate the best model on the test set."""
        print(f"\n📈 MODEL EVALUATION")
        print("-" * 25)
        
        # Make predictions
        y_pred = self.best_model.predict(self.X_test)
        y_pred_proba = self.best_model.predict_proba(self.X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        
        print(f"📊 Test Set Performance:")
        print(f"  • Accuracy:  {accuracy:.4f}")
        print(f"  • Precision: {precision:.4f}")
        print(f"  • Recall:    {recall:.4f}")
        print(f"  • F1-Score:  {f1:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print(f"\n📋 Confusion Matrix:")
        print(f"                 Predicted")
        print(f"                 No   Yes")
        print(f"Actual No      {cm[0,0]:4d} {cm[0,1]:4d}")
        print(f"Actual Yes     {cm[1,0]:4d} {cm[1,1]:4d}")
        
        # Feature importance for Random Forest
        if hasattr(self.best_model.named_steps['classifier'], 'feature_importances_'):
            print(f"\n🎯 Top 10 Most Important Features:")
            feature_names = self.X.columns[self.best_model.named_steps['feature_selector'].get_support()]
            importances = self.best_model.named_steps['classifier'].feature_importances_
            
            # Sort features by importance
            feature_importance = list(zip(feature_names, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            for i, (feature, importance) in enumerate(feature_importance[:10], 1):
                print(f"  {i:2d}. {feature:<15} {importance:.4f}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        }
    
    def save_model(self, model_filename='student_education_model.pkl', 
                   metrics_filename='model_metrics.pkl'):
        """Save the trained model and metrics."""
        print(f"\n💾 SAVING MODEL")
        print("-" * 15)
        
        try:
            # Save the complete pipeline
            with open(model_filename, 'wb') as f:
                pickle.dump(self.best_model, f)
            print(f"✓ Model saved as: {model_filename}")
            
            # Save model metrics and metadata
            metrics_data = {
                'model_type': type(self.best_model.named_steps['classifier']).__name__,
                'cv_accuracy': self.best_score,
                'test_metrics': self.evaluate_model(),
                'feature_names': self.X.columns.tolist(),
                'selected_features': self.X.columns[self.best_model.named_steps['feature_selector'].get_support()].tolist(),
                'training_samples': len(self.X_train),
                'test_samples': len(self.X_test)
            }
            
            with open(metrics_filename, 'wb') as f:
                pickle.dump(metrics_data, f)
            print(f"✓ Metrics saved as: {metrics_filename}")
            
            # Display usage instructions
            print(f"\n📖 USAGE INSTRUCTIONS:")
            print(f"-" * 25)
            print(f"To use the trained model in another application:")
            print(f"")
            print(f"```python")
            print(f"import pickle")
            print(f"import pandas as pd")
            print(f"")
            print(f"# Load the model")
            print(f"with open('{model_filename}', 'rb') as f:")
            print(f"    model = pickle.load(f)")
            print(f"")
            print(f"# Load metrics (optional)")
            print(f"with open('{metrics_filename}', 'rb') as f:")
            print(f"    metrics = pickle.load(f)")
            print(f"")
            print(f"# Make predictions")
            print(f"# X_new should be a DataFrame with the same features as training data")
            print(f"predictions = model.predict(X_new)")
            print(f"probabilities = model.predict_proba(X_new)")
            print(f"```")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving model: {str(e)}")
            return False
    
    def run_complete_pipeline(self):
        """Run the complete machine learning pipeline."""
        success = (
            self.load_data() and
            self.preprocess_data() and
            self.split_data() and
            self.feature_selection() and
            self.train_models() and
            self.save_model()
        )
        
        if success:
            print(f"\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
            print(f"=" * 50)
            print(f"The model is ready for use in prediction applications.")
        else:
            print(f"\n❌ TRAINING FAILED!")
            print(f"Please check the error messages above.")
        
        return success

def main():
    """Main function to run the training pipeline."""
    # Default dataset path - can be modified as needed
    dataset_path = "attached_assets/cleaned-por-data-withG12_1756695837826.csv"
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found: {dataset_path}")
        print(f"Please ensure the dataset is in the correct location.")
        return
    
    # Initialize and run the predictor
    predictor = StudentEducationPredictor(dataset_path)
    success = predictor.run_complete_pipeline()
    
    if success:
        print(f"\n🚀 Model training completed successfully!")
        print(f"Files generated:")
        print(f"  - student_education_model.pkl (trained model)")
        print(f"  - model_metrics.pkl (performance metrics)")
    else:
        print(f"\n💥 Model training failed. Please check the errors above.")

if __name__ == "__main__":
    main()
