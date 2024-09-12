import datetime

from sqlalchemy import Column, JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from cfg import DB_URL

engine = create_async_engine(
    f"{DB_URL}"
)
new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


class Model(DeclarativeBase):
    pass


class ConstantsORM(Model):
    __tablename__ = "constants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[str] = mapped_column(default=datetime.datetime.now().isoformat())
    coneHeight: Mapped[float]
    cylinderHeight: Mapped[float]
    Quefeed: Mapped[int]
    Qunderfl: Mapped[int]
    Flfeed: Mapped[float]
    psolid: Mapped[int]
    pfluid: Mapped[int]
    muliqour: Mapped[float]
    result = Column(JSON, nullable=True)
