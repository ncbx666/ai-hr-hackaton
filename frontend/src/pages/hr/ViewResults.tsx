import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import './ViewResults.css';

interface ScoreDetails {
  skill: string;
  score: string;
  comment: string;
}

interface ScoreBreakdown {
  hard_skills: {
    score_percent: number;
    details: ScoreDetails[];
  };
  experience: {
    score_percent: number;
    comment: string;
    scores: {
      duration: number;
      relevance: number;
      functionality: number;
    };
    penalty: number;
  };
  soft_skills: {
    score_percent: number;
    comment: string;
    scores: {
      star_method: number;
      motivation: number;
    };
  };
}

interface CandidateResult {
  candidate_name: string;
  final_score_percent: number;
  verdict: string;
  breakdown: ScoreBreakdown;
}

const ViewResults: React.FC = () => {
  const [results, setResults] = useState<CandidateResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [googleSheetsUrl, setGoogleSheetsUrl] = useState<string>('');

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      // Пытаемся загрузить реальные результаты из API
      const response = await fetch('http://localhost:8000/api/hr/results/current_interview');
      if (response.ok) {
        const data = await response.json();
        if (data.results_url) {
          setGoogleSheetsUrl(data.results_url);
        }
      }
    } catch (error) {
      console.warn('Не удалось загрузить реальные результаты, используем demo данные');
    }

    // Загружаем demo результаты для отображения
    const mockResult: CandidateResult = {
      candidate_name: "Сергеев Иван Петрович",
      final_score_percent: 82.33,
      verdict: "Рекомендован к следующему этапу",
      breakdown: {
        hard_skills: {
          score_percent: 85.0,
          details: [
            {
              skill: "Антифрод",
              score: "5/5",
              comment: "Глубокая экспертиза: приведены инструменты, метрики и объяснение выбора решения."
            },
            {
              skill: "СУБД",
              score: "4/5",
              comment: "Конкретный кейс: упомянуты инструменты и измеримые результаты."
            },
            {
              skill: "Разработка ТЗ",
              score: "2/5",
              comment: "Общее описание: есть понимание процесса, но без конкретных примеров."
            },
            {
              skill: "ДБО ЮЛ",
              score: "0/5",
              comment: "Уход от ответа или ответ слишком короткий."
            }
          ]
        },
        experience: {
          score_percent: 81.67,
          comment: "Оценка опыта частично использует заглушки.",
          scores: {
            duration: 100.0,
            relevance: 70.0,
            functionality: 75.0
          },
          penalty: 1.0
        },
        soft_skills: {
          score_percent: 90.0,
          comment: "Оценка Soft Skills основана на анализе ответов.",
          scores: {
            star_method: 100.0,
            motivation: 80.0
          }
        }
      }
    };

    setTimeout(() => {
      setResults(mockResult);
      setLoading(false);
    }, 1000);
  };

  const getVerdictClass = (verdict: string) => {
    if (verdict.includes('Рекомендован')) return 'verdict-recommended';
    if (verdict.includes('дополнительное')) return 'verdict-review';
    return 'verdict-rejected';
  };

  const exportToExcel = () => {
    if (!results) return;
    // Формируем данные для экспорта
    const data = [
      {
        'Кандидат': results.candidate_name,
        'Общий балл (%)': results.final_score_percent,
        'Вердикт': results.verdict,
      },
      ...results.breakdown.hard_skills.details.map(skill => ({
        'Навык': skill.skill,
        'Оценка': skill.score,
        'Комментарий': skill.comment
      })),
      {
        'Опыт работы (%)': results.breakdown.experience.score_percent,
        'Комментарий': results.breakdown.experience.comment,
        'Продолжительность (%)': results.breakdown.experience.scores.duration,
        'Релевантность (%)': results.breakdown.experience.scores.relevance,
        'Функциональность (%)': results.breakdown.experience.scores.functionality
      },
      {
        'Soft Skills (%)': results.breakdown.soft_skills.score_percent,
        'Комментарий': results.breakdown.soft_skills.comment,
        'STAR метод (%)': results.breakdown.soft_skills.scores.star_method,
        'Мотивация (%)': results.breakdown.soft_skills.scores.motivation
      }
    ];
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Результаты');
    XLSX.writeFile(workbook, 'interview_results.xlsx');
  };

  const openGoogleSheets = () => {
    const urlToOpen = googleSheetsUrl || 'https://docs.google.com/spreadsheets/d/demo_sheet/edit';
    window.open(urlToOpen, '_blank');
  };

  if (loading) {
    return (
      <div className="view-results">
        <div className="loading">Загрузка результатов...</div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="view-results">
        <div className="error">Результаты не найдены</div>
      </div>
    );
  }

  return (
    <div className="view-results">
      <div className="header">
        <h1>Результаты собеседования</h1>
        <div className="navigation-buttons">
          <button 
            className="nav-btn"
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
            className="nav-btn active"
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
        <div className="header-actions">
          <button 
            onClick={() => setEditMode(!editMode)}
            className="edit-btn"
          >
            {editMode ? 'Сохранить' : 'Редактировать'}
          </button>
          <button onClick={exportToExcel} className="export-btn">
            Экспорт в Excel
          </button>
          <button onClick={openGoogleSheets} className="export-btn">
            Открыть Google Sheets
          </button>
        </div>
      </div>

      <div className="results-container">
        <div className="summary-card">
          <h2>Общий результат</h2>
          <div className="candidate-info">
            <h3>{results.candidate_name}</h3>
            <div className="final-score">
              <span className="score-value">{results.final_score_percent}%</span>
              <span className={`verdict ${getVerdictClass(results.verdict)}`}>
                {results.verdict}
              </span>
            </div>
          </div>
        </div>

        <div className="breakdown-section">
          <h2>Детальная разбивка оценок</h2>
          
          {/* Hard Skills */}
          <div className="score-category">
            <h3>Технические навыки ({results.breakdown.hard_skills.score_percent}%)</h3>
            <div className="skills-details">
              {results.breakdown.hard_skills.details.map((skill, index) => (
                <div key={index} className="skill-item">
                  <div className="skill-header">
                    <span className="skill-name">{skill.skill}</span>
                    <span className="skill-score">{skill.score}</span>
                  </div>
                  <div className="skill-comment">{skill.comment}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Experience */}
          <div className="score-category">
            <h3>Опыт работы ({results.breakdown.experience.score_percent}%)</h3>
            <div className="experience-details">
              <p className="category-comment">{results.breakdown.experience.comment}</p>
              <div className="experience-scores">
                <div className="score-item">
                  <span>Продолжительность:</span>
                  <span>{results.breakdown.experience.scores.duration}%</span>
                </div>
                <div className="score-item">
                  <span>Релевантность:</span>
                  <span>{results.breakdown.experience.scores.relevance}%</span>
                </div>
                <div className="score-item">
                  <span>Функциональность:</span>
                  <span>{results.breakdown.experience.scores.functionality}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Soft Skills */}
          <div className="score-category">
            <h3>Поведенческие навыки ({results.breakdown.soft_skills.score_percent}%)</h3>
            <div className="soft-skills-details">
              <p className="category-comment">{results.breakdown.soft_skills.comment}</p>
              <div className="soft-skills-scores">
                <div className="score-item">
                  <span>STAR метод:</span>
                  <span>{results.breakdown.soft_skills.scores.star_method}%</span>
                </div>
                <div className="score-item">
                  <span>Мотивация:</span>
                  <span>{results.breakdown.soft_skills.scores.motivation}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="backend-info">
          <p>🔧 Backend в этот момент: запускает скоринг (ML-3), сохраняет отчёт в БД, обновляет Google Таблицу.</p>
        </div>
      </div>
    </div>
  );
};

export default ViewResults;
