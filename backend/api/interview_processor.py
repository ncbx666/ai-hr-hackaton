"""
Модуль для автоматической обработки интервью:
- Создание транскрипта (ds2)
- Автоматический скоринг (ds3)
- Интеграция с WebSocket
"""

import json
import tempfile
import subprocess
import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Optional
import os
from pathlib import Path

# Добавляем пути к ds модулям
sys.path.append(str(Path(__file__).parent.parent.parent / "ds2"))
sys.path.append(str(Path(__file__).parent.parent.parent / "ds3"))

try:
    from create_transcript import generate_transcript, classify_answer
    from score_candidate import ScoringModelGemini
    DS_MODULES_AVAILABLE = True
    print("[InterviewProcessor] DS модули подключены")
except ImportError as e:
    print(f"[InterviewProcessor] DS модули недоступны: {e}")
    DS_MODULES_AVAILABLE = False

class TranscriptProcessor:
    """Класс для создания и обработки транскриптов интервью используя ds2"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        
    def create_transcript(self, session_data: Dict) -> Dict:
        """Создает транскрипт из данных сессии интервью используя ds2/create_transcript.py"""
        
        # Используем реальный модуль ds2 если доступен
        if DS_MODULES_AVAILABLE:
            try:
                return self._create_transcript_with_ds2(session_data)
            except Exception as e:
                print(f"[TranscriptProcessor] Ошибка ds2: {e}")
                return self._create_simple_transcript(session_data)
        else:
            return self._create_simple_transcript(session_data)
    
    def _create_transcript_with_ds2(self, session_data: Dict) -> Dict:
        """Создание транскрипта через ds2 модуль"""
        
        candidate_name = session_data.get("candidate_name", "Unknown")
        questions = session_data.get("questions", [])
        answers = session_data.get("answers", [])
        job_description = session_data.get("job_description", "")
        
        # Формируем vacancy_info и resume_info для ds2
        vacancy_info = {
            "position": session_data.get("position", ""),
            "key_duties_and_skills": [job_description]
        }
        
        resume_info = {
            "candidate_name": candidate_name
        }
        
        # Создаем dialogue_parts
        dialogue_parts = []
        for i, (question, answer) in enumerate(zip(questions, answers)):
            # Классифицируем ответ
            assessment_category = classify_answer(answer, vacancy_info) if answer else "hard_skill"
            skill_assessed = f"навык_{i+1}"
            
            dialogue_parts.append({
                "question": question,
                "answer": answer,
                "assessment_category": assessment_category,
                "skill_assessed": skill_assessed
            })
        
        # Формируем финальный транскрипт
        transcript = {
            "candidate_name": candidate_name,
            "interview_date": datetime.now().isoformat(),
            "vacancy_info": vacancy_info,
            "resume_info": resume_info,
            "dialogue_parts": dialogue_parts,
            "experience_question_answer": answers[0] if answers else ""
        }
        
        return transcript
    
    def _create_simple_transcript(self, session_data: Dict) -> Dict:
        """Простое создание транскрипта без ds2"""
        
        candidate_name = session_data.get("candidate_name", "Unknown")
        questions = session_data.get("questions", [])
        answers = session_data.get("answers", [])
        
        # Создаем базовый транскрипт
        transcript = {
            "candidate_name": candidate_name,
            "interview_date": datetime.now().isoformat(),
            "position": session_data.get("position", session_data.get("job_description", "Unknown")),
            "dialogue_parts": []
        }
        
        # Определяем навыки для оценки (можно настроить)
        skills_to_assess = [
            "техническая компетентность",
            "коммуникативные навыки", 
            "опыт работы",
            "решение проблем",
            "работа в команде"
        ]
        
        dialogue_parts = []
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
    """Класс для автоматического скоринга используя ds3/score_candidate.py"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.weights = {"hard_skills": 0.5, "experience": 0.3, "soft_skills": 0.2}
        self.scorer = None
        
        # Загружаем промпты для скоринга
        if DS_MODULES_AVAILABLE:
            try:
                prompt_path = self.base_path / "ds3" / "scoring_prompt.md"
                exp_prompt_path = self.base_path / "ds3" / "experience_prompt.md"
                
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    scoring_prompt = f.read()
                with open(exp_prompt_path, 'r', encoding='utf-8') as f:
                    experience_prompt = f.read()
                
                prompts = {"scoring": scoring_prompt, "experience": experience_prompt}
                self.scorer = ScoringModelGemini(prompts=prompts, weights=self.weights)
                print("[AutoScoringProcessor] ds3 scorer инициализирован")
                
            except Exception as e:
                print(f"[AutoScoringProcessor] Ошибка инициализации ds3: {e}")
    
    async def run_scoring(self, transcript_data: Dict, session_id: str) -> Dict:
        """Запускает автоматический скоринг для транскрипта используя ds3"""
        try:
            print(f"[AutoScoringProcessor] Запуск скоринга для сессии {session_id}")
            
            # Используем ds3 модуль если доступен
            if DS_MODULES_AVAILABLE and self.scorer:
                try:
                    score_result = self.scorer.score(transcript_data)
                    print(f"[AutoScoringProcessor] ds3 скоринг завершен")
                except Exception as e:
                    print(f"[AutoScoringProcessor] Ошибка ds3 скоринга: {e}")
                    score_result = self._create_fallback_score(transcript_data)
            else:
                score_result = self._create_fallback_score(transcript_data)
            
            # Сохраняем результат скоринга
            score_path = await self._save_score_result(score_result, session_id)
            
            # Записываем результат в Google Sheets
            try:
                from google_sheets_service import google_sheets_service
                await google_sheets_service.update_interview_results(
                    interview_id=session_id,
                    results_data=score_result
                )
                print("[AutoScoringProcessor] Результат записан в Google Sheets")
            except Exception as e:
                print(f"[AutoScoringProcessor] Ошибка записи в Google Sheets: {e}")
            
            return {
                "success": True,
                "score_data": score_result,
                "score_path": score_path
            }
            
        except Exception as e:
            error_msg = f"Ошибка автоматического скоринга: {e}"
            print(f"[AutoScoringProcessor] {error_msg}")
            return {"error": error_msg}
    
    def _create_fallback_score(self, transcript_data: Dict) -> Dict:
        """Создает базовый скоринг если ds3 недоступен"""
        return {
            "candidate_name": transcript_data.get("candidate_name", "Unknown"),
            "final_score_percent": 75.0,
            "verdict": "Fallback оценка - требуется ручная проверка",
            "breakdown": {
                "hard_skills": {"score_percent": 70.0, "details": ["Автоматическая оценка недоступна"]},
                "soft_skills": {"score_percent": 80.0, "details": ["Автоматическая оценка недоступна"]},
                "experience": {"score_percent": 75.0, "details": ["Автоматическая оценка недоступна"]}
            }
        }
    
    async def _save_score_result(self, score_data: Dict, session_id: str) -> str:
        """Сохраняет результат скоринга в файл"""
        try:
            # Создаем папку для результатов если не существует
            score_dir = Path("uploads/scores")
            score_dir.mkdir(parents=True, exist_ok=True)
            
            # Создаем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"score_{session_id}_{timestamp}.json"
            filepath = score_dir / filename
            
            # Сохраняем результат
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(score_data, f, ensure_ascii=False, indent=2)
            
            print(f"[AutoScoringProcessor] Результат скоринга сохранен: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[AutoScoringProcessor] Ошибка сохранения результата: {e}")
            raise

