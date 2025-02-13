from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), unique=True, index=True, nullable=False)
    answer = Column(String(1000), nullable=False)

    __table_args__ = (UniqueConstraint("question", name="uq_faq_question"),)
