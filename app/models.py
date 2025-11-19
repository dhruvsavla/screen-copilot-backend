# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    guides = relationship("Guide", back_populates="owner")

class Guide(Base):
    __tablename__ = "guides"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    shortcut = Column(String, index=True, unique=True, nullable=False)
    description = Column(Text, nullable=False) # <-- ADD THIS LINE
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="guides")
    steps = relationship("Step", back_populates="guide", cascade="all, delete-orphan")

class Step(Base):
    # ... (no changes in this class)
    __tablename__ = "steps"
    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer, nullable=False)
    selector = Column(Text, nullable=False)
    instruction = Column(Text, nullable=False)
    guide_id = Column(Integer, ForeignKey("guides.id"))

    guide = relationship("Guide", back_populates="steps")