import React, { useState, useRef } from 'react';

const MicrophoneTest: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('Готов к тестированию');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      setStatus('Запрашиваю доступ к микрофону...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      setStatus('✅ Доступ получен! Начинаю запись...');
      
      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setStatus('✅ Запись завершена! Можете воспроизвести.');
        
        // Останавливаем все треки
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      
    } catch (error: any) {
      let errorMessage = 'Ошибка доступа к микрофону: ';
      
      if (error.name === 'NotAllowedError') {
        errorMessage += 'Разрешите доступ к микрофону в браузере';
      } else if (error.name === 'NotFoundError') {
        errorMessage += 'Микрофон не найден';
      } else {
        errorMessage += error.message || 'Неизвестная ошибка';
      }
      
      setStatus(`❌ ${errorMessage}`);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus('Останавливаю запись...');
    }
  };

  const playRecording = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play();
      setStatus('🔊 Воспроизведение...');
      audio.onended = () => setStatus('✅ Воспроизведение завершено');
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
        background: 'white',
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ 
          color: '#2c3e50', 
          margin: 0,
          fontSize: '28px',
          fontWeight: 600 
        }}>🎤 Тест микрофона</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={() => window.location.href = '/hr/dashboard'}
            style={{
              backgroundColor: '#ecf0f1',
              color: '#34495e',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.3s ease'
            }}
          >
            Главная
          </button>
          <button 
            onClick={() => window.location.href = '/hr/create'}
            style={{
              backgroundColor: '#ecf0f1',
              color: '#34495e',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.3s ease'
            }}
          >
            Создать собеседование
          </button>
          <button 
            onClick={() => window.location.href = '/hr/results'}
            style={{
              backgroundColor: '#ecf0f1',
              color: '#34495e',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.3s ease'
            }}
          >
            Результаты
          </button>
          <button 
            onClick={() => window.location.href = '/test/microphone'}
            style={{
              backgroundColor: '#3498db',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.3s ease'
            }}
          >
            Тест микрофона
          </button>
        </div>
      </div>
      
      <div style={{
        background: 'white',
        padding: '30px',
        borderRadius: '12px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
      }}>
        <h2>🎤 Тест микрофона</h2>
      
      <div style={{ 
        margin: '20px 0', 
        padding: '15px', 
        background: '#f0f0f0', 
        borderRadius: '5px' 
      }}>
        <strong>Статус:</strong> {status}
      </div>

      <div style={{ margin: '20px 0' }}>
        {!isRecording ? (
          <button 
            onClick={startRecording}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              background: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            🎤 Начать запись
          </button>
        ) : (
          <button 
            onClick={stopRecording}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              background: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            ⏹️ Остановить запись
          </button>
        )}

        {audioUrl && (
          <button 
            onClick={playRecording}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              background: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            🔊 Воспроизвести
          </button>
        )}
      </div>

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <h3>Инструкция:</h3>
        <ol>
          <li>Нажмите "Начать запись"</li>
          <li>Разрешите доступ к микрофону в браузере</li>
          <li>Говорите в микрофон</li>
          <li>Нажмите "Остановить запись"</li>
          <li>Нажмите "Воспроизвести" чтобы услышать запись</li>
        </ol>
      </div>
      
      </div>
    </div>
  );
};

export default MicrophoneTest;
