from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Trip(Base):
    __tablename__ = 'trip'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    train_number = Column(Integer, nullable=False)
    stops = relationship('Stop')

    def has_arrived(self):
        if not self.stops or not self.stops[-1].remarks:
            return False
        else:
            return 'arrived' in self.stops[-1].remarks.lower()

    def __str__(self):
        res = "Train #%d, %s\n" % (self.train_number, str(self.date))
        for s in self.stops:
            res += "%s\n" % str(s)
        return res


class Stop(Base):
    __tablename__ = 'stop'
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trip.id'), nullable=False)
    sequence_number = Column(Integer)
    station = Column(String, nullable=False)
    scheduled_arr = Column(DateTime)
    scheduled_dep = Column(DateTime)
    #estimated_arr = Column(DateTime)
    #estimated_dep = Column(DateTime)
    actual_arr = Column(DateTime)
    actual_dep = Column(DateTime)
    remarks = Column(String)

    def __str__(self):
        return ("%s\t\t%s-%s\t%s-%s\t%s" % 
                (self.station,
                 self.scheduled_arr,
                 self.scheduled_dep,
                 #self.estimated_arr,
                 #self.estimated_dep,
                 self.actual_arr,
                 self.actual_dep,
                 self.remarks))

if __name__ == '__main__':
    db = create_engine('sqlite:///db.sqlite')
    Base.metadata.create_all(db)
