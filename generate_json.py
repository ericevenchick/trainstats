import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base

from models import *
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

db = create_engine('postgresql://viaontime:ontime@localhost:5432/viaontime')
Session = sessionmaker(bind=db)
session = Session()

if __name__ == '__main__':
    # all corridor trains
    trains = [15, 33, 23, 25, 27, 29, 20, 22, 24, 26, 28, 628, 14, 51, 633, 55,
              59, 37, 639, 39, 30, 32, 632, 50, 634, 52, 38, 638, 651, 655, 61,
              63, 65, 67, 69, 669, 60, 62, 64, 66, 68, 650, 668, 40, 42, 44, 46,
              646, 48, 648, 41, 641, 43, 643, 45, 47, 647, 71, 73, 75, 81, 83,
              79, 82, 70, 80, 72, 76, 78, 85, 87, 84, 88, 97, 98]
    
    train_data = {}
    for t in trains:
        latest = session.query(Trip).filter_by(train_number = t)\
                                    .order_by(desc(Trip.date))\
                                    .first()
        stops = session.query(Stop).filter_by(trip_id = latest.id)\
                                   .all()
        train_data[t] = {'stops': []}
        for s in stops:
            train_data[t]['stops'].append(remove_accents(s.station))

    for train_number in trains:
        stop_data = {}
        trips = session.query(Trip).filter_by(train_number = train_number).\
                                    options(joinedload('stops')).\
                                    order_by(desc(Trip.date)).\
                                    limit(60).\
                                    all()
        for trip in trips:
            stops = session.query(Stop).filter_by(trip_id = trip.id).\
                                       order_by(asc(Stop.sequence_number))
            stop_data[str(trip.date)] = []
            for s in stops:
                if s.scheduled_arr:
                    sch_arr = s.scheduled_arr.strftime('%H:%M')
                else:
                    sch_arr = None
                if s.actual_arr:
                    act_arr = s.actual_arr.strftime('%H:%M')
                else:
                    act_arr = None
                if s.scheduled_dep:
                    sch_dep = s.scheduled_dep.strftime('%H:%M')
                else:
                    sch_dep = None
                if s.actual_dep:
                    act_dep = s.actual_dep.strftime('%H:%M')
                else:
                    act_dep = None

                stop_data[str(trip.date)].append({'st': s.station,
                                                  'sa': sch_arr,
                                                  'aa': act_arr,
                                                  'sd': sch_dep,
                                                  'ad': act_dep
                                                })
                with open('out/train/%d' % train_number, 'w') as f:                                 
                    json.dump(stop_data, f, separators=(',', ':'))
        print train_number

    print json.dumps(train_data, separators=(',', ':'))
