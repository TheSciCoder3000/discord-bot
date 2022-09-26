from sqlalchemy.orm import sessionmaker
from tables import engine, Schedule, Subject


class Connection(object):
    def __enter__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.session.commit()

    def add(self, row):
        self.session.add(row)