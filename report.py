import sys
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base

from models import *
import datetime

db = create_engine('postgresql://viaontime:ontime@localhost:5432/viaontime')
Session = sessionmaker(bind=db)
session = Session()

class Report:
    def __init__(self, train_number):
        self.train_number = train_number

    def make_report(self, days=180):
        # get trips from the db
        trips = session.query(Trip).filter_by(train_number = self.train_number).\
                                    filter(Trip.date >= datetime.date.today() -
                                           datetime.timedelta(days=days)).\
                                    options(joinedload('stops')).\
                                    order_by(desc(Trip.date)).\
                                    all()

        self.total_delay = datetime.timedelta(0)
        self.delay_bins = {0: 0, 5: 0, 10: 0, 15: 0, 20: 0, 30: 0, 45: 0, 60: 0}
        self.trip_count = 0
        for trip in trips:
            # get the stops, sorted by sequence
            stops = sorted(trip.stops, key=lambda s: s.sequence_number)
            if len(stops) == 0:
                # not a valid trip
                continue

            # get the last stop
            s = stops[-1]             

            if s.actual_arr == None or s.scheduled_arr == None:
                # not a valid trip
                continue

            delay = s.actual_arr - s.scheduled_arr
            self.total_delay += delay

            # update delay bins
            if delay < datetime.timedelta(minutes=60):
                self.delay_bins[60] += 1
            if delay < datetime.timedelta(minutes=45):
                self.delay_bins[45] += 1
            if delay < datetime.timedelta(minutes=30):
                self.delay_bins[30] += 1
            if delay < datetime.timedelta(minutes=20):
                self.delay_bins[20] += 1
            if delay < datetime.timedelta(minutes=15):
                self.delay_bins[15] += 1
            if delay < datetime.timedelta(minutes=10):
                self.delay_bins[10] += 1
            if delay < datetime.timedelta(minutes=5):
                self.delay_bins[5] += 1
            if delay < datetime.timedelta(minutes=0):
                self.delay_bins[0] += 1

            self.trip_count += 1

        if self.trip_count == 0:
            raise Exception('no valid trips!')
        stops = sorted(trips[0].stops, key=lambda s: s.sequence_number)
        self.scheduled_len = (stops[0].scheduled_dep -
                              stops[-1].scheduled_arr)

        self.average_delay = (self.total_delay.total_seconds() / 60.0 /
                              self.trip_count)
        for k in self.delay_bins:
            # convert to percentages
            self.delay_bins[k] = 100.0 * self.delay_bins[k] / self.trip_count

    def to_object(self):
        obj = {}
        obj['delay_bins'] = self.delay_bins
        obj['total_delay'] = self.total_delay.seconds / 60
        obj['average_delay'] = self.average_delay
        obj['scheduled_len'] = self.scheduled_len.seconds / 60
        obj['trip_count'] = self.trip_count
        return obj

if __name__ == '__main__':
    r = Report(int(sys.argv[1]))
    r.make_report()
    print r.trip_count
    print r.average_delay
    print r.delay_bins
