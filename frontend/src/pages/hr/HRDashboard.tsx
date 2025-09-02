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
  }, []);

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
        <h1>Панель HR - Управление собеседованиями</h1>
        <button 
          className="create-btn"
          onClick={() => window.location.href = '/hr/create'}
        >
          Создать новое собеседование
        </button>
      </div>

      <div className="interviews-list">
        <h2>Список уже созданных собеседований</h2>
        
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
                          <button 
                            className="view-results-btn"
                            onClick={() => window.location.href = '/hr/results'}
                          >
                            Просмотр результатов
                          </button>
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
