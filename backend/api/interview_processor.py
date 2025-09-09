"""
Модуль для автоматической обработки интервью:
- Создание транскрипта
- Автоматический скоринг
- Интеграция с WebSocket
"""

import json
import tempfile
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import os
from pathlib import Path

class TranscriptProcessor:
    """Класс для создания и обработки транскриптов интервью"""
    
    def __init__(self):
        self.transcript_template = {
            "candidate_name": "",
            "interview_date": "",
            "position": "",
            "dialogue_parts": []
        }
    
    def create_transcript(self, session_data: Dict) -> Dict:
        """Создает транскрипт из данных сессии интервью"""
        transcript = self.transcript_template.copy()
        
        # Заполняем основные данные
        transcript["candidate_name"] = session_data.get("candidate_name", "Unknown")
        transcript["interview_date"] = datetime.now().isoformat()
        transcript["position"] = session_data.get("position", session_data.get("job_description", "Unknown"))
        
        # Обрабатываем диалог
        dialogue_parts = []
        questions = session_data.get("questions", [])
        answers = session_data.get("answers", [])
        
        # Определяем навыки для оценки (можно настроить)
        skills_to_assess = [
            "техническая компетентность",
            "коммуникативные навыки", 
            "опыт работы",
            "решение проблем",
            "работа в команде"
        ]
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            # Определяем тип навыка для каждого вопроса
            skill_assessed = skills_to_assess[i % len(skills_to_assess)]
            assessment_category = "hard_skill" if i % 2 == 0 else "soft_skill"
            
            dialogue_part = {
                "question": question,
                "answer": answer,
                "skill_assessed": skill_assessed,
                "assessment_category": assessment_category
            }
            dialogue_parts.append(dialogue_part)
        
        transcript["dialogue_parts"] = dialogue_parts
        return transcript
    
    async def save_transcript(self, transcript_data: Dict, session_id: str) -> str:
        """Сохраняет транскрипт в файл"""
        try:
            # Создаем папку для транскриптов если не существует
            transcript_dir = Path("uploads/transcripts")
            transcript_dir.mkdir(parents=True, exist_ok=True)
            
            # Создаем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{session_id}_{timestamp}.json"
            filepath = transcript_dir / filename
            
            # Сохраняем транскрипт
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            print(f"[TranscriptProcessor] Транскрипт сохранен: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[TranscriptProcessor] Ошибка сохранения транскрипта: {e}")
            raise

class AutoScoringProcessor:
    """Класс для автоматического скоринга после создания транскрипта"""
    
    def __init__(self):
        self.ds3_script_path = "../../ds3/score_candidate.py"
    
    async def run_scoring(self, transcript_path: str, session_id: str) -> Dict:
        """Запускает автоматический скоринг для транскрипта"""
        try:
            # Создаем путь для результата скоринга
            output_path = transcript_path.replace(".json", "_score.json")
            
            print(f"[AutoScoringProcessor] Запуск скоринга для {transcript_path}")
            
            # Запускаем скрипт скоринга
            result = await asyncio.create_subprocess_exec(
                "python", self.ds3_script_path, transcript_path, output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                error_msg = f"Ошибка скоринга: {stderr.decode()}"
                print(f"[AutoScoringProcessor] {error_msg}")
                return {"error": error_msg, "details": stderr.decode()}
            
            # Читаем результат скоринга
            with open(output_path, 'r', encoding='utf-8') as f:
                score_data = json.load(f)
            
            print(f"[AutoScoringProcessor] Скоринг завершен: {output_path}")
            
            # Записываем результат в Google Sheets (если доступно)
            try:
                from google_sheets import write_result_to_sheet
                write_result_to_sheet(score_data)
                print("[AutoScoringProcessor] Результат записан в Google Sheets")
            except Exception as e:
                print(f"[AutoScoringProcessor] Ошибка записи в Google Sheets: {e}")
            
            return score_data
            
        except Exception as e:
            error_msg = f"Критическая ошибка скоринга: {e}"
            print(f"[AutoScoringProcessor] {error_msg}")
            return {"error": error_msg}

class InterviewAutoProcessor:
    """Главный класс для автоматической обработки интервью"""
    
    def __init__(self):
        self.transcript_processor = TranscriptProcessor()
        self.scoring_processor = AutoScoringProcessor()
    
    async def process_completed_interview(self, session: 'InterviewSession') -> Dict:
        """
        Полная обработка завершенного интервью:
        1. Создание транскрипта
        2. Автоматический скоринг
        3. Возврат результатов
        """
        try:
            print(f"[InterviewAutoProcessor] Начинаю обработку интервью {session.session_id}")
            
            # Шаг 1: Создаем данные сессии для транскрипта
            session_data = {
                "candidate_name": getattr(session, 'candidate_name', 'Unknown'),
                "position": session.job_description,
                "questions": session.previous_questions,
                "answers": session.transcript_buffer.split('\n') if hasattr(session, 'transcript_buffer') else []
            }
            
            # Шаг 2: Создаем транскрипт
            transcript_data = self.transcript_processor.create_transcript(session_data)
            transcript_path = await self.transcript_processor.save_transcript(
                transcript_data, 
                session.session_id
            )
            
            # Шаг 3: Запускаем автоматический скоринг
            scoring_result = await self.scoring_processor.run_scoring(
                transcript_path, 
                session.session_id
            )
            
            # Шаг 4: Формируем итоговый результат
            result = {
                "session_id": session.session_id,
                "status": "completed",
                "transcript_path": transcript_path,
                "transcript_data": transcript_data,
                "scoring_result": scoring_result,
                "processed_at": datetime.now().isoformat()
            }
            
            print(f"[InterviewAutoProcessor] Обработка завершена для {session.session_id}")
            return result
            
        except Exception as e:
            error_msg = f"Ошибка автоматической обработки интервью: {e}"
            print(f"[InterviewAutoProcessor] {error_msg}")
            return {
                "session_id": session.session_id,
                "status": "error",
                "error": error_msg,
                "processed_at": datetime.now().isoformat()
            }

# Глобальный экземпляр процессора
auto_processor = InterviewAutoProcessor()
