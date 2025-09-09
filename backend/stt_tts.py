# Заглушка для Google Speech-to-Text API
def transcribe_audio(audio_data: bytes) -> str:
    """
    Преобразует аудио в текст с помощью Google STT
    """
    print(f"[MOCK] STT: Получено {len(audio_data)} байт аудио")
    return "Тестовый транскрипт аудио"

def synthesize_speech(text: str) -> bytes:
    """
    Преобразует текст в речь с помощью Google TTS
    """
    print(f"[MOCK] TTS: Синтез речи для текста: {text}")
    return b"mock_audio_data"
