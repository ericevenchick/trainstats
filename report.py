import sys
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base

from models import *
import datetime
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


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
        self.delays = {} 
        self.trip_count = 0
        for trip in trips:
            # get the stops, sorted by sequence
            stops = sorted(trip.stops, key=lambda s: s.sequence_number)
            if len(stops) == 0:
                # not a valid trip
                continue

            # add the total trip delay to the running total
            last_stop = stops[-1]
            if last_stop.actual_arr == None or last_stop.scheduled_arr == None:
                # not a valid trip
                continue
            delay = last_stop.actual_arr - last_stop.scheduled_arr
            if delay > datetime.timedelta(0):
                self.total_delay += delay


            for s in stops:
                if s.actual_arr == None or s.scheduled_arr == None:
                    # didn't stop here, ignore it
                    continue
                s.station = remove_accents(s.station)
                if not s.station in self.delays.keys():
                    self.delays[s.station] = {0: 0, 10: 0, 30: 0, 
                                              'count': 0}
                    
                delay = s.actual_arr - s.scheduled_arr

                if delay < datetime.timedelta(minutes=10):
                    self.delays[s.station][0] += 1
                elif (delay >= datetime.timedelta(minutes=10) and delay <
                    datetime.timedelta(minutes=30)): 
                    self.delays[s.station][10] += 1
                elif delay >= datetime.timedelta(minutes=30):
                    self.delays[s.station][30] += 1
                self.delays[s.station]['count'] += 1
                
            self.trip_count += 1

        if self.trip_count == 0:
            raise Exception('no valid trips!')

        stops = sorted(trips[0].stops, key=lambda s: s.sequence_number)
        self.scheduled_len = (stops[0].scheduled_dep -
                              stops[-1].scheduled_arr)

        self.average_delay = (self.total_delay.total_seconds() / 60.0 /
                              self.trip_count)

    def to_object(self):
        obj = {}
        obj['delays'] = self.delays
        obj['total_delay'] = self.total_delay.seconds / 60
        obj['average_delay'] = self.average_delay
        obj['scheduled_len'] = self.scheduled_len.seconds / 60
        obj['trip_count'] = self.trip_count
        return obj

if __name__ == '__main__':
    r = Report(int(sys.argv[1]))
    r.make_report(days=180)
    #print r.trip_count
    #print r.average_delay
    print r.delays
    #print r.to_object()
