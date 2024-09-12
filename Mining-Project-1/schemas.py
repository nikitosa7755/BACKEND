import datetime

from pydantic import BaseModel, ConfigDict


class SConstantsAdd(BaseModel):
    coneHeight: float
    cylinderHeight: float
    Quefeed: int
    Qunderfl: int
    Flfeed: float
    psolid: int
    pfluid: int
    muliqour: float


class SConstants(SConstantsAdd):
    id: int
    created: str
    result: dict | None

    model_config = ConfigDict(from_attributes=True)


class SConstantsDict(BaseModel):
    value: list[SConstants]


class SConstantsID(BaseModel):
    ok: bool = True
    consts_id: int


class SValues(BaseModel):
    x: float
    y: float


class SResult(BaseModel):
    value: list[SValues]
