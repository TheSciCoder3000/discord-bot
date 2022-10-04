from distutils.command.config import config
from email.policy import default
from sqlalchemy.orm import sessionmaker, Query
from .tables import engine, Schedule, Subject, Assessment, SubjectClass
from typing import Type
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord

jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///job.sqlite")}

scheduler = AsyncIOScheduler(jobstores=jobstores)

class Connection(object):
    def __enter__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def add(self, row):
        self.session.add(row)
        self.session.commit()

    def query(self, rowObj) -> Query:
        return self.session.query(rowObj)

    def __del__(self):
        self.session.commit()
        self.session.close()

    def remove(self, instance):
        self.session.delete(instance)
        self.session.commit()