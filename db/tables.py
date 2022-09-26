from sqlalchemy import create_engine, Column, String, Integer, DateTime, Time, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import time

engine = create_engine('sqlite:///discordBot.sqlite', echo=True)
Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(15), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    schedules = relationship('Schedule', backref='subject')


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    timezone = Column(String(10), default=datetime.now().astimezone().tzinfo.tzname(datetime.now().astimezone()), nullable=False)
    weekdays = Column(Integer, nullable=False)
    time = Column(Time, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    def __repr__(self):
        name = self.time.strftime("%I:%M %p")
        return f"<{name} - {self.weekdays}>"
