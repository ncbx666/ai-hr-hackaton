# Инструкция по получению API ключей для AI-HR системы

## Google Cloud Speech-to-Text и Text-to-Speech

### 1. Создание проекта в Google Cloud
1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите следующие API:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API

### 2. Создание Service Account
1. Перейдите в IAM & Admin → Service Accounts
2. Нажмите "Create Service Account"
3. Дайте имя: `ai-hr-service-account`
4. Назначьте роли:
   - Speech Client
   - Cloud Speech Service Agent
5. Создайте и скачайте JSON ключ
6. Сохраните файл как `google-credentials.json` в папке backend

### 3. Настройка переменных окружения
```bash
# В файле .env
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

## OpenAI API

### 1. Получение ключа
1. Перейдите на [OpenAI Platform](https://platform.openai.com/)
2. Зарегистрируйтесь или войдите в аккаунт
3. Перейдите в Account → API Keys
4. Нажмите "Create new secret key"
5. Скопируйте ключ (он показывается только один раз!)

### 2. Настройка
```bash
# В файле .env
OPENAI_API_KEY=sk-proj-ваш-ключ-здесь
```

**Важно:** У OpenAI есть бесплатный tier с ограничениями. Для продакшн может потребоваться оплата.

## Google Gemini API

### 1. Получение ключа
1. Перейдите на [Google AI Studio](https://makersuite.google.com/)
2. Войдите с Google аккаунтом
3. Нажмите "Get API Key"
4. Создайте новый ключ или используйте существующий
5. Скопируйте ключ

### 2. Настройка
```bash
# В файле .env
GEMINI_API_KEY=ваш-gemini-ключ-здесь
```

**Важно:** Gemini имеет щедрый бесплатный tier, подходящий для разработки.

## PostgreSQL Database

### 1. Локальная установка
```bash
# Windows (через winget)
winget install PostgreSQL.PostgreSQL

# macOS (через Homebrew)
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

### 2. Создание базы данных
```sql
# Подключитесь к PostgreSQL
psql -U postgres

# Создайте базу данных
CREATE DATABASE ai_hr_hackaton;

# Создайте пользователя (опционально)
CREATE USER ai_hr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_hr_hackaton TO ai_hr_user;
```

### 3. Настройка
```bash
# В файле .env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_hr_hackaton
```

## Google Sheets API (опционально)

### 1. Настройка проекта
1. В том же Google Cloud проекте включите Google Sheets API
2. Используйте тот же Service Account что и для Speech API
3. Создайте Google Sheets документ
4. Поделитесь документом с email Service Account

### 2. Настройка
```bash
# В файле .env
GOOGLE_SHEETS_CREDENTIALS=google-credentials.json
SPREADSHEET_ID=1abc123def456ghi789jkl
```

## Проверка настройки

После настройки всех ключей запустите backend:

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

В логах должны появиться сообщения:
```
[SpeechService] Google services initialized
[SpeechService] OpenAI configured  
[SpeechService] Gemini configured
[MLQuestionGenerator] OpenAI available: True
[MLQuestionGenerator] Gemini available: True
```

## Стоимость использования

### Бесплатные лимиты:
- **Google Speech-to-Text**: 60 минут в месяц
- **Google Text-to-Speech**: 1 миллион символов в месяц  
- **OpenAI GPT-3.5**: $5 бесплатных кредитов
- **Google Gemini**: 15 запросов в минуту, 100 запросов в день

### Примерная стоимость для 100 интервью в месяц:
- Google STT/TTS: ~$2-5
- OpenAI GPT-3.5: ~$1-3
- Gemini: Бесплатно в рамках лимитов

## Безопасность

1. **Никогда не коммитьте .env файл в git**
2. **Используйте разные ключи для разработки и продакшн**
3. **Регулярно ротируйте API ключи**
4. **Ограничьте права Service Account минимально необходимыми**

## Troubleshooting

### Google Cloud ошибки:
- Проверьте что API включены в проекте
- Убедитесь что JSON файл credentials корректный
- Проверьте права Service Account

### OpenAI ошибки:
- Проверьте баланс аккаунта
- Убедитесь что ключ активен
- Проверьте rate limits

### Database ошибки:
- Убедитесь что PostgreSQL запущен
- Проверьте строку подключения
- Проверьте права пользователя БД
