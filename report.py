import sys
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base

from models import *
import datetime

db = create_engine('postgresql://viaontime:ontime@localhost:5432/viaontime')
Session = sessionmaker(bind=db)
session = Session()

def make_report(train_number):
    trips = session.query(Trip).filter_by(train_number = train_number).\
                                options(joinedload('stops')).\
                                order_by(desc(Trip.date)).\
                                limit(90).\
                                all()

    delayed = 0
    early = 0
    total_delay = datetime.timedelta(0)
    for trip in trips:
        s = session.query(Stop).filter_by(trip_id = trip.id).\
                                    order_by(desc(Stop.sequence_number)).\
                                    first()

        print 'sch: ' + str(s.scheduled_arr)
        print 'act: ' + str(s.actual_arr)
        if s.actual_arr - s.scheduled_arr > datetime.timedelta(0):
            print 'delayed: ' + str(s.actual_arr - s.scheduled_arr) + '\n'
            delayed += 1
            total_delay += s.actual_arr - s.scheduled_arr
        else:
            print 'early: ' + str(s.scheduled_arr - s.actual_arr) + '\n'
            early += 1
            total_delay -= s.scheduled_arr - s.actual_arr

    print 'delayed: %d, early: %d' % (delayed, early)
    print 'average delay: %s' % str((total_delay.seconds / 60)/60.0)

if __name__ == '__main__':
    make_report(int(sys.argv[1]))