class InterviewAutoProcessor:
    """Класс для полной автоматической обработки завершенного интервью"""
    
    def __init__(self):
        self.transcript_processor = TranscriptProcessor()
        self.scoring_processor = AutoScoringProcessor()
        print("[InterviewAutoProcessor] Инициализирован")
    
    async def process_completed_interview(self, interview_session):
        """
        Полная обработка завершенного интервью:
        1. Создание транскрипта
        2. Автоматический скоринг с ds3
        3. Запись в Google Sheets
        4. Возврат результатов
        """
        try:
            session_id = interview_session.session_id
            print(f"[InterviewAutoProcessor] Начинаю обработку интервью {session_id}")
            
            # Подготавливаем данные сессии для обработки
            session_data = {
                "session_id": session_id,
                "candidate_name": interview_session.candidate_name,
                "position": interview_session.job_description,
                "questions": interview_session.previous_questions,
                "answers": interview_session.candidate_answers,
                "transcript_buffer": interview_session.transcript_buffer,
                "start_time": interview_session.interview_start_time.isoformat() if interview_session.interview_start_time else None,
                "end_time": interview_session.interview_end_time.isoformat() if interview_session.interview_end_time else None
            }
            
            # Шаг 1: Создаем транскрипт используя ds2
            transcript_data = self.transcript_processor.create_transcript(session_data)
            transcript_path = await self.transcript_processor.save_transcript(
                transcript_data, 
                session_id
            )
            
            # Шаг 2: Запускаем автоматический скоринг используя ds3
            scoring_result = await self.scoring_processor.run_scoring(
                transcript_data,  # Передаем данные напрямую
                session_id
            )
            
            # Шаг 3: Записываем результат в Google Sheets
            try:
                from google_sheets_service import google_sheets_service
                if scoring_result.get("success") and scoring_result.get("score_data"):
                    await google_sheets_service.update_interview_results(
                        interview_id=session_id,
                        results_data=scoring_result["score_data"]
                    )
                    print(f"[InterviewAutoProcessor] Результат записан в Google Sheets для {session_id}")
            except Exception as e:
                print(f"[InterviewAutoProcessor] Ошибка записи в Google Sheets: {e}")
            
            # Шаг 4: Формируем итоговый результат
            result = {
                "session_id": session_id,
                "status": "completed",
                "success": scoring_result.get("success", False),
                "transcript_path": transcript_path,
                "transcript_data": transcript_data,
                "score_data": scoring_result.get("score_data", {}),
                "scoring_result": scoring_result,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"[InterviewAutoProcessor] Обработка завершена для {session_id}")
            return result
            
        except Exception as e:
            error_msg = f"Ошибка автоматической обработки: {e}"
            print(f"[InterviewAutoProcessor] {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                "session_id": getattr(interview_session, 'session_id', 'unknown'),
                "status": "error",
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

# Глобальные экземпляры процессоров
auto_processor = InterviewAutoProcessor()
