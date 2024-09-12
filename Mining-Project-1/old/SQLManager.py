from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json


class Constants(DeclarativeBase):
    __tablename__ = 'constants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, nullable=False)
    coneHeight = Column(Float, nullable=False)
    cylinderHeight = Column(Float, nullable=False)
    Quefeed = Column(Integer, nullable=False)
    Qunderfl = Column(Integer, nullable=False)
    Flfeed = Column(Float, nullable=False)
    psolid = Column(Integer, nullable=False)
    pfluid = Column(Integer, nullable=False)
    muliqour = Column(Float, nullable=False)

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'created': self.created.isoformat(),
            'coneHeight': self.coneHeight,
            'cylinderHeight': self.cylinderHeight,
            'Quefeed': self.Quefeed,
            'Qunderfl': self.Qunderfl,
            'Flfeed': self.Flfeed,
            'psolid': self.psolid,
            'pfluid': self.pfluid,
            'muliqour': self.muliqour
        })


class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.Session = async_sessionmaker(bind=self.engine)

    def add_constants(self, **kwargs):
        session = self.Session()
        new_constants = Constants(**kwargs)
        session.add(new_constants)
        session.commit()
        session.close()

    def get_constants(self):
        session = self.Session()
        constants = session.query(Constants).all()
        session.close()
        return [const.to_json() for const in constants]
