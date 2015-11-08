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
    # all corridor trains
    trains = [15, 33, 23, 25, 27, 29, 20, 22, 24, 26, 28, 628, 14, 51, 633, 55,
              59, 37, 639, 39, 30, 32, 632, 50, 634, 52, 38, 638, 651, 655, 61,
              63, 65, 67, 69, 669, 60, 62, 64, 66, 68, 650, 668, 40, 42, 44, 46,
              646, 48, 648, 41, 641, 43, 643, 45, 47, 647, 71, 73, 75, 81, 83,
              79, 82, 70, 80, 72, 76, 78, 85, 87, 84, 88, 97, 98]
    p = Pool(8)
    p.map(get_historic, trains)
