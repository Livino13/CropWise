from pydantic import BaseModel, Field as PydField


class WeatherRequest(BaseModel):
    latitude: float = PydField(ge=-90, le=90)
    longitude: float = PydField(ge=-180, le=180)


class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    source: str
