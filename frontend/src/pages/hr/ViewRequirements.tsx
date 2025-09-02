import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './ViewRequirements.css';

interface RequirementFile {
  id: string;
  name: string;
  type: 'vacancy' | 'resume';
  content: string;
  uploadedAt: string;
}

const ViewRequirements: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [files, setFiles] = useState<RequirementFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RequirementFile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Имитация загрузки файлов из БД
    const mockFiles: RequirementFile[] = [
      {
        id: '1',
        name: 'Описание_вакансии_Frontend.pdf',
        type: 'vacancy',
        content: `ВАКАНСИЯ: Frontend Developer

Описание позиции:
Мы ищем опытного Frontend разработчика для работы над веб-приложениями банка.

Обязанности:
• Разработка и поддержка пользовательских интерфейсов
• Работа с React, TypeScript, Redux
• Интеграция с REST API
• Написание unit-тестов
• Участие в code review

Требования:
• Опыт работы от 3 лет
• Отличное знание JavaScript, TypeScript
• Опыт работы с React (от 2 лет)
• Знание CSS препроцессоров (SASS/SCSS)
• Опыт работы с Git
• Понимание принципов UX/UI

Будет плюсом:
• Опыт работы в финтехе
• Знание Node.js
• Опыт с микрофронтендами`,
        uploadedAt: '2025-09-01'
      },
      {
        id: '2',
        name: 'Резюме_Иванов_Иван.pdf',
        type: 'resume',
        content: `РЕЗЮМЕ

Иванов Иван Петрович
Frontend Developer

Контакты:
Email: ivanov@example.com
Телефон: +7 (999) 123-45-67

Опыт работы:
2021-2025 - ООО "ТехноСофт"
Frontend Developer
• Разработка SPA на React
• Работа с TypeScript, Redux Toolkit
• Интеграция с REST API
• Покрытие кода тестами (Jest, RTL)

2019-2021 - ИП "ВебСтудия"
Junior Frontend Developer  
• Верстка адаптивных макетов
• Разработка на vanilla JavaScript
• Работа с jQuery, Bootstrap

Навыки:
• JavaScript, TypeScript
• React, Redux, Next.js
• HTML5, CSS3, SASS
• Git, Webpack, Vite
• Jest, React Testing Library

Образование:
2015-2019 - МГУ, Факультет ВМК
Бакалавр по направлению "Прикладная математика и информатика"`,
        uploadedAt: '2025-09-01'
      }
    ];

    setTimeout(() => {
      setFiles(mockFiles);
      setSelectedFile(mockFiles[0]);
      setLoading(false);
    }, 1000);
  }, [id]);

  if (loading) {
    return (
      <div className="view-requirements">
        <div className="loading">Загрузка файлов...</div>
      </div>
    );
  }

  return (
    <div className="view-requirements">
      <div className="header">
        <h1>Просмотр требований</h1>
        <button 
          onClick={() => window.location.href = '/hr/dashboard'}
          className="back-btn"
        >
          ← Назад к панели
        </button>
      </div>

      <div className="requirements-container">
        <div className="files-sidebar">
          <h3>Загруженные файлы</h3>
          <div className="files-list">
            {files.map((file) => (
              <div 
                key={file.id}
                className={`file-item ${selectedFile?.id === file.id ? 'active' : ''}`}
                onClick={() => setSelectedFile(file)}
              >
                <div className="file-icon">
                  {file.type === 'vacancy' ? '📋' : '👤'}
                </div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-type">
                    {file.type === 'vacancy' ? 'Вакансия' : 'Резюме'}
                  </div>
                  <div className="file-date">{file.uploadedAt}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="file-viewer">
          {selectedFile ? (
            <div className="file-content">
              <div className="file-header">
                <h2>{selectedFile.name}</h2>
                <span className="file-type-badge">
                  {selectedFile.type === 'vacancy' ? 'Описание вакансии' : 'Резюме кандидата'}
                </span>
              </div>
              <div className="file-text">
                <pre>{selectedFile.content}</pre>
              </div>
            </div>
          ) : (
            <div className="no-file-selected">
              <p>Выберите файл для просмотра</p>
            </div>
          )}
        </div>
      </div>

      <div className="backend-info">
        <p>🔧 Backend находит файл в БД и отдаёт его для просмотра.</p>
      </div>
    </div>
  );
};

export default ViewRequirements;
