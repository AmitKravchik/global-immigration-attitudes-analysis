from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from enum import Enum
from typing import Optional

class GDELTMode(str, Enum):
    ART_LIST = "artlist"
    ART_GALLERY = "artgallery"
    IMAGE_COLLAGE = "imagecollage"
    IMAGE_COLLAGE_INFO = "imagecollageinfo"
    IMAGE_GALLERY = "imagegallery"
    IMAGE_COLLAGE_SHARE = "imagecollageshare"
    TIMELINE_VOL = "timelinevol"
    TIMELINE_VOL_RAW = "timelinevolraw"
    TIMELINE_VOL_INFO = "timelinevolinfo"
    TIMELINE_TONE = "timelinetone"
    TIMELINE_LANG = "timelinelang"
    TIMELINE_SOURCE_COUNTRY = "timelinesourcecountry"
    TONE_CHART = "tonechart"
    WORD_CLOUD_IMAGE_TAGS = "wordcloudimagetags"
    WORD_CLOUD_IMAGE_WEB_TAGS = "wordcloudimagewebtags"

class OutputFormat(str, Enum):
    HTML = "html"
    CSV = "csv"
    RSS = "rss"
    RSS_ARCHIVE = "rssarchive"
    JSON = "json"
    JSONP = "jsonp"
    JSON_FEED = "jsonfeed"

class SortOrder(str, Enum):
    DATE_DESC = "DateDesc"
    DATE_ASC = "DateAsc"
    TONE_DESC = "ToneDesc"
    TONE_ASC = "ToneAsc"
    HYBRID_REL = "HybridRel"


class GDELTQuery(BaseModel):
    query: str = Field(..., serialization_alias="query", description="The base search query, e.g. 'immigration'")

    # Image-related filters
    image_face_tone: Optional[str] = Field(None, serialization_alias="imagefacetone", description="Image face tone filter (e.g., imagefacetone<-1.5)")
    image_num_faces: Optional[str] = Field(None, serialization_alias="imagenumfaces", description="Image number of faces filter (e.g., imagenumfaces>3)")
    image_ocr_meta: Optional[str] = Field(None, serialization_alias="imageocrmeta", description="Image OCR meta filter (e.g., imageocrmeta:\"zika\")")
    image_tag: Optional[str] = Field(None, serialization_alias="imagetag", description="Image tag filter (e.g., imagetag:\"safesearchviolence\")")
    image_web_count: Optional[str] = Field(None, serialization_alias="imagewebcount", description="Image web count filter (e.g., imagewebcount<10)")
    image_web_tag: Optional[str] = Field(None, serialization_alias="imagewebtag", description="Image web tag filter (e.g., imagewebtag:\"drone\")")

    # Additional operators
    near: Optional[str] = Field(None, serialization_alias="near", description="Near operator filter (e.g., near20:\"trump putin\")")
    repeat: Optional[str] = Field(None, serialization_alias="repeat", description="Repeat operator filter (e.g., repeat3:\"trump\")")

    # Source and language filters
    source_lang: Optional[str] = Field(None, serialization_alias="sourcelang", description="Language filter (e.g., sourcelang:spanish)")
    source_country: Optional[str] = Field(None, serialization_alias="sourcecountry", description="Country filter (e.g., sourcecountry:US)")
    
    # Theme filter
    theme: Optional[str] = Field(None, serialization_alias="theme", description="GKG theme filter (e.g., theme:TERROR)")
    
    # Tone filters
    tone: Optional[str] = Field(None, serialization_alias="tone", description="Tone filter (e.g., tone<-5 or tone>5)")
    tone_abs: Optional[str] = Field(None, serialization_alias="toneabs", description="Absolute tone filter (e.g., toneabs>10)")

    # Domain
    domain: Optional[str] = Field(None, serialization_alias="domain", description="Domain filter (e.g., domain:nytimes.com)")
    domain_is: Optional[str] = Field(None, serialization_alias="domainis", description="Domain is filter (e.g., domainis:nytimes.com)")

    def build(self) -> str:
        query_dict = self.model_dump(exclude_unset=True, by_alias=True)
        query_str = " ".join(query_dict.values())
        return query_str
    
    def __str__(self):
        return self.build()
        


class GDELTRequestParams(BaseModel):
    # Basic parameters
    query: GDELTQuery = Field(..., serialization_alias="query", description="The base search query, e.g. 'immigration'")
    mode: GDELTMode = Field(GDELTMode.ART_LIST, serialization_alias="mode", description="Output mode (e.g., artlist, tonechart, etc.)")
    start_datetime: Optional[datetime] = Field(None, serialization_alias="STARTDATETIME", description="Start datetime in YYYYMMDDHHMMSS format")
    end_datetime: Optional[datetime] = Field(None, serialization_alias="ENDDATETIME", description="End datetime in YYYYMMDDHHMMSS format")
    output_format: OutputFormat = Field(OutputFormat.JSON, serialization_alias="format", description="Output format (json, csv, etc.)")
    sort_order: Optional[SortOrder] = Field(None, serialization_alias="sort", description="Sort order (e.g., ToneDesc)")
    timespan: Optional[str] = Field(None, serialization_alias="timespan", description="Time span for the search (e.g., '3months')")
    
    # HTML only Parameters
    timeline_smooth: Optional[int] = Field(None, serialization_alias="TIMELINESMOOTH", description="Moving window smoothing over the specified number of time steps, up to a maximum of 30")
    trans: Optional[str] = Field(None, serialization_alias="TRANS", description="Machine translation widget for article titles in the requested language")
    time_zoom: Optional[str] = Field(None, serialization_alias="TIMEZOOM", description='Enable interactive zooming of the timeline ("yes" to enable, "no" to disable)')

    @field_serializer("start_datetime", "end_datetime", mode="plain")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y%m%d%H%M%S")

    def build_url(self, base_url: str) -> str:
        query_dict = self.model_dump(exclude_unset=True, by_alias=True)
        query_dict['query'] = self.query.build()
        query_str = "&".join([f"{key}={value}" for key, value in query_dict.items()])
        query_str = f"{base_url}?{query_str}"
        return query_str






