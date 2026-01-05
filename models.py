from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    comics = relationship("Comic", back_populates="owner")

class Publisher(Base):
    __tablename__ = "publisher"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    comics = relationship("Comic", back_populates="publisher")

class Grade(Base):
    __tablename__ = "grade"
    id = Column(Integer, primary_key=True)
    abbreviation = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    comment = Column(String)

    comics = relationship("Comic", back_populates="grade")

class Comic(Base):
    __tablename__ = "comic"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    issue_number = Column(String, nullable=False)
    publisher_id = Column(Integer, ForeignKey("publisher.id"), nullable=True)
    grade_id = Column(Integer, ForeignKey("grade.id"), nullable=True)
    cover_image_url = Column(String)
    buy_price = Column(Float)
    current_value = Column(Float)
    sell_price = Column(Float)
    created_at = Column(DateTime, default=DateTime.utcnow, nullable=False)  # ← ADD THIS

    owner = relationship("User", back_populates="comics")
    publisher = relationship("Publisher", back_populates="comics")
    grade = relationship("Grade", back_populates="comics")