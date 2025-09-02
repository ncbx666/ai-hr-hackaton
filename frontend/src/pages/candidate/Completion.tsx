import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './Completion.css';

const Completion: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  useEffect(() => {
    // Запуск процесса скоринга
    const processResults = async () => {
      try {
        // Имитация запуска скоринга на backend
        console.log('Запуск скоринга для сессии:', sessionId);
        
        // Здесь backend:
        // 1. Запускает scoring (ML-3) 
        // 2. Сохраняет отчёт в БД
        // 3. Обновляет Google Таблицу
        
      } catch (error) {
        console.error('Ошибка при обработке результатов:', error);
      }
    };

    processResults();
  }, [sessionId]);

  return (
    <div className="completion-page">
      <div className="completion-container">
        <div className="success-icon">
          <div className="checkmark">
            <div className="checkmark-circle"></div>
            <div className="checkmark-stem"></div>
            <div className="checkmark-kick"></div>
          </div>
        </div>

        <div className="completion-content">
          <h1>Спасибо!</h1>
          <h2>Собеседование завершено</h2>
          
          <div className="completion-message">
            <p>
              Благодарим вас за время, потраченное на прохождение собеседования. 
              Ваши ответы были записаны и будут тщательно проанализированы нашей системой.
            </p>
          </div>

          <div className="next-steps">
            <h3>Что происходит дальше:</h3>
            <div className="steps-list">
              <div className="step-item">
                <div className="step-icon">🤖</div>
                <div className="step-text">
                  <strong>Анализ ответов:</strong> AI-система обрабатывает ваши ответы и выставляет оценки
                </div>
              </div>
              <div className="step-item">
                <div className="step-icon">📊</div>
                <div className="step-text">
                  <strong>Формирование отчёта:</strong> Система создаёт детальный отчёт для HR-специалиста
                </div>
              </div>
              <div className="step-item">
                <div className="step-icon">📧</div>
                <div className="step-text">
                  <strong>Обратная связь:</strong> HR-менеджер свяжется с вами в течение 2-3 рабочих дней
                </div>
              </div>
            </div>
          </div>

          <div className="contact-info">
            <h3>Остались вопросы?</h3>
            <p>
              Если у вас есть вопросы о процессе собеседования или вакансии, 
              вы можете связаться с нашим HR-отделом:
            </p>
            <div className="contact-details">
              <div className="contact-item">
                <span>📧</span>
                <span>hr@company.com</span>
              </div>
              <div className="contact-item">
                <span>📞</span>
                <span>+7 (495) 123-45-67</span>
              </div>
            </div>
          </div>

          <div className="session-info">
            <h3>Информация о сессии:</h3>
            <div className="session-details">
              <div className="detail-item">
                <span>ID сессии:</span>
                <span className="session-id">{sessionId}</span>
              </div>
              <div className="detail-item">
                <span>Дата завершения:</span>
                <span>{new Date().toLocaleDateString('ru-RU')}</span>
              </div>
              <div className="detail-item">
                <span>Время завершения:</span>
                <span>{new Date().toLocaleTimeString('ru-RU')}</span>
              </div>
            </div>
          </div>

          <div className="feedback-section">
            <h3>Поделитесь мнением</h3>
            <p>
              Ваше мнение о процессе собеседования поможет нам улучшить систему. 
              Оцените ваш опыт от 1 до 5 звёзд:
            </p>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map(star => (
                <button key={star} className="star-btn">
                  ⭐
                </button>
              ))}
            </div>
          </div>

          <div className="closing-message">
            <p>
              <strong>Еще раз спасибо за ваш интерес к нашей компании!</strong>
            </p>
            <p>
              Мы ценим ваше время и надеемся на дальнейшее сотрудничество.
            </p>
          </div>
        </div>

        <div className="backend-info">
          <p>🔧 Backend в этот момент: запускает скоринг (ML-3), сохраняет отчёт в БД, обновляет Google Таблицу.</p>
        </div>
      </div>
    </div>
  );
};

export default Completion;
