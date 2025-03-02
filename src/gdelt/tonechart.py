from datetime import datetime
from typing import Optional

from pydantic import Field, field_serializer, field_validator
from src.gdelt.responses import ToneChartResponse


class ToneChart(ToneChartResponse):
    source_country: str = Field(..., alias="source_country", description="Source country of the tone chart")
    start_datetime: datetime = Field(..., alias="startdatetime", description="Start datetime of the tone chart")
    end_datetime: datetime = Field(..., alias="enddatetime", description="End datetime of the tone chart")

    @field_serializer("start_datetime", "end_datetime", mode="plain")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y%m%d%H%M%S")