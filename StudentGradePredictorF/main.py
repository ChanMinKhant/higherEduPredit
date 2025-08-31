#!/usr/bin/env python3
"""
Console-based Machine Learning Application for Student Math Performance
Trains both regression and classification models on student data
"""

import os
import pandas as pd
from data_processor import DataProcessor
from models import ModelTrainer

def main():
    """Main function to run the machine learning pipeline"""
    
    # File path for the CSV data
    csv_file_path = "attached_assets/cleaned-por-data-withG12.csv"
    
    print("=" * 60)
    print("Student Math Performance - ML Model Training")
    print("=" * 60)
    
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return
    
    try:
        # Initialize data processor
        print("Loading and processing data...")
        data_processor = DataProcessor(csv_file_path)
        
        # Load and prepare data
        df = data_processor.load_data()
        print(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Prepare features and targets
        X, y_regression, y_classification = data_processor.prepare_features_and_targets()
        print(f"Features prepared: {X.shape[1]} features")
        print(f"Regression target (G3): {len(y_regression)} samples")
        print(f"Classification target (Pass/Fail): {len(y_classification)} samples")
        print(f"Pass rate: {(y_classification.sum() / len(y_classification) * 100):.1f}%")
        
        # Initialize model trainer
        model_trainer = ModelTrainer()
        
        print("\n" + "=" * 60)
        print("Training Regression Model (G3 Prediction)")
        print("=" * 60)
        
        # Train regression model
        regression_results = model_trainer.train_regression_model(X, y_regression)
        
        print("\n" + "=" * 60)
        print("Training Classification Model (Pass/Fail Prediction)")
        print("=" * 60)
        
        # Train classification model
        classification_results = model_trainer.train_classification_model(X, y_classification)
        
        print("\n" + "=" * 60)
        print("Model Training Complete!")
        print("=" * 60)
        print("Models saved successfully:")
        print("- regression_model.pkl (G3 prediction)")
        print("- classification_model.pkl (Pass/Fail prediction)")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
