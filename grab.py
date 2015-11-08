from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

db = create_engine('sqlite:///db.sqlite')

from via import ViaGrabber
from models import *

Session = sessionmaker(bind=db)
session = Session()


def add_trip(train_number, date):
    v = ViaGrabber()
    trip = v.get_status(train_number, date)

    existing = session.query(Trip).filter(and_(Trip.train_number == train_number,
                                               Trip.date == date)).first()
    if existing:
        # existing trip data exists, delete the stop info and update
        for stop in existing.stops:
            session.delete(stop)
        for stop in trip.stops:
            session.add(stop)
        existing.stops = trip.stops
        print "updating train #%d on %s" % (trip.train_number, str(date))
    else:
        # no existing trip, add this one
        print "adding train #%d on %s" % (trip.train_number, str(date))
        session.add(trip)

    session.commit()

if __name__ == '__main__':
    train_number = 87
    date = datetime.datetime.strptime('2015-11-01', '%Y-%m-%d').date()
    add_trip(train_number, date)




