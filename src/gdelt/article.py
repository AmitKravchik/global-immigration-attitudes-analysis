from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer, field_validator

from src.gdelt.responses import GDELTArticle



class Article(GDELTArticle):
    html: Optional[str] = Field(None, description="HTML content of the article")
    html_body: Optional[str] = Field(None, alias="html_body", description="Body of the article")
    html_title: Optional[str] = Field(None, alias="html_title", description="Title of the article")
    gdelt_tone: Optional[int] = Field(None, alias="tone", description="Tone of the article")
    start_datetime: Optional[datetime] = Field(None, alias="startdatetime", description="Start datetime of the article")
    end_datetime: Optional[datetime] = Field(None, alias="enddatetime", description="End datetime of the article")
    source_country: Optional[str] = Field(None, alias="sourcecountry", description="Source country of the article")

    @field_serializer("start_datetime", "end_datetime", mode="plain")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y%m%d%H%M%S")

    @field_validator("start_datetime", "end_datetime", mode="before")
    def serialize_seen_date(cls, value: str) -> datetime:
        return datetime.strptime(value, '%Y%m%d%H%M%S')

class ArticleList(BaseModel):
    articles: List[Article] = Field(..., alias="articles", description="List of articles")



class ToneChartBin(BaseModel):
    bin: int = Field(..., validation_alias ="bin", description="Bin number")
    count: int = Field(..., validation_alias ="count", description="Count of articles in the bin")
    top_articles: List[Article] = Field(..., validation_alias ="top_articles", description="Top articles in the bin")

class ToneChart(BaseModel):
    tonechart: List[ToneChartBin] = Field(..., validation_alias ="tonechart", description="List of bins")
    source_country: str = Field(..., alias="source_country", description="Source country of the tone chart")
    start_datetime: datetime = Field(..., alias="start_datetime", description="Start datetime of the tone chart")
    end_datetime: datetime = Field(..., alias="end_datetime", description="End datetime of the tone chart")


    @field_serializer("start_datetime", "end_datetime", mode="plain")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y%m%d%H%M%S")


    @field_validator("start_datetime", "end_datetime", mode="before")
    def serialize_seen_date(cls, value: str) -> datetime:
        return datetime.strptime(value, '%Y%m%d%H%M%S')
    

