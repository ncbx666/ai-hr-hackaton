import os
import json
import base64
import asyncio
from typing import Optional, Dict, Any
import tempfile
import io
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импорты для Google Cloud
try:
    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google Cloud libraries not available. Using mock services.")

# Импорты для ML моделей
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not available.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI library not available.")


class SpeechService:
    def __init__(self):
        self.stt_client = None
        self.tts_client = None
        
        if GOOGLE_AVAILABLE:
            try:
                # Проверяем наличие credentials файла
                credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "google-credentials.json")
                if os.path.exists(credentials_path):
                    # Инициализируем Google STT
                    self.stt_client = speech.SpeechClient()
                    
                    # Инициализируем Google TTS
                    self.tts_client = texttospeech.TextToSpeechClient()
                    
                    print("[SpeechService] Google services initialized")
                else:
                    print(f"[SpeechService] Google credentials file not found: {credentials_path}")
                    print("[SpeechService] Using mock services instead")
                    self.stt_client = None
                    self.tts_client = None
            except Exception as e:
                print(f"[SpeechService] Failed to initialize Google services: {e}")
                print("[SpeechService] Using mock services instead")
                self.stt_client = None
                self.tts_client = None
        
        # Настройка ML моделей
        self._setup_ml_models()
    
    def _setup_ml_models(self):
        """Настройка ML моделей для генерации вопросов"""
        # Настройка Google Cloud Generative Language API
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key and google_api_key != "your-google-cloud-api-key-here":
            try:
                if GEMINI_AVAILABLE:
                    genai.configure(api_key=google_api_key)
                    print("[SpeechService] Google Cloud Generative Language API configured")
            except Exception as e:
                print(f"[SpeechService] Error configuring Google Cloud API: {e}")
        
        # Альтернативный Gemini ключ из AI Studio
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your-gemini-api-key-here" and not google_api_key:
            try:
                if GEMINI_AVAILABLE:
                    genai.configure(api_key=gemini_key)
                    print("[SpeechService] Gemini AI Studio API configured")
            except Exception as e:
                print(f"[SpeechService] Error configuring Gemini API: {e}")
        
        # Настройка OpenAI как fallback
        if OPENAI_AVAILABLE:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and openai_key != "sk-your-openai-api-key-here":
                openai.api_key = openai_key
                print("[SpeechService] OpenAI configured as fallback")
            else:
                print("[SpeechService] OpenAI API key not provided or placeholder")
    
    async def transcribe_audio(self, audio_data: bytes, is_final: bool = False) -> str:
        """
        Транскрипция аудио в текст
        """
        if not self.stt_client:
            # Заглушка если Google STT недоступен
            return f"[MOCK STT] Обработано {len(audio_data)} байт аудио"
        
        try:
            # Конфигурация для STT
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="ru-RU",
                alternative_language_codes=["en-US"],
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
                model="latest_long"
            )
            
            # Создаем объект аудио
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Выполняем транскрипцию
            response = self.stt_client.recognize(config=config, audio=audio)
            
            # Извлекаем результат
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                print(f"[STT] Transcript: {transcript} (confidence: {confidence})")
                return transcript
            else:
                return ""
                
        except Exception as e:
            print(f"[STT] Error: {e}")
            return f"[STT ERROR] {str(e)}"
    
    async def generate_speech(self, text: str) -> bytes:
        """
        Генерация речи из текста
        """
        if not self.tts_client:
            # Заглушка если Google TTS недоступен
            return b"[MOCK TTS] Audio data for: " + text.encode()
        
        try:
            # Настройка синтеза речи
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="ru-RU",
                name="ru-RU-Standard-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Генерируем аудио
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, 
                voice=voice, 
                audio_config=audio_config
            )
            
            print(f"[TTS] Generated {len(response.audio_content)} bytes for: {text[:50]}...")
            return response.audio_content
            
        except Exception as e:
            print(f"[TTS] Error: {e}")
            return b""


