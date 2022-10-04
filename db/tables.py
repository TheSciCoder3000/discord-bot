from itertools import combinations
from typing import Any
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Time, ForeignKey
from discord.ext import commands
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta, date, time
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

    days = [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
    ]

    dt_days = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
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

    def datetime_sortable(self) -> datetime:
        utc_datetime = (datetime.combine(date(1,1,(8 + self.dt_days.index(self.get_day()))), self.time_in) - timedelta(hours=8))
        converted_datetime = utc_datetime if repl else datetime.combine(date(1,1,(8 + self.dt_days.index(self.get_day()))), self.time_in)
        return converted_datetime

    @staticmethod
    def get_day_list():
        return [
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
        ]

    def dispatch_sched_event(self, bot: commands.Bot, channel_id: int):
        utc_datetime = (datetime.combine(date(1,1,(8 + self.dt_days.index(self.get_day()))), self.time_in) - timedelta(hours=8))
        converted_datetime = utc_datetime if repl else datetime.combine(date(1,1,(8 + self.dt_days.index(self.get_day()))), self.time_in)
        print(f'dispatching sched event {converted_datetime.strftime("%A | %I:%M %p")}')
        print(f'converted to utc: {utc_datetime.strftime("%A | %I:%M %p")}')
        bot.dispatch(
            'add_schedule',
            self.dt_days[converted_datetime.weekday()].lower()[:3],
            f'{self.id} - {self.sched_class.subject.code}',
            self.sched_class.subject.name,
            converted_datetime,
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
    due_date: datetime = Column(DateTime, nullable=False)
    time = Column(Time, nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    ass_type = Column(String(20), nullable=True)
    category = Column(String(25), nullable=True)
    guild_id = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<{self.name} - {self.category}>"
    
    def dispatch_create_event(
        self, bot, channel_id: int = None, user_id: int = None, job_id: str = None,
        hour = 0, min = 0, sec = 0
    ):
        # create due_time
        due_time = self.time if self.time != None else time(23, 59, 59)
        sched_id = f"{self.id} - {self.name}" if job_id is None else job_id

        # set due date with due time
        converted_date = self.due_date.replace(
            hour=due_time.hour,
            minute=due_time.minute,
            second=due_time.second
        ) - timedelta(  # subtract timezone if in repl
            hours=8 if repl else 0
        ) - timedelta(  # subtract for advance reminders
            hours=hour, minutes=min, seconds=sec
        )

        # dispatch event
        bot.dispatch(
            'add_assessment',
            sched_id,
            converted_date,
            channel_id=channel_id,
            user_id=user_id
        )
    
    def dispatch_remove_event(self, bot: commands.Bot, job_id: str = None, channel_id: str = None, user_id: int = None):
        bot.dispatch(
            'remove_assessment',
            f"{self.id} - {self.name}" if job_id is None else job_id,
            channel_id=channel_id,
            user_id=user_id
        )