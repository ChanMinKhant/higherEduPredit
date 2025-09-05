import pickle
import pandas as pd

# Load the model
with open('student_education_model.pkl', 'rb') as f:        
    model = pickle.load(f)

# Load metrics (optional)
with open('model_metrics.pkl', 'rb') as f:
    metrics = pickle.load(f)

# Make predictions
# X_new should be a DataFrame with the same features as training data
data = {
  "sex": 0,
  "age": 20,
  "famsize": 0,
  "Pstatus": 0,
  "Medu": 0,
  "Fedu": 0,
  "traveltime": 1,
  "studytime": 1,
  "failures": 0,
  "schoolsup": 0,
  "famsup": 0,
  "paid": 0,
  "internet": 0,
  "romantic": 0,
  "famrel": 1,
  "freetime": 1,
  "goout": 1,
  "health": 1,
  "absences": 0,
  "G1": 20,
  "G2": 20,
  "Mjob_at_home": 1,
  "Mjob_health": 0,
  "Mjob_other": 0,
  "Mjob_services": 0,
  "Mjob_teacher": 0,
  "Fjob_at_home": 1,
  "Fjob_health": 0,
  "Fjob_other": 0,
  "Fjob_services": 0,
  "Fjob_teacher": 0,
  "guardian_father": 1,
  "guardian_mother": 0,
  "guardian_other": 0,
  "G3": 20
}
X_new = pd.DataFrame([data])
predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)

print("Predictions:", predictions)
print("Probabilities:", probabilities)