import React, { useState, useEffect } from 'react';
import './HRDashboard.css';

interface Interview {
  id: string;
  candidateName: string;
  position: string;
  status: 'created' | 'in_progress' | 'completed';
  createdAt: string;
  score?: number;
}

const HRDashboard: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInterviews();
  }, []);

  const loadInterviews = async () => {
    try {
      // Пытаемся загрузить реальные интервью из API
      const response = await fetch('http://localhost:8000/api/hr/interviews');
      if (response.ok) {
        const data = await response.json();
        // API возвращает объект с полем interviews, а не массив напрямую
        if (data && Array.isArray(data.interviews)) {
          setInterviews(data.interviews);
        } else if (data && typeof data === 'object' && 'interviews' in data) {
          // Если API вернул объект с полем interviews
          setInterviews([]);
        } else if (Array.isArray(data)) {
          // Если API вернул массив напрямую
          setInterviews(data);
        } else {
          // Если формат неожиданный, используем пустой массив
          setInterviews([]);
        }
        setLoading(false);
        return;
      }
    } catch (error) {
      console.warn('Не удалось загрузить реальные интервью, используем demo данные');
    }

    // Заглушка для демонстрации
    const mockInterviews: Interview[] = [
      {
        id: '1',
        candidateName: 'Иванов Иван',
        position: 'Frontend Developer',
        status: 'completed',
        createdAt: '2025-09-01',
        score: 85
      },
      {
        id: '2',
        candidateName: 'Петрова Анна',
        position: 'Backend Developer',
        status: 'in_progress',
        createdAt: '2025-09-02'
      }
    ];
    
    setTimeout(() => {
      setInterviews(mockInterviews);
      setLoading(false);
    }, 1000);
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'created': return 'Создано';
      case 'in_progress': return 'В процессе';
      case 'completed': return 'Завершено';
      default: return status;
    }
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'created': return 'status-created';
      case 'in_progress': return 'status-progress';
      case 'completed': return 'status-completed';
      default: return '';
    }
  };

  if (loading) {
    return (
      <div className="hr-dashboard">
        <div className="loading">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="hr-dashboard">
      <div className="dashboard-header">
        <h1>HR Панель</h1>
        <div className="navigation-buttons">
          <button 
            className="nav-btn active"
            onClick={() => window.location.href = '/hr/dashboard'}
          >
            Главная
          </button>
          <button 
            className="nav-btn"
            onClick={() => window.location.href = '/hr/create'}
          >
            Создать собеседование
          </button>
          <button 
            className="nav-btn"
            onClick={() => window.location.href = '/hr/results'}
          >
            Результаты
          </button>
          <button 
            className="nav-btn"
            onClick={() => window.location.href = '/test/microphone'}
          >
            Тест микрофона
          </button>
        </div>
      </div>

      <div className="main-actions">
        <div className="action-card">
          <h3>Создать собеседование</h3>
          <p>Загрузите вакансию и резюме для генерации вопросов</p>
          <button 
            className="action-btn primary"
            onClick={() => window.location.href = '/hr/create'}
          >
            Создать
          </button>
        </div>
        
        <div className="action-card">
          <h3>Просмотр результатов</h3>
          <p>Анализ оценок и результатов собеседований</p>
          <button 
            className="action-btn secondary"
            onClick={() => window.location.href = '/hr/results'}
          >
            Открыть
          </button>
        </div>
        
        <div className="action-card">
          <h3>Тест микрофона</h3>
          <p>Проверка работы аудио перед собеседованием</p>
          <button 
            className="action-btn secondary"
            onClick={() => window.location.href = '/test/microphone'}
          >
            Тестировать
          </button>
        </div>
      </div>

      <div className="interviews-list">
        <h2>Активные собеседования</h2>
        
        {interviews.length === 0 ? (
          <div className="empty-state">
            <p>Собеседования не найдены</p>
            <button 
              className="create-first-btn"
              onClick={() => window.location.href = '/hr/create'}
            >
              Создать первое собеседование
            </button>
          </div>
        ) : (
          <div className="interviews-table">
            <table>
              <thead>
                <tr>
                  <th>Кандидат</th>
                  <th>Позиция</th>
                  <th>Статус</th>
                  <th>Дата создания</th>
                  <th>Результат</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {interviews.map((interview) => (
                  <tr key={interview.id}>
                    <td>{interview.candidateName}</td>
                    <td>{interview.position}</td>
                    <td>
                      <span className={`status ${getStatusClass(interview.status)}`}>
                        {getStatusText(interview.status)}
                      </span>
                    </td>
                    <td>{interview.createdAt}</td>
                    <td>
                      {interview.score ? `${interview.score}%` : '-'}
                    </td>
                    <td>
                      <div className="actions">
                        {interview.status === 'completed' && (
                          <>
                            <button 
                              className="view-results-btn"
                              onClick={() => window.location.href = '/hr/results'}
                            >
                              Просмотр результатов
                            </button>
                            <button 
                              className="google-sheets-btn"
                              onClick={async () => {
                                try {
                                  const response = await fetch(`http://localhost:8000/api/hr/results/${interview.id}`);
                                  if (response.ok) {
                                    const data = await response.json();
                                    if (data.results_url) {
                                      window.open(data.results_url, '_blank');
                                    }
                                  }
                                } catch (error) {
                                  console.error('Ошибка получения ссылки на Google Sheets:', error);
                                  window.open(`https://docs.google.com/spreadsheets/d/demo_${interview.id}/edit`, '_blank');
                                }
                              }}
                            >
                              Google Sheets
                            </button>
                          </>
                        )}
                        <button 
                          className="view-requirements-btn"
                          onClick={() => window.location.href = `/hr/requirements/${interview.id}`}
                        >
                          Требования
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default HRDashboard;
