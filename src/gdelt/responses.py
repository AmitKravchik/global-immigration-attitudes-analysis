from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer, field_validator



class GDELTArticle(BaseModel):
    url: str = Field(..., validation_alias ="url", description="URL of the article")
    title: str = Field(..., validation_alias ="title", description="Title of the article")



class ArticleListArticle(GDELTArticle):
    url_mobile: str = Field(..., validation_alias ="url_mobile", description="Mobile URL of the article")
    seen_date: datetime = Field(..., validation_alias ="seendate", description="Date the article was seen")
    social_image: str = Field(..., validation_alias ="socialimage", description="Social image URL of the article")
    domain: str = Field(..., validation_alias ="domain", description="Domain of the article")
    language: str = Field(..., validation_alias ="language", description="Language of the article")
    source_country: str = Field(..., validation_alias ="sourcecountry", description="Source country of the article")

    @field_validator("seen_date", mode="before")
    def serialize_seen_date(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ")
    
    @field_serializer("seen_date", mode="plain")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y%m%d%H%M%S")


class ArticleListResponse(BaseModel):
    articles: List[GDELTArticle] = Field(..., validation_alias ="articles", description="List of articles")
    


class GDELTToneChartBin(BaseModel):
    bin: int = Field(..., validation_alias ="bin", description="Bin number")
    count: int = Field(..., validation_alias ="count", description="Count of articles in the bin")
    top_articles: List[GDELTArticle] = Field(..., validation_alias ="toparts", description="Top articles in the bin")

class ToneChartResponse(BaseModel):
    tonechart: List[GDELTToneChartBin] = Field(..., validation_alias ="tonechart", description="List of bins")

