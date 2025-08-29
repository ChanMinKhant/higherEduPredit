"""
Machine learning models module for student performance prediction
Includes both regression and classification models
"""

import pickle
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

class ModelTrainer:
    """Class to handle model training and evaluation"""
    
    def __init__(self):
        """Initialize the model trainer"""
        self.regression_model = None
        self.classification_model = None
        self.random_state = 42
    
    def train_regression_model(self, X, y):
        """Train and evaluate a regression model to predict G3"""
        print("Initializing Random Forest Regressor...")
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=None
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Initialize and train the model
        self.regression_model = RandomForestRegressor(
            n_estimators=100,
            random_state=self.random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            n_jobs=-1
        )
        
        print("Training regression model...")
        self.regression_model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = self.regression_model.predict(X_train)
        y_test_pred = self.regression_model.predict(X_test)
        
        # Calculate metrics
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.regression_model, X_train, y_train, cv=5, scoring='r2')
        
        # Display results
        print("\nRegression Model Performance:")
        print("-" * 40)
        print(f"Training MSE: {train_mse:.4f}")
        print(f"Test MSE: {test_mse:.4f}")
        print(f"Training MAE: {train_mae:.4f}")
        print(f"Test MAE: {test_mae:.4f}")
        print(f"Training R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        print(f"Cross-validation R² (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        # Feature importance
        feature_importance = sorted(
            zip(X.columns, self.regression_model.feature_importances_),
            key=lambda x: x[1], reverse=True
        )[:10]
        
        print("\nTop 10 Most Important Features (Regression):")
        print("-" * 40)
        for feature, importance in feature_importance:
            print(f"{feature}: {importance:.4f}")
        
        # Save the model
        model_filename = "regression_model.pkl"
        with open(model_filename, 'wb') as f:
            pickle.dump(self.regression_model, f)
        print(f"\nRegression model saved as: {model_filename}")
        
        return {
            'model': self.regression_model,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'cv_scores': cv_scores,
            'feature_importance': feature_importance
        }
    
    def train_classification_model(self, X, y):
        """Train and evaluate a classification model to predict pass/fail"""
        print("Initializing Random Forest Classifier...")
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        print(f"Training set class distribution:")
        print(f"  - Fail (0): {(y_train == 0).sum()} ({(y_train == 0).sum() / len(y_train) * 100:.1f}%)")
        print(f"  - Pass (1): {(y_train == 1).sum()} ({(y_train == 1).sum() / len(y_train) * 100:.1f}%)")
        
        # Initialize and train the model
        self.classification_model = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            n_jobs=-1
        )
        
        print("Training classification model...")
        self.classification_model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = self.classification_model.predict(X_train)
        y_test_pred = self.classification_model.predict(X_test)
        y_test_pred_proba = self.classification_model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        test_precision = precision_score(y_test, y_test_pred, average='binary')
        test_recall = recall_score(y_test, y_test_pred, average='binary')
        test_f1 = f1_score(y_test, y_test_pred, average='binary')
        
        # Cross-validation score
        cv_scores = cross_val_score(self.classification_model, X_train, y_train, cv=5, scoring='accuracy')
        
        # Display results
        print("\nClassification Model Performance:")
        print("-" * 40)
        print(f"Training Accuracy: {train_accuracy:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Precision: {test_precision:.4f}")
        print(f"Test Recall: {test_recall:.4f}")
        print(f"Test F1-Score: {test_f1:.4f}")
        print(f"Cross-validation Accuracy (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        # Detailed classification report
        print("\nDetailed Classification Report:")
        print("-" * 40)
        target_names = ['Fail', 'Pass']
        print(classification_report(y_test, y_test_pred, target_names=target_names))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_test_pred)
        print("Confusion Matrix:")
        print("    Predicted")
        print("     F   P")
        print(f"F  {cm[0,0]:3d} {cm[0,1]:3d}")
        print(f"P  {cm[1,0]:3d} {cm[1,1]:3d}")
        print("Actual")
        
        # Feature importance
        feature_importance = sorted(
            zip(X.columns, self.classification_model.feature_importances_),
            key=lambda x: x[1], reverse=True
        )[:10]
        
        print("\nTop 10 Most Important Features (Classification):")
        print("-" * 40)
        for feature, importance in feature_importance:
            print(f"{feature}: {importance:.4f}")
        
        # Save the model
        model_filename = "classification_model.pkl"
        with open(model_filename, 'wb') as f:
            pickle.dump(self.classification_model, f)
        print(f"\nClassification model saved as: {model_filename}")
        
        return {
            'model': self.classification_model,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'cv_scores': cv_scores,
            'confusion_matrix': cm,
            'feature_importance': feature_importance
        }
