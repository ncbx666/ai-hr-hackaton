#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram PDF Parser
Модуль для извлечения телеграм аккаунта из PDF резюме
"""

import sys
import json
import argparse
import re
from pathlib import Path
import pdfplumber

def extract_telegram_from_pdf(pdf_path: str) -> dict:
    """
    Извлекает телеграм аккаунт из PDF резюме
    
    Args:
        pdf_path (str): Путь к PDF файлу резюме
        
    Returns:
        dict: Словарь с телеграм аккаунтом в формате {"telegram": "username"} или {"error": "сообщение"}
    """
    try:
        # Проверяем существование файла
        if not Path(pdf_path).exists():
            return {"error": f"Файл {pdf_path} не найден"}
        
        # Извлекаем текст из PDF
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        # Ищем телеграм аккаунт по различным паттернам
        # Паттерны для поиска телеграм аккаунта
        patterns = [
            r'telegram[:\s]*@([a-zA-Z0-9_]+)',
            r'tg[:\s]*@([a-zA-Z0-9_]+)',
            r'@([a-zA-Z0-9_]+)',
            r'telegram[:\s]*([a-zA-Z0-9_]{5,32})',
            r'tg[:\s]*([a-zA-Z0-9_]{5,32})'
        ]
        
        telegram_username = None
        
        # Пробуем каждый паттерн
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                username = match.group(1)
                # Проверяем, что это похоже на телеграм аккаунт (не слишком короткое и не число)
                if len(username) >= 5 and not username.isdigit():
                    telegram_username = username
                    break
        
        # Если не нашли по паттернам, ищем просто @username
        if not telegram_username:
            at_matches = re.findall(r'@([a-zA-Z0-9_]{5,32})', text)
            for match in at_matches:
                if len(match) >= 5 and not match.isdigit():
                    telegram_username = match
                    break
        
        if telegram_username:
            return {"telegram": telegram_username}
        else:
            # Если телеграм не найден, возвращаем пустой словарь
            return {}
            
    except Exception as e:
        return {"error": f"Ошибка при обработке файла: {str(e)}"}

def main():
    """Основная функция для запуска из командной строки"""
    parser = argparse.ArgumentParser(description='Извлечение телеграм аккаунта из PDF резюме')
    parser.add_argument('pdf_path', help='Путь к PDF файлу резюме')
    
    args = parser.parse_args()
    
    # Извлекаем телеграм аккаунт
    result = extract_telegram_from_pdf(args.pdf_path)
    
    # Выводим результат в формате JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
