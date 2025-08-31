import React, { useState, useEffect } from 'react';
import './PredictionForm.css';
import PredictionResult from '../../components/PredictionResult';
import { getFormStructure, predict } from '../../services/predict';

interface FormField {
  name: string;
  type: string;
  label: string;
  options?: Array<{ value: any; label: string }>;
  min?: number;
  max?: number;
}

interface FormData {
  [key: string]: any;
}

interface PredictionResponse {
  predicted_grade: number;
  pass_fail: string;
  probability_fail: number;
  probability_pass: number;
  confidence: string;
}

const PredictionForm: React.FC = () => {
  const [formFields, setFormFields] = useState<FormField[]>([]);
  const [formData, setFormData] = useState<FormData>({});
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  

  useEffect(() => {
    fetchFormStructure();
  }, []);

  const fetchFormStructure = async () => {
    try {
      const response = await getFormStructure();
      setFormFields(response.fields);
      console.log(response);
      
      // Initialize form data with default values
      const initialData: FormData = {};
      response.fields.forEach((field: FormField) => {
        if (field.type === 'number') {
          initialData[field.name] = field.min || 0;
        } else if (field.type === 'select' && field.options && field.options.length > 0) {
          initialData[field.name] = field.options[0].value;
        } else {
          initialData[field.name] = '';
        }
      });
      setFormData(initialData);
    } catch (err) {
      setError('Failed to load form structure');
      console.error('Error fetching form structure:', err);
    }
  };

  const handleInputChange = (name: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const convertFormDataForAPI = (data: FormData) => {
    const apiData: FormData = { ...data };
    
    // Convert job selections to one-hot encoding
    const motherJob = data.mother_job;
    const fatherJob = data.father_job;
    const guardian = data.guardian;

    // Remove the simple job fields
    delete apiData.mother_job;
    delete apiData.father_job;
    delete apiData.guardian;

    // Add mother job one-hot encoding
    apiData.Mjob_at_home = motherJob === 'at_home' ? 1 : 0;
    apiData.Mjob_health = motherJob === 'health' ? 1 : 0;
    apiData.Mjob_other = motherJob === 'other' ? 1 : 0;
    apiData.Mjob_services = motherJob === 'services' ? 1 : 0;
    apiData.Mjob_teacher = motherJob === 'teacher' ? 1 : 0;

    // Add father job one-hot encoding
    apiData.Fjob_at_home = fatherJob === 'at_home' ? 1 : 0;
    apiData.Fjob_health = fatherJob === 'health' ? 1 : 0;
    apiData.Fjob_other = fatherJob === 'other' ? 1 : 0;
    apiData.Fjob_services = fatherJob === 'services' ? 1 : 0;
    apiData.Fjob_teacher = fatherJob === 'teacher' ? 1 : 0;

    // Add guardian one-hot encoding
    apiData.guardian_father = guardian === 'father' ? 1 : 0;
    apiData.guardian_mother = guardian === 'mother' ? 1 : 0;
    apiData.guardian_other = guardian === 'other' ? 1 : 0;

    return apiData;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPrediction(null);

    try {
      const apiData = convertFormDataForAPI(formData);
      const response = await predict(apiData);
      setPrediction(response);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to get prediction');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderField = (field: FormField) => {
    console.log(field);
    if (field.type === 'select') {
      return (
        <select
          id={field.name}
          value={formData[field.name] || ''}
          onChange={(e) => handleInputChange(field.name, field.type === 'number' ? Number(e.target.value) : e.target.value)}
          required
        >
          {field.options?.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    } else if (field.type === 'number') {
      return (
        <input
          type="number"
          id={field.name}
          onChange={(e) => handleInputChange(field.name, Number(e.target.value))}
          min={field.min}
          max={field.max}
          required
        />
      );
    } else {
      return (
        <input
          type="text"
          id={field.name}
          value={formData[field.name] || ''}
          onChange={(e) => handleInputChange(field.name, e.target.value)}
          required
        />
      );
    }
  };

  const groupFields = (fields: FormField[]) => {
    const groups = {
      basic: fields.slice(0, 4),
      education: fields.slice(4, 9),
      support: fields.slice(9, 15),
      personal: fields.slice(15, 20),
      family: fields.slice(20,23),
      academic: fields.slice(23, 25)
    };
    return groups;
  };

  const fieldGroups = groupFields(formFields);

  return (
    <div className="prediction-container">
      <div className="form-section">
        <h2>Student Information Form</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="form-group">
            <h3>Basic Information</h3>
            <div className="form-row">
              {fieldGroups.basic.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3>Education Background</h3>
            <div className="form-row">
              {fieldGroups.education.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3>Support & Activities</h3>
            <div className="form-row">
              {fieldGroups.support.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3>Personal & Social</h3>
            <div className="form-row">
              {fieldGroups.personal.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3>Family Information</h3>
            <div className="form-row">
              {fieldGroups.family.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <h3>Academic Information</h3>
            <div className="form-row">
              {fieldGroups.academic.map(field => (
                <div key={field.name} className="form-field">
                  <label htmlFor={field.name}>{field.label}</label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>

          <button 
            type="submit" 
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Predicting...' : 'Get Prediction'}
          </button>
        </form>
      </div>

      {prediction && (
        <div className="result-section">
          <PredictionResult prediction={prediction} />
        </div>
      )}
    </div>
  );
};

export default PredictionForm;