from pydantic import BaseModel
from typing import Optional

class PublisherBase(BaseModel):
    name: str

class Publisher(PublisherBase):
    id: int

    class Config:
        from_attributes = True

class GradeBase(BaseModel):
    abbreviation: str
    name: str
    value: float

class Grade(GradeBase):
    id: int

    class Config:
        from_attributes = True

class ComicBase(BaseModel):
    title: str
    issue_number: str
    buy_price: Optional[float] = None
    current_value: Optional[float] = None
    sell_price: Optional[float] = None
    cover_image_url: Optional[str] = None

class ComicCreate(ComicBase):
    publisher_name: str
    grade_abbr: str

class Comic(ComicBase):
    id: int
    user_id: int
    publisher: Publisher
    grade: Grade

    class Config:
        from_attributes = True