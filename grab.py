import sys
from datetime import datetime, timedelta
from multiprocessing import Pool

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from via import ViaGrabber
from models import *

db = create_engine('postgresql://viaontime@localhost:5432/viaontime')
Session = sessionmaker(bind=db)
session = Session()


def add_trip(train_number, date, update=False):
    existing = session.query(Trip).filter(and_(Trip.train_number == train_number,
                                               Trip.date == date)).first()
    if existing and not update:
        raise Exception('not updating train %d on %s' % (train_number,
                                                         str(date)))

    v = ViaGrabber()
    trip = v.get_status(train_number, date)
    if trip == None:
        raise Exception('no data for train #%d on %s!' % (train_number,
                                                         str(date)))

    if existing:
        # existing trip data exists, delete the stop info and update
        for stop in existing.stops:
            session.delete(stop)
        for stop in trip.stops:
            session.add(stop)
        existing.stops = trip.stops
        print 'updating train #%d on %s' % (trip.train_number, str(date))
    else:
        # no existing trip, add this one
        print 'adding train #%d on %s' % (trip.train_number, str(date))
        session.add(trip)

    session.commit()

def get_historic(train_number):
    date = datetime.datetime.strptime('2015-04-13', '%Y-%m-%d').date()

    while date < datetime.datetime.today().date() - timedelta(days=1):
        date += timedelta(days=1)
        try:
            add_trip(train_number, date)
        except Exception as inst:
            print inst

if __name__ == '__main__':
    # ottawa -> toronto
    #trains = [41, 43, 51, 45, 47, 55, 647, 59]
    # toronto -> ottawa
    trains = [50, 52, 40, 42, 44, 46, 646, 48]
    p = Pool(len(trains))
    p.map(get_historic, trains)
