import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Interview.css';

interface Message {
  id: string;
  type: 'ai' | 'user';
  content: string;
  timestamp: Date;
  isVoice?: boolean;
}

const Interview: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('text');
  const [interviewStep, setInterviewStep] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const totalSteps = 5; // Общее количество вопросов

  useEffect(() => {
    // Инициализация собеседования
    startInterview();
  }, []);

  useEffect(() => {
    // Автоскролл к последнему сообщению
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startInterview = async () => {
    // Приветственное сообщение от AI
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: 'Здравствуйте! Меня зовут AI-ассистент, и я проведу с вами собеседование. Давайте начнем с небольшого рассказа о себе. Расскажите о своем опыте работы и ключевых навыках.',
      timestamp: new Date()
    };
    
    setMessages([welcomeMessage]);
    setInterviewStep(1);
  };

  const sendMessage = async (content: string, isVoice: boolean = false) => {
    if (!content.trim()) return;

    // Добавляем сообщение пользователя
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
      isVoice
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsProcessing(true);

    try {
      // Имитация обработки ответа и генерации следующего вопроса
      await new Promise(resolve => setTimeout(resolve, 2000));

      const nextQuestion = getNextQuestion(interviewStep);
      
      if (nextQuestion) {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: nextQuestion,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        setInterviewStep(prev => prev + 1);
      } else {
        // Собеседование завершено
        const completionMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: 'Спасибо за ваши ответы! Собеседование завершено. Мы обработаем результаты и свяжемся с вами в ближайшее время.',
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, completionMessage]);
        
        // Переход к завершению через 3 секунды
        setTimeout(() => {
          navigate(`/candidate/${sessionId}/completion`);
        }, 3000);
      }
    } catch (error) {
      console.error('Ошибка при обработке сообщения:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const getNextQuestion = (step: number): string | null => {
    const questions = [
      '', // step 0 - уже задан приветственный вопрос
      'Расскажите о самом сложном проекте, над которым вы работали. Какие технологии использовали и какие проблемы решали?',
      'Опишите ситуацию, когда вам пришлось работать в команде над срочной задачей. Как вы организовали работу?',
      'Как вы обычно изучаете новые технологии? Приведите пример последней технологии, которую освоили.',
      'Почему вы хотите работать именно у нас? Что вас привлекает в данной позиции?',
    ];

    return step < questions.length ? questions[step] : null;
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(currentMessage, false);
  };

  const startVoiceRecording = async () => {
    setIsRecording(true);
    // Здесь будет реальная интеграция с Web Speech API
    
    // Имитация записи голоса
    setTimeout(() => {
      setIsRecording(false);
      const mockVoiceText = "Это пример голосового ответа, который был распознан системой";
      sendMessage(mockVoiceText, true);
    }, 3000);
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="interview-page">
      <div className="interview-header">
        <h1>Собеседование</h1>
        <div className="progress-info">
          <span>Вопрос {interviewStep} из {totalSteps}</span>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${(interviewStep / totalSteps) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages-area">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.type}`}
            >
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-meta">
                  <span className="message-time">{formatTime(message.timestamp)}</span>
                  {message.isVoice && <span className="voice-indicator">🎤</span>}
                </div>
              </div>
            </div>
          ))}
          {isProcessing && (
            <div className="message ai">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-mode-switcher">
            <button 
              className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
              onClick={() => setInputMode('text')}
              disabled={isProcessing}
            >
              ✏️ Текст
            </button>
            <button 
              className={`mode-btn ${inputMode === 'voice' ? 'active' : ''}`}
              onClick={() => setInputMode('voice')}
              disabled={isProcessing}
            >
              🎤 Голос
            </button>
          </div>

          {inputMode === 'text' ? (
            <form onSubmit={handleTextSubmit} className="text-input-form">
              <div className="input-group">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  placeholder="Введите ваш ответ..."
                  className="message-input"
                  disabled={isProcessing}
                  rows={3}
                />
                <button 
                  type="submit" 
                  className="send-btn"
                  disabled={!currentMessage.trim() || isProcessing}
                >
                  Отправить
                </button>
              </div>
            </form>
          ) : (
            <div className="voice-input-area">
              <button 
                className={`voice-btn ${isRecording ? 'recording' : ''}`}
                onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                disabled={isProcessing}
              >
                {isRecording ? '⏹️ Остановить запись' : '🎤 Начать запись'}
              </button>
              {isRecording && (
                <div className="recording-indicator">
                  <span className="recording-dot"></span>
                  Идет запись...
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="backend-info">
        <p>🔧 Самая сложная часть для Backend: Real-time цикл (Google S2T → Gemini (ML-2) → Google TTS).</p>
      </div>
    </div>
  );
};

export default Interview;
