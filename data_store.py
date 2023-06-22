import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import config

Base = declarative_base()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

    def __repr__(self):
        return f'{self.profile_id}_{self.worksheet_id}'


class DBase():
    def __init__(self):
        self.create()
        self.engine = create_engine(config.db_url_object)
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(self.engine)

    def create(self):
        engine = create_engine(config.db_url_object)
        if not database_exists(engine.url):
            create_database(engine.url)

    def to_bd(self, profile_id, worksheet_id):
        self.session.add(Viewed(profile_id=profile_id, worksheet_id=worksheet_id))
        self.session.commit()

    def from_bd(self, profile_id, worksheet_id):
        return self.session.query(Viewed).filter(Viewed.profile_id == profile_id,
                                                 Viewed.worksheet_id == worksheet_id).first()


if __name__ == '__main__':
    my_ = DBase()
    # my_.to_bd(1, 4)
    print(my_.from_bd(1, 0))