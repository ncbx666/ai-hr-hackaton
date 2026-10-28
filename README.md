# AI-HR: автоматизированное собеседование

Хакатонный прототип системы, которая проводит первичное собеседование вместо
HR. Система разбирает резюме и вакансию, генерирует вопросы через LLM,
проводит голосовое интервью с кандидатом и выставляет итоговую оценку.
Результаты выгружаются в Google Sheets.

> Это код с хакатона (сентябрь 2025): в нём есть несколько вариантов сервера
> и экспериментальные скрипты. Ниже описано, что из этого основное.

## Как устроено

| Часть | Где | Что делает |
|---|---|---|
| Фронтенд | `frontend/` | React + TypeScript: кабинет HR (создание интервью, требования, результаты) и интерфейс кандидата (регистрация, голосовое интервью) |
| Бэкенд | `backend/api/main.py` | FastAPI на `:8000`: интервью, загрузка резюме и вакансий, результаты, выгрузка в Google Sheets |
| Голосовой канал | `backend/api/simple_websocket_server.py` | WebSocket на `:8001`, к нему подключается страница интервью |
| Речь | `backend/api/speech_service.py` | распознавание и синтез речи |
| Генерация вопросов | `ds1/` | вопросы по резюме и вакансии через Gemini, правила и системный промпт рядом |
| Разбор документов | `ds2/` | парсинг PDF резюме и вакансий, сборка транскрипта, классификаторы вопросов и ответов (`ds2/models/*.joblib`) |
| Оценка кандидата | `ds3/` | скоринг по hard/soft skills и опыту через Gemini |
| Telegram-бот | `backend/telegram_bot.go` | прототип бота на Go |
| Тестовые данные | `mocks/`, `backend/materials/` | примеры резюме и вакансий |

`backend/api/main_optimized.py` — облегчённая демо-версия бэкенда: быстро
стартует, но оценка в ней заглушка (всегда 85%), а загрузки файлов нет. Её
запускает `start_all.bat`.

## Состояние

- Полный бэкенд `main.py` запускается: загрузка файлов, создание интервью,
  результаты и WebSocket `/ws/interview/{id}` отвечают.
- Выгрузка в Google Sheets в `main.py` идёт через `google_sheets_service.py`,
  а он только **имитирует** таблицы (пишет в лог и возвращает фиктивную
  ссылку). Настоящая работа с gspread есть в `google_sheets.py`, но к серверу
  не подключена.
- Автоматическая обработка завершённых интервью (`interview_processor.py`)
  использует `ds2`/`ds3` и требует `sentence-transformers`, которого нет в
  `backend/requirements.txt`; без него обработка отключается с сообщением в
  консоли.
- Без ключей LLM вопросы генерируются из запасного набора.
- Автотестов нет, `backend/test_api.py` и `backend/system_test.py` — ручные
  скрипты против запущенного сервера.

## Настройка

Нужны Python 3.10+, Node.js 18+ и ключи:

- `GEMINI_API_KEY` / `GOOGLE_API_KEY` — генерация вопросов и оценка;
- `OPENAI_API_KEY` — если используются модели OpenAI;
- `GOOGLE_APPLICATION_CREDENTIALS` и `GOOGLE_SHEETS_CREDENTIALS` — путь к
  JSON сервисного аккаунта Google (речь и Sheets), `SPREADSHEET_ID` — таблица
  для результатов.

```bash
cp backend/.env.example backend/.env   # заполнить ключи
pip install -r backend/requirements.txt
cd frontend && npm install
```

Подробнее о получении ключей — в [backend/API_KEYS_SETUP.md](backend/API_KEYS_SETUP.md).
Файлы `.env` и `*credentials*.json` в `.gitignore`, не коммитьте их.

## Запуск

Три процесса:

```bash
cd backend/api && python main.py                     # API на :8000, документация на /docs
cd backend/api && python simple_websocket_server.py  # голосовой канал на :8001
cd frontend && npm start                             # интерфейс на :3000
```

На Windows `start_all.bat` запускает облегчённый `main_optimized.py` и
фронтенд — быстрее, но без загрузки файлов и с оценкой-заглушкой.

Отдельные модули:

```bash
python ds2/pdf_parser.py                 # PDF из mocks/ds2/{cv,vacansy} → JSON в mocks/ds2
python ds1/test_generate_questions.py    # генерация вопросов на примере (нужен GEMINI_API_KEY)
```

## Документация

- [RUNNING_INSTRUCTIONS.md](RUNNING_INSTRUCTIONS.md), [TESTING_GUIDE.md](TESTING_GUIDE.md) — запуск и проверка
- [ds1/INTEGRATION_INSTRUCTIONS.md](ds1/INTEGRATION_INSTRUCTIONS.md) — подключение генератора вопросов
- [backend/api/MONITORING_README.md](backend/api/MONITORING_README.md) — мониторинг выгрузки в Google Sheets
- [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) — что ускоряли в демо-версии
