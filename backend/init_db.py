#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from db import Base, engine, SessionLocal, InterviewDB, ResumeDB

def init_database():
    """Инициализация базы данных"""
    print("Создаем таблицы в базе данных...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Таблицы успешно созданы!")
        
        # Проверяем подключение
        session = SessionLocal()
        interviews = session.query(InterviewDB).all()
        print(f"Найдено собеседований: {len(interviews)}")
        session.close()
        
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    init_database()
