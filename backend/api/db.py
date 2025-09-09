from sqlalchemy import create_engine, Column, String, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/aihr"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InterviewDB(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, index=True)
    position = Column(String, index=True)
    job_description = Column(Text)
    status = Column(String)
    results_url = Column(String)
    resumes = relationship("ResumeDB", back_populates="interview")

class ResumeDB(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    url = Column(String)
    interview_id = Column(String, ForeignKey("interviews.id"))
    interview = relationship("InterviewDB", back_populates="resumes")

# Для создания таблиц
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
