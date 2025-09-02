# AI-HR Frontend

React приложение для AI-агента собеседований.

## Структура приложения

### HR Интерфейс (для работников HR)
- `/hr/dashboard` - Главная панель со списком собеседований
- `/hr/create` - Создание нового собеседования
- `/hr/results` - Просмотр результатов собеседования  
- `/hr/requirements/:id` - Просмотр загруженных файлов

### Интерфейс кандидата
- `/candidate/:sessionId/welcome` - Приветственная страница
- `/candidate/:sessionId/registration` - Регистрация кандидата
- `/candidate/:sessionId/waiting` - Подготовка к собеседованию
- `/candidate/:sessionId/interview` - Процесс собеседования (чат с AI)
- `/candidate/:sessionId/completion` - Завершение собеседования

## Основные компоненты

### Страницы HR:
- **HRDashboard** - список всех собеседований с фильтрацией
- **CreateInterview** - форма загрузки вакансии и резюме
- **ViewResults** - детальные результаты скоринга
- **ViewRequirements** - просмотр файлов вакансии/резюме

### Страницы кандидата:
- **Welcome** - приветствие и инструкции
- **Registration** - сбор данных кандидата
- **Waiting** - подготовка WebSocket соединения
- **Interview** - основной интерфейс чата с AI
- **Completion** - благодарность и следующие шаги

## Технологии

- **React 18** с TypeScript
- **React Router** для роутинга
- **CSS Modules** для стилизации  
- **WebSocket** для реального времени (в Interview)
- **Web Speech API** для голосового ввода

## Интеграции с Backend

### REST API:
```
GET /api/hr/interviews - список собеседований
POST /api/hr/interviews - создание собеседования
GET /api/hr/results/:id - результаты скоринга
GET /api/candidate/session/:id - данные сессии
POST /api/candidate/register - регистрация кандидата
```

### WebSocket:
```
/ws/interview/:sessionId - реалтайм чат для собеседования
```

### События WebSocket:
- `message_sent` - текст от кандидата
- `voice_input` - голос от кандидата  
- `ai_question` - вопрос от AI
- `interview_complete` - завершение

## Установка и запуск

```bash
# Установка зависимостей
npm install

# Запуск в dev режиме
npm start

# Сборка для продакшена
npm run build
```

## Файловая структура

```
src/
├── pages/
│   ├── hr/                 # Страницы для HR
│   │   ├── HRDashboard.tsx
│   │   ├── CreateInterview.tsx
│   │   ├── ViewResults.tsx
│   │   └── ViewRequirements.tsx
│   └── candidate/          # Страницы для кандидатов
│       ├── Welcome.tsx
│       ├── Registration.tsx
│       ├── Waiting.tsx
│       ├── Interview.tsx
│       └── Completion.tsx
├── components/             # Переиспользуемые компоненты
├── App.tsx                 # Главный роутер
└── index.tsx              # Точка входа
```

## Особенности реализации

### Interview компонент (самый сложный):
- Управление WebSocket соединением
- Обработка голосового ввода (Web Speech API)
- Переключение между текстом и голосом
- Прогресс собеседования
- Автоскролл сообщений

### Адаптивность:
- Все компоненты адаптированы под мобильные устройства
- Специальная оптимизация для голосового ввода на мобильных

### Интеграция с AI:
- Готова архитектура для подключения Gemini API
- Заглушки для Google Speech-to-Text
- Структура для реалтайм обработки

## Следующие этапы

1. Установка Node.js и зависимостей
2. Подключение к реальному Backend API
3. Интеграция голосовых API (Google Speech)
4. Тестирование пользовательских сценариев
5. Оптимизация производительности

## Демо данные

Все компоненты используют mock-данные для демонстрации функционала:
- Список собеседований с разными статусами
- Результаты скоринга из `ds3/score_sample.json`
- Примеры файлов вакансий и резюме
