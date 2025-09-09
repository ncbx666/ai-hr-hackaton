from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# URL базы данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./ai_hr_hackaton.db')

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

class InterviewDB(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    position = Column(String)
    experience_level = Column(String)
    status = Column(String, default="created")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    total_score = Column(Float)
    transcript = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ResumeDB(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(Text)
    analysis = Column(Text)
    skills = Column(Text)
    experience_years = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)
