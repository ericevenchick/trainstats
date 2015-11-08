import requests
from bs4 import BeautifulSoup
import datetime
from models import *

class ViaGrabber:
    def _combine_date(self, date, time_str):
        if time_str == None or date == None:
            return None
        t = datetime.datetime.strptime(time_str, "%H:%M").time()
        return datetime.datetime.combine(date, t)

    def _get_time(self, text):
        """ Helper function to convert a table data element into a time """
        res = text.encode('utf-8')

        # remove nbsps
        res = res.replace('\xc2\xa0', '')

        if res == '':
            return None
        else:
            return res

    def get_status(self, train_number, trip_date):
        payload = {'l': 'en',
                   'TsiCCode': 'VIA',
                    'TsiTrainNumber': train_number,
                    'DepartureDate': trip_date,
                    'ArrivalDate': trip_date,
                    'TrainInstanceDate': trip_date}
        r = requests.get('http://reservia.viarail.ca/tsi/GetTrainStatus.aspx',
                         params=payload)

        soup = BeautifulSoup(r.text, 'html.parser')

        # fetch the table
        tsicontent = soup.find(id='tsicontent')
        if tsicontent == None:
            # no data was found
            return None
        table = tsicontent.find('center').find('table')
        # extract all top level rows
        rows = table.find_all('tr', recursive=False)

        # first two rows and last row are static, remove them
        rows = rows[2:]
        rows = rows[:-1]

        # loop through the table rows
        index = 0
        trip = Trip(date=trip_date, train_number=train_number)
        for row in rows:
            # get all the data value for all columns
            cols = row.find_all('td', recursive=False)

            # column 0: station name
            station = cols[0].text.encode('utf-8')

            # column 1: dep/arrive text. used to determine number of rows
            num_rows = len(cols[1].find_all('tr'))

            # column 2: scheduled time
            if num_rows == 1 and index == 0:
                # first station, depart time only
                scheduled_arr = None
                scheduled_dep_s = self._get_time(cols[2].find_all('tr')[0].text)
                scheduled_dep = self._combine_date(trip_date, scheduled_dep_s)

            elif num_rows == 1 and index > 0:
                # last station, arrival time only
                scheduled_arr_s = self._get_time(cols[2].find_all('tr')[0].text)
                scheduled_arr = self._combine_date(trip_date, scheduled_arr_s)
                scheduled_dep = None
            elif num_rows > 1:
                # station has depart and arrival times
                scheduled_arr_s = self._get_time(cols[2].find_all('tr')[0].text)
                scheduled_arr = self._combine_date(trip_date, scheduled_arr_s)
                scheduled_dep_s = self._get_time(cols[2].find_all('tr')[1].text)
                scheduled_dep = self._combine_date(trip_date, scheduled_dep_s)
            else:
                raise Exception('failed to parse scheduled time!')

            # check for day overflows
            if index > 0 and trip.stops[0].scheduled_dep and scheduled_dep:
                if trip.stops[0].scheduled_dep > scheduled_dep:
                    scheduled_dep += datetime.timedelta(days=1)
            if index > 0 and trip.stops[0].scheduled_dep and scheduled_arr:
                if trip.stops[0].scheduled_dep > scheduled_arr:
                    scheduled_arr += datetime.timedelta(days=1)

            # column 3: estimated time, not tracked

            # column 4: actual time
            if num_rows == 1 and index == 0:
                # first station, depart time only
                actual_arr = None
                actual_dep_s = self._get_time(cols[4].find_all('tr')[0].text)
                actual_dep = self._combine_date(trip_date, actual_dep_s)
            elif num_rows == 1 and index > 0:
                # last station, arrival time only
                actual_arr_s = self._get_time(cols[4].find_all('tr')[0].text)
                actual_arr = self._combine_date(trip_date, actual_arr_s)
                actual_dep = None
            elif num_rows > 1:
                # station has depart and arrival times
                actual_arr_s = self._get_time(cols[4].find_all('tr')[0].text)
                actual_arr = self._combine_date(trip_date, actual_arr_s)
                actual_dep_s = self._get_time(cols[4].find_all('tr')[1].text)
                actual_dep = self._combine_date(trip_date, actual_dep_s)
            else:
                raise Exception('failed to parse actual time!')

            # check for day overflows
            if index > 0 and trip.stops[0].actual_dep and actual_dep:
                if trip.stops[0].actual_dep > actual_dep:
                    actual_dep += datetime.timedelta(days=1)
            if index > 0 and trip.stops[0].actual_dep and actual_arr:
                if trip.stops[0].actual_dep > actual_arr:
                    actual_arr += datetime.timedelta(days=1)

            # column 5: remarks
            remarks = cols[5].text.encode('utf-8')
            # remove nbsp
            remarks = remarks.replace('\xc2\xa0', '')
            # if empty, set value to none
            if remarks == '':
                remarks = None

            this_stop = Stop()
            this_stop.station = station
            this_stop.scheduled_arr = scheduled_arr
            this_stop.scheduled_dep = scheduled_dep
            this_stop.actual_arr = actual_arr
            this_stop.actual_dep = actual_dep
            this_stop.remarks = remarks
            this_stop.sequence_number = index + 1

            trip.stops.append(this_stop)
            index = index + 1

        return trip

if __name__ == '__main__':
    db = create_engine('sqlite:///db.sqlite')
    Session = sessionmaker(bind=db)
    session = Session()
    Base.metadata.create_all(db)

    v = ViaGrabber()
    trip = v.get_status(87, datetime.datetime.strptime('2015-11-06', '%Y-%m-%d'))
    print trip
    print trip.has_arrived()

    session.add(trip)
    session.commit()

    trip = session.query(Trip).first()
