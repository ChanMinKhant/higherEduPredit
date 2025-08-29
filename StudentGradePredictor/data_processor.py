"""
Data processing module for student math performance data
Handles loading, cleaning, and feature preparation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataProcessor:
    """Class to handle data loading and preprocessing"""
    
    def __init__(self, csv_path):
        """Initialize with path to CSV file"""
        self.csv_path = csv_path
        self.df = None
        self.scaler = StandardScaler()
    
    def load_data(self):
        """Load the CSV data and perform basic validation"""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"Data shape: {self.df.shape}")
            
            # Display basic info about the data
            print("\nDataset Info:")
            print(f"- Total samples: {len(self.df)}")
            print(f"- Total features: {len(self.df.columns)}")
            
            # Check for missing values
            missing_values = self.df.isnull().sum().sum()
            print(f"- Missing values: {missing_values}")
            
            # Display G3 statistics
            if 'G3' in self.df.columns:
                print(f"\nG3 (Final Grade) Statistics:")
                print(f"- Mean: {self.df['G3'].mean():.2f}")
                print(f"- Std: {self.df['G3'].std():.2f}")
                print(f"- Min: {self.df['G3'].min()}")
                print(f"- Max: {self.df['G3'].max()}")
                print(f"- Students with G3 >= 10: {(self.df['G3'] >= 10).sum()} ({(self.df['G3'] >= 10).sum() / len(self.df) * 100:.1f}%)")
            
            return self.df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find the CSV file at {self.csv_path}")
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def prepare_features_and_targets(self):
        """Prepare features (X) and targets (y) for both regression and classification"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Check if G3 column exists
        if 'G3' not in self.df.columns:
            raise ValueError("G3 column not found in the dataset")
        
        # Prepare features (X) - all columns except G3
        feature_columns = [col for col in self.df.columns if col != 'G3']
        X = self.df[feature_columns].copy()
        
        # Handle any potential missing values in features
        if X.isnull().sum().sum() > 0:
            print("Warning: Found missing values in features, filling with median/mode")
            # Fill numeric columns with median
            numeric_columns = X.select_dtypes(include=[np.number]).columns
            X[numeric_columns] = X[numeric_columns].fillna(X[numeric_columns].median())
            
            # Fill categorical columns with mode
            categorical_columns = X.select_dtypes(exclude=[np.number]).columns
            for col in categorical_columns:
                X[col] = X[col].fillna(X[col].mode()[0] if not X[col].mode().empty else 'Unknown')
        
        # Ensure all features are numeric (they should be based on the data structure)
        X = X.astype(float)
        
        # Prepare regression target (G3 as continuous variable)
        y_regression = self.df['G3'].copy()
        
        # Prepare classification target (G3 >= 10 as binary: 1 for pass, 0 for fail)
        y_classification = (self.df['G3'] >= 10).astype(int)
        
        # Scale features for better model performance
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        print(f"\nFeature scaling applied.")
        print(f"Features shape: {X_scaled.shape}")
        print(f"Available features: {list(X_scaled.columns)}")
        
        return X_scaled, y_regression, y_classification
