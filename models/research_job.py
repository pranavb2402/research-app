from sqlalchemy import Column,UUID,String,Float,DateTime,Enum
from models.question import Base

class ResearchJob(Base):

    __tablename__ = 'researchJob'


    id = Column(UUID, primary_key=True)
    question = Column(String)
    summary = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
