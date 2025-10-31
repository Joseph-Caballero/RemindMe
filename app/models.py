from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Reminder(Base):
    __tablename__ = "reminders" 

    id: Mapped[int] = mapped_column(primary_key=True)         
    title: Mapped[str] = mapped_column(String(100), nullable=False)   
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False) 
    sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)     
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (Index("reminders_due_at", "due_at"),)