from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, UUID, String, Enum
from schemas.question import QuestionStatus

Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'

    id = Column(UUID, primary_key=True, index=True)
    question = Column(String)
    status= Column(
        Enum(QuestionStatus, values_callable=lambda e: [m.value for m in e]),
        default=QuestionStatus.PENDING,
    )
    error_type = Column(String, nullable=True)
    error_description = Column(String, nullable=True)