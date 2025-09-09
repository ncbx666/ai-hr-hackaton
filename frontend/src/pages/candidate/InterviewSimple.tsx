import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import './Interview.css';

const InterviewSimple: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);

  // Функция для настройки микрофона
  const setupMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      alert('✅ Доступ к микрофону получен!');
      stream.getTracks().forEach(track => track.stop());
    } catch (error: any) {
      alert('❌ Ошибка доступа к микрофону: ' + error.message);
    }
  };

  // Начать запись
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsRecording(true);
      setMessages(prev => [...prev, '🎤 Запись началась...']);
      
      // Останавливаем через 5 секунд для демо
      setTimeout(() => {
        stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
        setMessages(prev => [...prev, '⏹️ Запись остановлена']);
      }, 5000);
      
    } catch (error: any) {
      alert('❌ Ошибка записи: ' + error.message);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setMessages(prev => [...prev, '⏹️ Запись остановлена вручную']);
  };

  return (
    <div className="interview-container">
      <div className="interview-header">
        <h1>Интервью - Сессия {sessionId}</h1>
        <div className="connection-status">
          Статус: 🟢 Готов к работе
        </div>
      </div>

      <div className="interview-content">
        <div className="messages-section">
          <h3>Сообщения:</h3>
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className="message">
                {msg}
              </div>
            ))}
            {messages.length === 0 && (
              <p>Пока сообщений нет. Настройте микрофон и начните запись.</p>
            )}
          </div>
        </div>

        <div className="controls-section">
          <div className="microphone-setup">
            <button 
              onClick={setupMicrophone}
              className="setup-button"
              title="Настроить доступ к микрофону"
            >
              🔐 Настроить микрофон
            </button>
          </div>
          
          <div className="recording-controls">
            {!isRecording ? (
              <button 
                onClick={startRecording}
                className="record-button"
              >
                🎤 Начать запись
              </button>
            ) : (
              <button 
                onClick={stopRecording}
                className="stop-button"
              >
                ⏹️ Остановить запись
              </button>
            )}
          </div>

          <div className="interview-controls">
            <button 
              onClick={() => setMessages(prev => [...prev, '❌ Интервью завершено'])}
              className="end-button"
            >
              ❌ Завершить интервью
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewSimple;
