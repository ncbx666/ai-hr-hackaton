import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Welcome.css';

const Welcome: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Проверяем валидность сессии
    const validateSession = async () => {
      try {
        // Имитация проверки сессии
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Мок данных сессии
        const mockSessionData = {
          id: sessionId,
          position: 'Frontend Developer',
          companyName: 'ТехноБанк',
          isValid: true
        };
        
        if (mockSessionData.isValid) {
          setSessionData(mockSessionData);
        } else {
          setError('Сессия недействительна или истекла');
        }
      } catch (err) {
        setError('Ошибка при загрузке данных сессии');
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      validateSession();
    } else {
      setError('Некорректная ссылка');
      setLoading(false);
    }
  }, [sessionId]);

  const handleStartInterview = () => {
    navigate(`/candidate/${sessionId}/registration`);
  };

  if (loading) {
    return (
      <div className="welcome-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="welcome-page">
        <div className="error-container">
          <h2>Ошибка</h2>
          <p>{error}</p>
          <p>Пожалуйста, обратитесь к HR для получения новой ссылки.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <div className="company-header">
          <h1>Добро пожаловать!</h1>
          <h2>{sessionData?.companyName}</h2>
        </div>

        <div className="position-info">
          <h3>Собеседование на позицию:</h3>
          <div className="position-name">{sessionData?.position}</div>
        </div>

        <div className="welcome-content">
          <div className="info-section">
            <h4>Что вас ждёт:</h4>
            <ul>
              <li>📋 Краткая регистрация (имя, согласие на обработку данных)</li>
              <li>🤖 Интерактивное собеседование с AI-ассистентом</li>
              <li>🗣️ Возможность отвечать голосом или текстом</li>
              <li>⏱️ Примерная продолжительность: 15-20 минут</li>
            </ul>
          </div>

          <div className="instructions">
            <h4>Рекомендации:</h4>
            <ul>
              <li>Найдите тихое место для проведения собеседования</li>
              <li>Проверьте микрофон (если планируете отвечать голосом)</li>
              <li>Будьте готовы рассказать о своём опыте работы</li>
              <li>Отвечайте честно и развёрнуто</li>
            </ul>
          </div>
        </div>

        <div className="start-section">
          <p className="ready-text">Готовы начать собеседование?</p>
          <button 
            onClick={handleStartInterview}
            className="start-btn"
          >
            Начать собеседование
          </button>
        </div>

        <div className="session-info">
          <small>ID сессии: {sessionId}</small>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
