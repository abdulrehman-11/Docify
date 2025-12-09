from sqlalchemy import Column, Integer, String
from database import Base
from models.base import TimestampMixin

class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    insurance_provider = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', email='{self.email}')>"
