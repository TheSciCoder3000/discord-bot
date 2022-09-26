from sqlalchemy import create_engine, Column, String, Integer, DateTime, Time, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import time

engine = create_engine('sqlite:///discordBot.sqlite')
Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(15), nullable=False, unique=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    classes = relationship('SubjectClass', backref='subject')
    assessments = relationship('Assessment', backref='subject')
    guild_id = Column(Integer, nullable=True)


class SubjectClass(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    schedules = relationship('Schedule', backref='class')
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    guild_id = Column(Integer, nullable=True)
    

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    timezone = Column(String(10), default=datetime.now().astimezone().tzinfo.tzname(datetime.now().astimezone()), nullable=False)
    weekdays = Column(Integer, nullable=False)
    time_in = Column(Time, nullable=False)
    time_out = Column(Time, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    guild_id = Column(Integer, nullable=True)

    def __repr__(self):
        name = self.time.strftime("%I:%M %p")
        return f"<{name} - {self.weekdays}>"


class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    ass_type = Column(String(20), nullable=True)
    category = Column(String(25), nullable=True)
    guild_id = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<{self.name} - {self.category}>"