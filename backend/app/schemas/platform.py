from pydantic import BaseModel, ConfigDict


class PlatformResponse(BaseModel):
    slug: str
    name: str
    count: int

    model_config = ConfigDict(from_attributes=True)
