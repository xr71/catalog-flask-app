from sqlalchemy import (
        create_engine,
        Column,
        ForeignKey,
        Integer,
        String
    )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

###############################################################################
# Models
###############################################################################

# User login model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), nullable=False)
    picture = Column(String(255))

    @property
    def serialize(self):
        return {
            "name": self.name,
            "email": self.email,
            "id": self.id
        }

# Catalog Top Level Category model
# which is Airline Alliances here - An alliance is an agreement between a
# number of airlines to pool resources.
class Alliance(Base):
    __tablename__ = "alliances"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    uid = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "alliance_name": self.name,
            "id": self.id
        }


# Airline model and which alliance category it belongs to
class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    miles = Column(Integer)
    description = Column(String(255))
    aid = Column(Integer, ForeignKey("alliances.id"))
    alliance = relationship(Alliance, backref=backref("alliances", cascade="all, delete"))
    uid = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "miles": self.miles,
            "alliance": self.alliance.name,
            "id": self.id
        }


engine = create_engine('sqlite:///airlines_alliances_catalog.db')
Base.metadata.create_all(engine)
