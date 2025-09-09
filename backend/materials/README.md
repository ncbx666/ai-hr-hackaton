# Тестовые материалы для AI-HR системы

Эта папка содержит тестовые файлы для проверки работы системы собеседований.

## Описания вакансий (Job Descriptions)

### Frontend позиции:
- `job_description_frontend.txt` - Senior Frontend Developer (React)
  - Требует опыт React 3+ года
  - TypeScript, Redux, тестирование
  - Зарплата: 200-300k руб/месяц

### Backend позиции:
- `job_description_backend.txt` - Middle Backend Developer (Python)
  - Python, Django/FastAPI
  - PostgreSQL, Docker
  - Зарплата: 150-220k руб/месяц

### DevOps позиции:
- `job_description_devops.txt` - Middle DevOps Engineer
  - Kubernetes, AWS, CI/CD
  - Terraform, Ansible
  - Зарплата: 180-250k руб/месяц

## Резюме кандидатов (Resumes)

### Frontend разработчики:
- `resume_frontend_senior.txt` - Петров Алексей (Senior)
  - 5+ лет опыта
  - React, TypeScript, Redux
  - Опыт менторинга и лидерства

- `resume_frontend_junior.txt` - Козлов Дмитрий (Junior/Middle)
  - 2+ года опыта
  - React, JavaScript, стремление к росту
  - Активно изучает новые технологии

### Backend разработчики:
- `resume_backend_middle.txt` - Иванова Мария (Middle)
  - 3+ года опыта Python
  - FastAPI, Django, PostgreSQL
  - AWS сертификация

### DevOps инженеры:
- `resume_devops_middle.txt` - Сидоров Павел (Middle)
  - 4+ года опыта
  - Kubernetes, AWS, Terraform
  - Сертификаты AWS и CKA

## Сценарии тестирования

### Идеальные пары (High Match):
1. `job_description_frontend.txt` + `resume_frontend_senior.txt`
   - Ожидаемый результат: 85-95% соответствия
   - Senior кандидат на Senior позицию

2. `job_description_backend.txt` + `resume_backend_middle.txt`
   - Ожидаемый результат: 80-90% соответствия
   - Middle кандидат на Middle позицию

### Частичные совпадения (Medium Match):
1. `job_description_frontend.txt` + `resume_frontend_junior.txt`
   - Ожидаемый результат: 60-75% соответствия
   - Junior кандидат на Senior позицию (недостаток опыта)

### Несоответствие (Low Match):
1. `job_description_devops.txt` + `resume_frontend_senior.txt`
   - Ожидаемый результат: 20-40% соответствия
   - Frontend разработчик на DevOps позицию

## Использование

Эти файлы можно использовать для:
1. Тестирования системы создания собеседований
2. Проверки алгоритмов matching'а
3. Тестирования ML моделей оценки кандидатов
4. Отладки Google Sheets интеграции

## Примеры вопросов для собеседований

### Frontend (React):
- Расскажите о разнице между useState и useEffect
- Как бы вы оптимизировали производительность React приложения?
- Опишите ваш подход к state management в крупных приложениях

### Backend (Python):
- Объясните разницу между синхронным и асинхронным программированием
- Как бы вы спроектировали RESTful API для e-commerce системы?
- Расскажите о вашем опыте оптимизации запросов к базе данных

### DevOps:
- Опишите процесс настройки CI/CD пайплайна
- Как бы вы обеспечили масштабируемость приложения в Kubernetes?
- Расскажите о вашем подходе к мониторингу инфраструктуры
