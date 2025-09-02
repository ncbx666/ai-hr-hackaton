import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Waiting.css';

const Waiting: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [isReady, setIsReady] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');

  useEffect(() => {
    // Имитация проверки готовности системы
    const checkSystemReady = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsReady(true);
      } catch (error) {
        console.error('Ошибка при проверке готовности системы');
      }
    };

    checkSystemReady();
  }, []);

  const handleStartInterview = async () => {
    setIsConnecting(true);
    setConnectionStatus('connecting');

    try {
      // Имитация установки WebSocket соединения
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setConnectionStatus('connected');
      
      // Небольшая задержка перед переходом
      setTimeout(() => {
        navigate(`/candidate/${sessionId}/interview`);
      }, 1000);
      
    } catch (error) {
      alert('Ошибка при подключении к серверу собеседований');
      setIsConnecting(false);
      setConnectionStatus('disconnected');
    }
  };

  const getConnectionMessage = () => {
    switch (connectionStatus) {
      case 'connecting':
        return 'Устанавливаем соединение с AI-ассистентом...';
      case 'connected':
        return 'Соединение установлено! Переходим к собеседованию...';
      default:
        return '';
    }
  };

  return (
    <div className="waiting-page">
      <div className="waiting-container">
        <div className="header">
          <h1>Подготовка к собеседованию</h1>
          <p>Мы почти готовы начать ваше собеседование</p>
        </div>

        <div className="status-section">
          <div className="system-checks">
            <h3>Проверка системы:</h3>
            <div className="check-item">
              <span className={`check-icon ${isReady ? 'success' : 'loading'}`}>
                {isReady ? '✓' : '⏳'}
              </span>
              <span>AI-ассистент готов к работе</span>
            </div>
            <div className="check-item">
              <span className="check-icon success">✓</span>
              <span>Ваши данные сохранены</span>
            </div>
            <div className="check-item">
              <span className="check-icon success">✓</span>
              <span>Система скоринга подключена</span>
            </div>
          </div>

          {connectionStatus !== 'disconnected' && (
            <div className="connection-status">
              <div className="connection-message">
                {getConnectionMessage()}
              </div>
              <div className="connection-progress">
                <div className="progress-bar">
                  <div className={`progress-fill ${connectionStatus}`}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="instructions-section">
          <h3>Что будет дальше:</h3>
          <div className="instruction-steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Начало диалога</h4>
                <p>AI-ассистент поприветствует вас и зададёт первый вопрос</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Ответы на вопросы</h4>
                <p>Вы можете отвечать голосом или печатать текстом</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Завершение</h4>
                <p>После всех вопросов система покажет результат</p>
              </div>
            </div>
          </div>
        </div>

        <div className="tips-section">
          <h3>Полезные советы:</h3>
          <ul className="tips-list">
            <li>🎤 Говорите четко и не торопитесь при голосовых ответах</li>
            <li>💬 Можете переключаться между голосом и текстом в любой момент</li>
            <li>📖 Приводите конкретные примеры из вашего опыта</li>
            <li>⏱️ Обычно собеседование длится 15-20 минут</li>
          </ul>
        </div>

        <div className="ready-section">
          <p className="ready-question">
            {isReady ? 'Всё готово! Можете начинать собеседование.' : 'Ожидаем готовности системы...'}
          </p>
          
          <button 
            onClick={handleStartInterview}
            className="start-interview-btn"
            disabled={!isReady || isConnecting}
          >
            {isConnecting ? 'Подключение...' : 'Я готов, начинаем!'}
          </button>
        </div>

        <div className="backend-info">
          <p>🔧 В этот момент Frontend устанавливает WebSocket-соединение с Backend.</p>
        </div>
      </div>
    </div>
  );
};

export default Waiting;
