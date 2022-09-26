from sqlalchemy.orm import sessionmaker, Query
from .tables import engine, Schedule, Subject, Assessment, SubjectClass


class Connection(object):
    def __enter__(self):
        Session = sessionmaker(bind=engine, expire_on_commit=False)
        self.session = Session()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.session.commit()

    def add(self, row):
        self.session.add(row)

    def query(self, rowObj):
        return self.session.query(rowObj)

    def __del__(self):
        self.session.close()

    def remove(self, instance):
        # instance = self.session.query(rowObj).filter_by(id=id).first()
        self.session.delete(instance)
        self.session.commit()
