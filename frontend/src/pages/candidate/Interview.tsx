import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import './Interview.css';

interface Message {
  type: 'welcome' | 'transcript' | 'question' | 'interview_ended' | 'audio_response' | 'processing_completed' | 'info_received';
  text?: string;
  message?: string;
  is_final?: boolean;
  question_number?: number;
  audio_data?: string;
  processing_result?: any;
}

const Interview: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [processingResult, setProcessingResult] = useState<any>(null);
  const [candidateName, setCandidateName] = useState('');
  const [showNameInput, setShowNameInput] = useState(true);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Функция для воспроизведения аудио ответа
  const playAudioResponse = (audioBase64: string) => {
    try {
      // Декодируем base64 в blob
      const audioData = atob(audioBase64);
      const arrayBuffer = new ArrayBuffer(audioData.length);
      const uint8Array = new Uint8Array(arrayBuffer);
      
      for (let i = 0; i < audioData.length; i++) {
        uint8Array[i] = audioData.charCodeAt(i);
      }
      
      const blob = new Blob([uint8Array], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(blob);
      
      const audio = new Audio(audioUrl);
      audio.play().catch(e => console.error('Audio play error:', e));
      
      // Очищаем URL после воспроизведения
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
    } catch (error) {
      console.error('Audio decoding error:', error);
    }
  };

  // WebSocket подключение
  useEffect(() => {
    if (!sessionId) return;

    const websocket = new WebSocket(`ws://localhost:8000/ws/interview/${sessionId}`);
    
    websocket.onopen = () => {
      console.log('[WebSocket] Подключение установлено');
      setIsConnected(true);
    };

    websocket.onmessage = (event) => {
      const message: Message = JSON.parse(event.data);
      console.log('[WebSocket] Получено:', message);
      
      switch (message.type) {
        case 'welcome':
          setMessages(prev => [...prev, message]);
          break;
          
        case 'transcript':
          if (message.is_final) {
            setCurrentTranscript('');
            setMessages(prev => [...prev, message]);
          } else {
            setCurrentTranscript(message.text || '');
          }
          break;
          
        case 'question':
          setMessages(prev => [...prev, message]);
          break;
          
        case 'audio_response':
          // Воспроизводим аудио ответ
          if (message.audio_data) {
            playAudioResponse(message.audio_data);
          }
          break;
          
        case 'interview_ended':
          setMessages(prev => [...prev, message]);
          setIsRecording(false);
          break;
          
        case 'processing_completed':
          setMessages(prev => [...prev, {
            type: 'interview_ended',
            message: 'Обработка завершена! Результаты готовы.'
          }]);
          setProcessingResult(message.processing_result);
          break;
          
        case 'info_received':
          setMessages(prev => [...prev, message]);
          setShowNameInput(false);
          break;
          
        default:
          setMessages(prev => [...prev, message]);
      }
    };

    websocket.onclose = () => {
      console.log('[WebSocket] Соединение закрыто');
      setIsConnected(false);
    };

    websocket.onerror = (error) => {
      console.error('[WebSocket] Ошибка:', error);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [sessionId]);

  // Запуск записи аудио
  const startRecording = async () => {
    try {
      console.log('[Recording] Запрашиваю доступ к микрофону...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      console.log('[Recording] Доступ к микрофону получен');
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log(`[Recording] Получен аудио чанк: ${event.data.size} байт`);
          
          // Отправляем реальные аудио данные через WebSocket
          if (ws && ws.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.onload = () => {
              const arrayBuffer = reader.result as ArrayBuffer;
              const uint8Array = new Uint8Array(arrayBuffer);
              const binaryString = Array.from(uint8Array, byte => String.fromCharCode(byte)).join('');
              const base64 = btoa(binaryString);
              
              ws.send(JSON.stringify({
                type: 'audio_chunk',
                data: base64,
                size: event.data.size
              }));
            };
            reader.readAsArrayBuffer(event.data);
          }
        }
      };

      mediaRecorder.onstop = () => {
        console.log('[Recording] Запись остановлена');
        
        if (audioChunksRef.current.length > 0) {
          // Создаем финальную запись
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          console.log(`[Recording] Создан финальный блоб: ${audioBlob.size} байт`);
          
          // Отправляем финальный сигнал
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              type: 'recording_finished',
              total_chunks: audioChunksRef.current.length,
              total_size: audioBlob.size
            }));
          }
        }
        
        // Очищаем аудио чанки
        audioChunksRef.current = [];
        
        // Останавливаем все треки
        stream.getTracks().forEach(track => {
          track.stop();
          console.log('[Recording] Трек остановлен:', track.kind);
        });
      };

      mediaRecorder.onerror = (event) => {
        console.error('[Recording] Ошибка MediaRecorder:', event);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(500); // Записываем чанки каждые 500мс
      setIsRecording(true);
      
      console.log('[Recording] Запись началась');
      
    } catch (error: any) {
      console.error('[Recording] Ошибка доступа к микрофону:', error);
      
      let errorMessage = 'Не удалось получить доступ к микрофону: ';
      
      if (error.name === 'NotAllowedError') {
        errorMessage += 'Разрешите доступ к микрофону в браузере';
      } else if (error.name === 'NotFoundError') {
        errorMessage += 'Микрофон не найден';
      } else {
        errorMessage += error.message || 'Неизвестная ошибка';
      }
      
      alert(errorMessage);
    }
  };

  // Остановка записи
  const stopRecording = () => {
    console.log('[Recording] Останавливаю запись...');
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      console.log('[Recording] Команда остановки отправлена');
    } else {
      console.log('[Recording] MediaRecorder не активен или уже остановлен');
      setIsRecording(false);
    }
  };

  // Функция для отправки имени кандидата
  const submitCandidateName = () => {
    if (ws && ws.readyState === WebSocket.OPEN && candidateName.trim()) {
      ws.send(JSON.stringify({ 
        type: 'candidate_info', 
        name: candidateName.trim() 
      }));
    }
  };

  // Функция для перенаправления на страницу настройки микрофона
  const setupMicrophone = () => {
    const currentUrl = window.location.href;
    const setupUrl = `/microphone-permission?return=${encodeURIComponent(currentUrl)}`;
    window.location.href = setupUrl;
  };

  // Завершение интервью
  const endInterview = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'end_interview' }));
    }
  };

  return (
    <div className="interview-container">
      <div className="interview-header">
        <h1>Интервью - Сессия {sessionId}</h1>
        <div className="connection-status">
          Статус: {isConnected ? '🟢 Подключено' : '🔴 Отключено'}
        </div>
      </div>

      <div className="interview-content">
        {showNameInput && (
          <div className="name-input-section">
            <h3>Представьтесь, пожалуйста:</h3>
            <div className="name-input">
              <input
                type="text"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                placeholder="Введите ваше имя"
                onKeyPress={(e) => e.key === 'Enter' && submitCandidateName()}
              />
              <button onClick={submitCandidateName} disabled={!candidateName.trim()}>
                Продолжить
              </button>
            </div>
          </div>
        )}
        
        {!showNameInput && (
          <>
            <div className="messages-section">
              <h3>История интервью:</h3>
              <div className="messages-list">
                {messages.map((msg, index) => (
                  <div key={index} className={`message message-${msg.type}`}>
                    {msg.type === 'welcome' && (
                      <p><strong>Система:</strong> {msg.message}</p>
                    )}
                    {msg.type === 'transcript' && (
                      <p><strong>Ваш ответ:</strong> {msg.text}</p>
                    )}
                    {msg.type === 'question' && (
                      <p><strong>Вопрос {msg.question_number}:</strong> {msg.text}</p>
                    )}
                    {msg.type === 'interview_ended' && (
                      <p><strong>Система:</strong> {msg.message}</p>
                    )}
                    {msg.type === 'info_received' && (
                      <p><strong>Система:</strong> {msg.message}</p>
                    )}
                  </div>
                ))}
              </div>
              
              {currentTranscript && (
                <div className="current-transcript">
                  <p><strong>Сейчас говорите:</strong> {currentTranscript}</p>
                </div>
              )}
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
                    disabled={!isConnected}
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
                  onClick={endInterview}
                  disabled={!isConnected}
                  className="end-button"
                >
                  ❌ Завершить интервью
                </button>
              </div>
            </div>
          </>
        )}
        
        {processingResult && (
          <div className="processing-results">
            <h3>Результаты обработки:</h3>
            <div className="results-content">
              <p><strong>Статус:</strong> {processingResult.status}</p>
              {processingResult.scoring_result && (
                <div className="scoring-results">
                  <h4>Результаты скоринга:</h4>
                  <pre>{JSON.stringify(processingResult.scoring_result, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Interview;
