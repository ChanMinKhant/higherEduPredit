# Overview

This is a machine learning application designed to predict student math performance using student academic and demographic data. The system trains both regression models (to predict exact final grades) and classification models (to predict pass/fail outcomes) using Random Forest algorithms. The application processes student data from a CSV file and provides comprehensive model evaluation metrics.

## Recent Changes (August 29, 2025)
- Successfully trained and saved both regression and classification models using Random Forest algorithms
- Regression model: Predicts exact G3 grades (continuous values) with R² score of 0.264 on test data
- Classification model: Predicts pass/fail outcomes (G3 >= 10) with 68.3% accuracy on test data
- Models saved as pickle files: regression_model.pkl and classification_model.pkl
- Console application displays comprehensive performance metrics and feature importance rankings

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Data Processing Pipeline
The system uses a modular architecture with separation of concerns:
- **DataProcessor class**: Handles CSV data loading, validation, and preprocessing
- **ModelTrainer class**: Manages model training and evaluation for both regression and classification tasks
- **Main execution script**: Orchestrates the entire pipeline from data loading to model training

## Machine Learning Framework
- **Primary Algorithm**: Random Forest (both regressor and classifier variants)
- **Model Types**: Dual-purpose system supporting both continuous grade prediction and binary pass/fail classification
- **Data Splitting**: 80/20 train-test split with stratification for classification tasks
- **Feature Scaling**: StandardScaler for numerical feature normalization

## Data Processing Strategy
- **Validation Layer**: File existence checking, empty data detection, and basic data integrity validation
- **Statistical Analysis**: Automatic generation of descriptive statistics for target variables
- **Missing Value Handling**: Built-in detection and reporting of missing data points
- **Feature Engineering**: Automatic preparation of features and multiple target variables from raw data

## Model Training Architecture
- **Cross-validation**: Built-in support for model performance validation
- **Hyperparameter Configuration**: Pre-configured Random Forest parameters optimized for student performance data
- **Evaluation Metrics**: Comprehensive metric calculation including RMSE, MAE, R², accuracy, precision, recall, and F1-score
- **Model Persistence**: Pickle-based model serialization for future predictions

# External Dependencies

## Core ML Libraries
- **scikit-learn**: Primary machine learning framework for models, preprocessing, and evaluation metrics
- **pandas**: Data manipulation and CSV file processing
- **numpy**: Numerical computations and array operations

## Data Requirements
- **Input Format**: CSV file containing student performance data
- **Required Columns**: Expects 'G3' column for final grade target variable
- **File Location**: Configured to read from 'attached_assets/cleaned-mat-data_1756443115411.csv'

## Python Environment
- **Python 3.x**: Required for modern syntax and library compatibility
- **Standard Library**: os module for file system operations
- **Warning Suppression**: Configured to suppress sklearn warnings for cleaner output