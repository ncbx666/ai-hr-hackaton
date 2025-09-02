import React, { useState } from 'react';
import './CreateInterview.css';

const CreateInterview: React.FC = () => {
  const [jobDescription, setJobDescription] = useState<File | null>(null);
  const [resume, setResume] = useState<File | null>(null);
  const [candidateName, setCandidateName] = useState('');
  const [position, setPosition] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedLink, setGeneratedLink] = useState('');

  const handleJobDescriptionUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setJobDescription(file);
    }
  };

  const handleResumeUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setResume(file);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!jobDescription || !resume || !candidateName || !position) {
      alert('Пожалуйста, заполните все поля');
      return;
    }

    setLoading(true);

    try {
      // Имитация создания собеседования
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Генерация уникальной ссылки
      const sessionId = Math.random().toString(36).substring(2, 15);
      const link = `${window.location.origin}/candidate/${sessionId}/welcome`;
      setGeneratedLink(link);
      
    } catch (error) {
      alert('Ошибка при создании собеседования');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedLink);
    alert('Ссылка скопирована в буфер обмена!');
  };

  const resetForm = () => {
    setJobDescription(null);
    setResume(null);
    setCandidateName('');
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

          <div className="form-group">
            <label htmlFor="candidateName">Имя кандидата:</label>
            <input
              type="text"
              id="candidateName"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              placeholder="Например: Иванов Иван Иванович"
              required
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Загрузка файлов</h2>
          
          <div className="form-group">
            <label htmlFor="jobDescription">Описание вакансии:</label>
            <div className="file-upload">
              <input
                type="file"
                id="jobDescription"
                onChange={handleJobDescriptionUpload}
                accept=".pdf,.doc,.docx,.txt"
                required
              />
              {jobDescription && (
                <div className="file-info">
                  ✓ Загружен: {jobDescription.name}
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="resume">Резюме пользователя:</label>
            <div className="file-upload">
              <input
                type="file"
                id="resume"
                onChange={handleResumeUpload}
                accept=".pdf,.doc,.docx,.txt"
                required
              />
              {resume && (
                <div className="file-info">
                  ✓ Загружено: {resume.name}
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
            <p>Обрабатываем файлы и создаём собеседование...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateInterview;