class MLQuestionGenerator:
    """Класс для генерации вопросов с помощью ML моделей"""
    
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        # Приоритет: Google Cloud API > Gemini AI Studio > OpenAI
        self.google_cloud_available = (GEMINI_AVAILABLE and 
                                      google_api_key and 
                                      google_api_key != "your-google-cloud-api-key-here")
        
        self.gemini_available = (GEMINI_AVAILABLE and 
                                gemini_key and 
                                gemini_key != "your-gemini-api-key-here" and
                                not self.google_cloud_available)
        
        self.openai_available = (OPENAI_AVAILABLE and 
                                openai_key and 
                                openai_key != "sk-your-openai-api-key-here")
        
        if self.google_cloud_available or self.gemini_available:
            # Используем актуальную модель
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
        print(f"[MLQuestionGenerator] Google Cloud API available: {self.google_cloud_available}")
        print(f"[MLQuestionGenerator] Gemini AI Studio available: {self.gemini_available}")
        print(f"[MLQuestionGenerator] OpenAI available: {self.openai_available}")
    
    async def generate_question(
        self, 
        transcript: str, 
        question_number: int, 
        job_description: str = "",
        previous_questions: list = None
    ) -> str:
        """
        Генерация следующего вопроса на основе ответа кандидата
        """
        
        # Базовый промпт
        prompt = self._build_prompt(transcript, question_number, job_description, previous_questions or [])
        
        # Пробуем сначала Google Cloud/Gemini, потом OpenAI, потом заглушка
        if self.google_cloud_available or self.gemini_available:
            try:
                return await self._generate_with_gemini(prompt)
            except Exception as e:
                print(f"[Gemini] Error: {e}")
        
        if self.openai_available:
            try:
                return await self._generate_with_openai(prompt)
            except Exception as e:
                print(f"[OpenAI] Error: {e}")
        
        # Заглушка
        return self._generate_fallback_question(transcript, question_number)
    
    def _build_prompt(self, transcript: str, question_number: int, job_description: str, previous_questions: list) -> str:
        """Построение промпта для ML модели"""
        
        prompt = f"""Ты - опытный HR-специалист, проводящий собеседование.

Описание вакансии: {job_description}

Предыдущие вопросы: {previous_questions}

Последний ответ кандидата: "{transcript}"

Твоя задача - сгенерировать следующий уместный вопрос (номер {question_number}) для продолжения собеседования.

Правила:
1. Вопрос должен быть релевантен вакансии и ответу кандидата
2. Избегай повторения уже заданных вопросов
3. Вопрос должен быть конкретным и помогать оценить кандидата
4. Длина вопроса - не более 2 предложений
5. Используй профессиональный, но дружелюбный тон

Сгенерируй только сам вопрос, без дополнительных комментариев:"""

        return prompt
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Генерация вопроса с помощью Gemini"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.gemini_model.generate_content, prompt
            )
            question = response.text.strip()
            print(f"[Gemini] Generated question: {question}")
            return question
        except Exception as e:
            print(f"[Gemini] Generation error: {e}")
            raise
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Генерация вопроса с помощью OpenAI"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты опытный HR-специалист"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            question = response.choices[0].message.content.strip()
            print(f"[OpenAI] Generated question: {question}")
            return question
        except Exception as e:
            print(f"[OpenAI] Generation error: {e}")
            raise
    
    def _generate_fallback_question(self, transcript: str, question_number: int) -> str:
        """Заглушка для генерации вопроса"""
        
        fallback_questions = [
            "Расскажите подробнее о вашем опыте работы",
            "Какие технологии вы используете в своей работе?",
            "Как вы решаете сложные задачи?",
            "Расскажите о своих достижениях",
            "Что вас мотивирует в работе?",
            "Как вы работаете в команде?",
            "Какие у вас планы на развитие?",
            "Почему вас интересует эта позиция?"
        ]
        
        # Выбираем вопрос по номеру или случайно
        if question_number <= len(fallback_questions):
            question = fallback_questions[question_number - 1]
        else:
            import random
            question = random.choice(fallback_questions)
        
        print(f"[Fallback] Generated question {question_number}: {question}")
        return question


# Глобальные экземпляры сервисов
speech_service = SpeechService()
question_generator = MLQuestionGenerator()
