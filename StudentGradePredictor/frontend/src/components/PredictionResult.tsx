import React from 'react';
import './PredictionResult.css';

interface PredictionResultProps {
  prediction: {
    predicted_grade: number;
    pass_fail: string;
    probability_fail: number;
    probability_pass: number;
    confidence: string;
  };
}

const PredictionResult: React.FC<PredictionResultProps> = ({ prediction }) => {
  const getGradeColor = (grade: number) => {
    if (grade >= 15) return '#27ae60';
    if (grade >= 10) return '#f39c12';
    return '#e74c3c';
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return '#27ae60';
      case 'moderate': return '#f39c12';
      case 'low': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="prediction-result">
      <h2>Prediction Results</h2>
      
      <div className="result-cards">
        <div className="result-card grade-card">
          <h3>Predicted Grade</h3>
          <div 
            className="grade-value"
            style={{ color: getGradeColor(prediction.predicted_grade) }}
          >
            {prediction.predicted_grade}/20
          </div>
          <div className="grade-bar">
            <div 
              className="grade-fill"
              style={{ 
                width: `${(prediction.predicted_grade / 20) * 100}%`,
                backgroundColor: getGradeColor(prediction.predicted_grade)
              }}
            />
          </div>
        </div>

        <div className="result-card status-card">
          <h3>Pass/Fail Status</h3>
          <div 
            className={`status-value ${prediction.pass_fail}`}
          >
            {prediction.pass_fail.toUpperCase()}
          </div>
          <div className="status-description">
            {prediction.pass_fail === 'pass' 
              ? 'Student is predicted to pass the course'
              : 'Student is predicted to fail the course'
            }
          </div>
        </div>

        <div className="result-card probability-card">
          <h3>Confidence Level</h3>
          <div 
            className="confidence-value"
            style={{ color: getConfidenceColor(prediction.confidence) }}
          >
            {prediction.confidence.toUpperCase()}
          </div>
          <div className="probability-details">
            <div className="prob-item">
              <span>Pass: </span>
              <span className="prob-value pass">
                {(prediction.probability_pass * 100).toFixed(1)}%
              </span>
            </div>
            <div className="prob-item">
              <span>Fail: </span>
              <span className="prob-value fail">
                {(prediction.probability_fail * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="interpretation">
        <h3>Interpretation</h3>
        <div className="interpretation-text">
          {prediction.predicted_grade >= 10 ? (
            <p>
              ✅ The student is predicted to <strong>pass</strong> with a grade of{' '}
              <strong>{prediction.predicted_grade.toFixed(1)}/20</strong>.
            </p>
          ) : (
            <p>
              ❌ The student is predicted to <strong>fail</strong> with a grade of{' '}
              <strong>{prediction.predicted_grade.toFixed(1)}/20</strong>.
            </p>
          )}
          <p>
            Confidence in this prediction is{' '}
            <strong style={{ color: getConfidenceColor(prediction.confidence) }}>
              {prediction.confidence}
            </strong>{' '}
            ({(Math.max(prediction.probability_pass, prediction.probability_fail) * 100).toFixed(1)}%).
          </p>
        </div>
      </div>
    </div>
  );
};

export default PredictionResult;