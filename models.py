import os
import json

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from flask_sqlalchemy import SQLAlchemy

# Connect the local postgres database
database_name = "hktm"
database_path = "postgresql://{}/{}".format(
    "postgres@localhost:5432", database_name)

# Connect the postgres database on Heroku
# database_path = "postgresql" + os.environ['DATABASE_URL'][8:]

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    return db


class helperMethodsClass(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


"""
Trademark
"""


class Trademark(helperMethodsClass):
    __tablename__ = "trademarks"

    app_no = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    owners = Column(String, nullable=False)
    applicant = Column(String, nullable=True)
    type = Column(String, nullable=True)
    trademark_id = Column(String, nullable=True)
    specs = db.relationship("Spec",
                            backref="trademark",
                            lazy=True,
                            cascade="all,delete")

    def format(self):
        return {
            "app_no": self.app_no,
            "name": self.name,
            "status": self.status,
            "owners": self.owners,
        }

    def long(self):
        return {
            "app_no": self.app_no,
            "name": self.name,
            "status": self.status,
            "owners": self.owners,
            "applicant": self.applicant,
            "type": self.type,
            "trademark_id": self.trademark_id
        }


'''
Trademark Class Specifications
'''


class Spec(helperMethodsClass):
    __tablename__ = "specs"

    id = Column(Integer, primary_key=True)
    class_no = Column(Integer, nullable=False)
    class_spec = Column(String, nullable=False)
    tm_app_no = Column(String, ForeignKey("trademarks.app_no"), nullable=True)

    def format(self):
        return {
            "id": self.id,
            "class_no": self.class_no,
            "class_spec": self.class_spec,
            "tm_app_no": self.tm_app_no
        }
