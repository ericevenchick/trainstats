import json
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base

from models import *
from report import *
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

db = create_engine('postgresql://viaontime:ontime@localhost:5432/viaontime')
Session = sessionmaker(bind=db)
session = Session()

if __name__ == '__main__':
    # all corridor trains, 97 removed due to lack of US arrival data
    # 15 removed due to being rare/outlier
    trains = [33, 23, 25, 27, 29, 20, 22, 24, 26, 28, 14, 51, 55,
              59, 37, 39, 30, 32, 50, 52, 38, 61,
              63, 65, 67, 69, 60, 62, 64, 66, 68, 40, 42, 44, 46,
              48, 41, 43, 45, 47, 71, 73, 75, 81, 83,
              79, 82, 70, 80, 72, 76, 78, 85, 87, 84, 88, 98]
    
    train_info = {'all_stops': [], 'train_stops': {}}
    average_delays = {}
    for t in trains:
        latest = session.query(Trip).filter_by(train_number = t)\
                                    .order_by(desc(Trip.date))\
                                    .first()
        stops = session.query(Stop).filter_by(trip_id = latest.id)\
                                   .all()
        train_info['train_stops'][t] = []
        for s in stops:
            train_info['train_stops'][t].append(remove_accents(s.station))
            if not remove_accents(s.station) in train_info['all_stops']:
                train_info['all_stops'].append(remove_accents(s.station))

    with open('out/data/train_info', 'w') as f:
        json.dump(train_info, f, separators=(',', ':'))


    for train_number in trains:
        stop_data = {}
        trips = session.query(Trip).filter_by(train_number = train_number).\
                                    options(joinedload('stops')).\
                                    order_by(desc(Trip.date)).\
                                    limit(60).\
                                    all()
        try:
            os.makedirs('out/data/train/%d' % train_number)
        except OSError:
            # ignore directory exists error
            pass

        r = Report(train_number)
        # get 6 month data
        r.make_report(180)
        with open('out/data/train/%d/report-180' % train_number, 'w') as f:
            json.dump(r.to_object(), f, separators=(',', ':'))
        average_delays[train_number] = r.average_delay

        # get 3 month data
        r.make_report(90)
        with open('out/data/train/%d/report-90' % train_number, 'w') as f:
            json.dump(r.to_object(), f, separators=(',', ':'))

        # get 1 month data
        r.make_report(30)
        with open('out/data/train/%d/report-30' % train_number, 'w') as f:
            json.dump(r.to_object(), f, separators=(',', ':'))

        print train_number

    with open('out/data/average_delays', 'w') as f:
        json.dump(average_delays, f, separators=(',', ':'))


    
