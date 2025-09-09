import React, { useState } from 'react';
import './CreateInterview.css';

const CreateInterview: React.FC = () => {
  const [jobDescriptions, setJobDescriptions] = useState<File[]>([]);
  const [resumes, setResumes] = useState<File[]>([]);
  const [position, setPosition] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedLink, setGeneratedLink] = useState('');

  const handleJobDescriptionUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      setJobDescriptions(Array.from(files));
    }
  };

  const handleResumeUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      setResumes(Array.from(files));
    }
  } 

  const uploadFiles = async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
  const response = await fetch('http://localhost:8000/api/hr/upload-multi', {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Ошибка загрузки файлов');
    const data = await response.json();
    return data.files;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (jobDescriptions.length === 0 || resumes.length === 0 || !position) {
      alert('Пожалуйста, заполните все поля');
      return;
    }
    setLoading(true);
    try {
      // Загружаем вакансии
      const jobDescLinks = await uploadFiles(jobDescriptions);
      // Загружаем резюме
      const resumeLinks = await uploadFiles(resumes);
      // Формируем данные для API создания собеседования
      const interviewData = {
        position,
        job_description: jobDescLinks.map((f: { url: string }) => f.url).join(', '),
        resumes: resumeLinks.map((f: { filename: string; url: string }) => ({ filename: f.filename, url: f.url }))
      };
      // Отправляем запрос на создание собеседования
  const resp = await fetch('http://localhost:8000/api/hr/interviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(interviewData)
      });
      if (!resp.ok) throw new Error('Ошибка создания собеседования');
      const result = await resp.json();
      // Генерация уникальной ссылки
      const link = `${window.location.origin}/candidate/${result.id}/welcome`;
      setGeneratedLink(link);
    } catch (error) {
      alert('Ошибка при создании собеседования');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      // Попробуем современный Clipboard API
      await navigator.clipboard.writeText(generatedLink);
      alert('Ссылка скопирована в буфер обмена!');
    } catch (error) {
      // Fallback: используем старый метод через временное текстовое поле
      const textArea = document.createElement('textarea');
      textArea.value = generatedLink;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        document.execCommand('copy');
        alert('Ссылка скопирована в буфер обмена!');
      } catch (execError) {
        console.error('Ошибка копирования:', execError);
        // Показываем ссылку для ручного копирования
        prompt('Скопируйте ссылку вручную:', generatedLink);
      } finally {
        document.body.removeChild(textArea);
      }
    }
  };

  const resetForm = () => {
    setJobDescriptions([]);
    setResumes([]);
    setPosition('');
    setGeneratedLink('');
  };

  if (generatedLink) {
    return (
      <div className="create-interview">
        <div className="success-container">
          <h1>Ссылка сгенерирована!</h1>
          <div className="link-container">
            <p>На этом экране появляется уникальная ссылка для кандидата. HR её копирует и отправляет.</p>
            <div className="generated-link">
              <input 
                type="text" 
                value={generatedLink} 
                readOnly 
                className="link-input"
              />
              <button onClick={copyToClipboard} className="copy-btn">
                Копировать
              </button>
            </div>
            <p className="backend-info">
              🔧 Backend в этот момент: парсит файлы (ML-1), сохраняет всё в БД, генерирует ссылку.
            </p>
          </div>
          <div className="actions">
            <button onClick={resetForm} className="new-interview-btn">
              Создать новое собеседование
            </button>
            <button 
              onClick={() => window.location.href = '/hr/dashboard'} 
              className="dashboard-btn"
            >
              Вернуться к панели
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="create-interview">
      <div className="header">
        <h1>Создание собеседования</h1>
        <button 
          onClick={() => window.location.href = '/hr/dashboard'}
          className="back-btn"
        >
          ← Назад к панели
        </button>
      </div>

      <form onSubmit={handleSubmit} className="interview-form">
        <div className="form-section">
          <h2>Информация о позиции</h2>
          <div className="form-group">
            <label htmlFor="position">Название позиции:</label>
            <input
              type="text"
              id="position"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              placeholder="Например: Frontend Developer"
              required
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Загрузка файлов</h2>
          <div className="form-group">
            <label htmlFor="jobDescriptions">Описание вакансии (можно несколько):</label>
            <div className="file-upload">
              <input
                type="file"
                id="jobDescriptions"
                onChange={handleJobDescriptionUpload}
                accept=".pdf,.doc,.docx,.txt"
                multiple
                required
              />
              {jobDescriptions.length > 0 && (
                <div className="file-info">
                  <ul>
                    {jobDescriptions.map((file, idx) => (
                      <li key={idx}>✓ {file.name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="resumes">Резюме кандидатов (можно несколько):</label>
            <div className="file-upload">
              <input
                type="file"
                id="resumes"
                onChange={handleResumeUpload}
                accept=".pdf,.doc,.docx,.txt"
                multiple
                required
              />
              {resumes.length > 0 && (
                <div className="file-info">
                  <ul>
                    {resumes.map((file, idx) => (
                      <li key={idx}>✓ {file.name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="submit" 
            className="create-btn"
            disabled={loading}
          >
            {loading ? 'Создаётся...' : 'Создать'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="custom-spinner"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateInterview;
