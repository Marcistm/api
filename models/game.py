from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_date = Column(Date)
    time_start = Column(String(10))
    status = Column(String(10))
    home = Column(String(15))
    road = Column(String(15))
    home_score = Column(Integer)
    road_score = Column(Integer)
