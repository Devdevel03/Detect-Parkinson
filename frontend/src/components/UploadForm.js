import React, { useState } from 'react';
import './UploadForm.css';

function UploadForm({ onPredict, disabled }) {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('No file chosen');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv') {
        setError('Invalid file type. Please upload a .csv file.');
        setFile(null);
        setFileName('No file chosen');
        return;
      }
      setError('');
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please choose a file before predicting.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    onPredict(formData);
  };

  return (
    <div className="upload-form-container">
      <p className="upload-instructions">
        Upload a CSV file containing voice measurements to get a prediction. The file must contain the 22 feature columns from the standard Parkinson's dataset.
      </p>
      <form onSubmit={handleSubmit} className="upload-form">
        <label htmlFor="file-upload" className="custom-file-upload">
          {fileName}
        </label>
        <input 
          id="file-upload" 
          type="file" 
          accept=".csv"
          onChange={handleFileChange} 
          disabled={disabled}
        />
        <button type="submit" disabled={disabled || !file}>
          {disabled ? 'Analyzing...' : 'Get Prediction'}
        </button>
      </form>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}

export default UploadForm;