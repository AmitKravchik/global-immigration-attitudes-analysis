from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator



class Article(BaseModel):
    url: str = Field(..., validation_alias ="url", description="URL of the article")
    url_mobile: str = Field(..., validation_alias ="url_mobile", description="Mobile URL of the article")
    title: str = Field(..., validation_alias ="title", description="Title of the article")
    seen_date: datetime = Field(..., validation_alias ="seendate", description="Date the article was seen")
    social_image: str = Field(..., validation_alias ="socialimage", description="Social image URL of the article")
    domain: str = Field(..., validation_alias ="domain", description="Domain of the article")
    language: str = Field(..., validation_alias ="language", description="Language of the article")
    source_country: str = Field(..., validation_alias ="sourcecountry", description="Source country of the article")

    @field_validator("seen_date", mode="before")
    def serialize_seen_date(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ")

class ArticleListResponse(BaseModel):
    articles: List[Article] = Field(..., validation_alias ="articles", description="List of articles")
    