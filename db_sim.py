from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Alliance, Airline

# Create database and create a shortcut for easier to update database
engine = create_engine('sqlite:///airlines_alliances_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="robot", email="test@test.com")
session.add(User1)
session.commit()


# add alliances
category1 = Alliance(uid=1, name="Star Alliance")
session.add(category1)
session.commit()

category2 = Alliance(uid=1, name="SkyTeam")
session.add(category2)
session.commit()

category3 = Alliance(uid=1, name="Oneworld")
session.add(category3)
session.commit()

category4 = Alliance(uid=1, name="Non-Alliance")
session.add(category4)
session.commit()


# Add airlines
airline1 = Airline(uid=1, name="United Airlines",
                             description="Major US carrier based in Chicago, IL, USA.",
                             miles = 1,
                             alliance=category1)
session.add(airline1)
session.commit()

airline2 = Airline(uid=1, name="Delta Air Lines",
                             description="Major US carrier based in Atlanta, GA, USA.",
                             miles=2,
                             alliance=category2)
session.add(airline2)
session.commit()

airline3 = Airline(uid=1, name="American Airlines",
                             description="Major US carrier based in Fort-Worth, TX, USA.",
                             miles=3,
                             alliance=category3)
session.add(airline3)
session.commit()

airline4 = Airline(uid=1, name="Southwest Airlines",
                             description="US low-cost carrier based out of Dallas, TX, USA.",
                             miles=4,
                             alliance=category4)
session.add(airline4)
session.commit()


airline5 = Airline(uid=1, name="Singapore Airlines",
                             description="Flagship carrier of Singapore.",
                             miles=5,
                             alliance=category1)
session.add(airline5)
session.commit()


airline6 = Airline(uid=1, name="AIRFRANCE",
                             description="Flagship French carrier and subsidiary of Airfrance-KLM, based out of Tremblay en France, Paris, France",
                             miles=6,
                             alliance=category2)
session.add(airline6)
session.commit()


airline7 = Airline(uid=1, name="Qatar Airways",
                             description="State-owned carrier of Qatar, based out of Doha.",
                             miles=7,
                             alliance=category3)
session.add(airline7)
session.commit()

print("added category items!")
