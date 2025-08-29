#!/usr/bin/env python3
"""
Interactive prediction console for student math performance
Load trained models and make predictions on new student data
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def load_models():
    """Load the trained models"""
    try:
        with open('regression_model.pkl', 'rb') as f:
            regression_model = pickle.load(f)
        
        with open('classification_model.pkl', 'rb') as f:
            classification_model = pickle.load(f)
        
        return regression_model, classification_model
    except FileNotFoundError as e:
        print(f"Error: Could not find model files. Please train models first by running main.py")
        return None, None

def get_user_input():
    """Get student data from user input"""
    print("\n" + "="*60)
    print("Enter Student Information for Prediction")
    print("="*60)
    
    student_data = {}
    
    # Basic demographic info
    print("\n--- Basic Information ---")
    student_data['sex'] = int(input("Sex (0=female, 1=male): "))
    student_data['age'] = int(input("Age (15-22): "))
    student_data['famsize'] = int(input("Family size (0=<=3, 1=>3): "))
    student_data['Pstatus'] = int(input("Parent cohabitation status (0=apart, 1=together): "))
    
    # Education info
    print("\n--- Education Background ---")
    student_data['Medu'] = int(input("Mother's education (0-4, 0=none, 4=higher): "))
    student_data['Fedu'] = int(input("Father's education (0-4, 0=none, 4=higher): "))
    student_data['traveltime'] = int(input("Travel time to school (1=<15min, 2=15-30min, 3=30min-1hr, 4=>1hr): "))
    student_data['studytime'] = int(input("Weekly study time (1=<2hrs, 2=2-5hrs, 3=5-10hrs, 4=>10hrs): "))
    student_data['failures'] = int(input("Number of past class failures (0-4): "))
    
    # Support and activities
    print("\n--- Support and Activities ---")
    student_data['schoolsup'] = int(input("Extra educational support (0=no, 1=yes): "))
    student_data['famsup'] = int(input("Family educational support (0=no, 1=yes): "))
    student_data['paid'] = int(input("Extra paid classes (0=no, 1=yes): "))
    student_data['higher'] = int(input("Wants to take higher education (0=no, 1=yes): "))
    student_data['internet'] = int(input("Internet access at home (0=no, 1=yes): "))
    student_data['romantic'] = int(input("In a romantic relationship (0=no, 1=yes): "))
    
    # Personal and social
    print("\n--- Personal and Social ---")
    student_data['famrel'] = int(input("Quality of family relationships (1-5, 1=very bad, 5=excellent): "))
    student_data['freetime'] = int(input("Free time after school (1-5, 1=very low, 5=very high): "))
    student_data['goout'] = int(input("Going out with friends (1-5, 1=very low, 5=very high): "))
    student_data['health'] = int(input("Current health status (1-5, 1=very bad, 5=very good): "))
    student_data['absences'] = int(input("Number of school absences (0-93): "))
    
    # Job information (one-hot encoded)
    print("\n--- Parent Job Information ---")
    print("Mother's job options: at_home, health, other, services, teacher")
    mjob = input("Mother's job: ").lower()
    student_data['Mjob_at_home'] = 1 if mjob == 'at_home' else 0
    student_data['Mjob_health'] = 1 if mjob == 'health' else 0
    student_data['Mjob_other'] = 1 if mjob == 'other' else 0
    student_data['Mjob_services'] = 1 if mjob == 'services' else 0
    student_data['Mjob_teacher'] = 1 if mjob == 'teacher' else 0
    
    print("Father's job options: at_home, health, other, services, teacher")
    fjob = input("Father's job: ").lower()
    student_data['Fjob_at_home'] = 1 if fjob == 'at_home' else 0
    student_data['Fjob_health'] = 1 if fjob == 'health' else 0
    student_data['Fjob_other'] = 1 if fjob == 'other' else 0
    student_data['Fjob_services'] = 1 if fjob == 'services' else 0
    student_data['Fjob_teacher'] = 1 if fjob == 'teacher' else 0
    
    # Guardian information
    print("\nGuardian options: father, mother, other")
    guardian = input("Guardian: ").lower()
    student_data['guardian_father'] = 1 if guardian == 'father' else 0
    student_data['guardian_mother'] = 1 if guardian == 'mother' else 0
    student_data['guardian_other'] = 1 if guardian == 'other' else 0
    
    return student_data

def prepare_input_data(student_data):
    """Prepare the input data for prediction (same preprocessing as training)"""
    # Create DataFrame with the same column order as training data
    feature_columns = ['sex', 'age', 'famsize', 'Pstatus', 'Medu', 'Fedu', 'traveltime', 
                      'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'higher', 
                      'internet', 'romantic', 'famrel', 'freetime', 'goout', 'health', 
                      'absences', 'Mjob_at_home', 'Mjob_health', 'Mjob_other', 'Mjob_services', 
                      'Mjob_teacher', 'Fjob_at_home', 'Fjob_health', 'Fjob_other', 'Fjob_services', 
                      'Fjob_teacher', 'guardian_father', 'guardian_mother', 'guardian_other']
    
    # Create DataFrame
    df = pd.DataFrame([student_data], columns=feature_columns)
    
    # Load the original scaler used during training
    # Note: In a production system, you'd save the scaler separately
    # For now, we'll create a new one based on the training data
    csv_file_path = "attached_assets/cleaned-mat-data_1756443115411.csv"
    original_data = pd.read_csv(csv_file_path)
    X_original = original_data.drop('G3', axis=1)
    
    scaler = StandardScaler()
    scaler.fit(X_original)
    
    # Scale the input data
    X_scaled = scaler.transform(df)
    
    return X_scaled

def make_predictions(regression_model, classification_model, X_scaled):
    """Make predictions using both models"""
    # Regression prediction (exact grade)
    predicted_grade = regression_model.predict(X_scaled)[0]
    
    # Classification prediction (pass/fail)
    predicted_class = classification_model.predict(X_scaled)[0]
    predicted_prob = classification_model.predict_proba(X_scaled)[0]
    
    return predicted_grade, predicted_class, predicted_prob

def display_results(predicted_grade, predicted_class, predicted_prob):
    """Display the prediction results"""
    print("\n" + "="*60)
    print("PREDICTION RESULTS")
    print("="*60)
    
    print(f"\nPredicted Final Grade (G3): {predicted_grade:.2f}")
    
    if predicted_class == 1:
        result = "PASS"
    else:
        result = "FAIL"
    
    print(f"Pass/Fail Prediction: {result}")
    print(f"Probability of Failing: {predicted_prob[0]:.3f}")
    print(f"Probability of Passing: {predicted_prob[1]:.3f}")
    
    # Additional interpretation
    print(f"\nInterpretation:")
    if predicted_grade >= 10:
        print(f"- The student is predicted to pass with a grade of {predicted_grade:.1f}/20")
    else:
        print(f"- The student is predicted to fail with a grade of {predicted_grade:.1f}/20")
    
    if predicted_prob[1] > 0.7:
        confidence = "high"
    elif predicted_prob[1] > 0.5:
        confidence = "moderate"
    else:
        confidence = "low"
    
    print(f"- Confidence in passing: {confidence} ({predicted_prob[1]:.1%})")

def main():
    """Main function for the prediction console"""
    print("Student Math Performance Prediction Console")
    print("=" * 60)
    
    # Load models
    regression_model, classification_model = load_models()
    if regression_model is None or classification_model is None:
        return
    
    print("Models loaded successfully!")
    
    while True:
        try:
            # Get user input
            student_data = get_user_input()
            
            # Prepare data for prediction
            X_scaled = prepare_input_data(student_data)
            
            # Make predictions
            predicted_grade, predicted_class, predicted_prob = make_predictions(
                regression_model, classification_model, X_scaled
            )
            
            # Display results
            display_results(predicted_grade, predicted_class, predicted_prob)
            
            # Ask if user wants to continue
            print("\n" + "="*60)
            continue_pred = input("Would you like to make another prediction? (y/n): ").lower()
            if continue_pred != 'y' and continue_pred != 'yes':
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except ValueError as e:
            print(f"\nError: Invalid input. Please enter numeric values where required.")
            continue
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            continue
    
    print("Thank you for using the prediction console!")

if __name__ == "__main__":
    main()