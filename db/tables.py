from typing import Any
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Time, ForeignKey
from discord.ext import commands
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta, date
from config import repl

engine = create_engine('sqlite:///discordBot.sqlite')
Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(15), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    classes = relationship('SubjectClass', backref='subject', cascade='all,delete')
    assessments = relationship('Assessment', backref='subject', cascade='all,delete')
    guild_id = Column(Integer, nullable=True)


class SubjectClass(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    schedules = relationship('Schedule', backref='sched_class', cascade='all,delete')
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    guild_id = Column(Integer, nullable=True)


class Schedule(Base):
    __tablename__ = 'schedules'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        

    days = [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
    ]

    id = Column(Integer, primary_key=True)
    timezone = Column(String(10), default=datetime.now().astimezone().tzinfo.tzname(datetime.now().astimezone()), nullable=False)
    weekdays = Column(Integer, nullable=False)
    time_in = Column(Time, nullable=False)
    time_out = Column(Time, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    guild_id = Column(Integer, nullable=True)

    def __repr__(self):
        time_start = self.time_in.strftime("%I:%M %p")
        time_end = self.time_out.strftime("%I:%M %p")
        return f"{self.days[self.weekdays]} | {time_start} - {time_end}"

    def get_day(self) -> str:
        return self.days[self.weekdays]

    def dispatch_sched_event(self, bot: commands.Bot, channel_id: int):
        utc_time = (datetime.combine(date(1,1,1), self.time_in) - timedelta(hours=8)).time()
        converted_time = utc_time if repl else self.time_in
        bot.dispatch(
            'add_schedule',
            self.get_day().lower()[:3],
            f'{self.id} - {self.sched_class.subject.code}',
            self.sched_class.subject.name,
            converted_time,
            channel_id
        )
    
    def dispatch_remove_event(self, bot: commands.Bot, channel_id: int):
        bot.dispatch(
            'remove_schedule',
            f'{self.id} - {self.sched_class.subject.code}',
            channel_id
        )


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