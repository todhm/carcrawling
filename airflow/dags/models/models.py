#!/bin/python3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Date, Integer, String
from datetime import datetime
from models.utils import create_session

# Initialize the declarative base model
Base = declarative_base()

def insert_auction_car_list(car_data_list,session):
    for car_data in car_data_list:
        auction_loc = car_data.get("car_loc")
        auction_id = car_data.get('auction_id')
        auction = Auction.upsert_auction(auction_id,auction_loc,session)
        car_data['auction_id'] = auction.id
        car = Car.insert_car(car_data,session)
    return True

class Car(Base):
    __tablename__ = "car"
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_brand = Column(String, nullable=False)
    car_name = Column(String, nullable=False)
    year = Column(Integer)
    transmission = Column(String(length=50))
    fuel_type = Column(String(length=50))
    engine_size = Column(Integer)
    kilos = Column(Integer)
    auction_id = Column(Integer, ForeignKey("auction.id"))
    auction_car_id = Column(Integer)
    car_img_src = Column(String(length=255))
    car_color = Column(String(length=50))
    car_type = Column(String(length=255))
    car_owner = Column(String(length=255))
    car_reputation = Column(String(length=255))
    car_auction_start_price = Column(Integer)


    @property
    def to_json(self):
        return {
        "car_brand":self.car_brand,
        "car_name":self.car_name,
        "year":self.year,
        'transmission':self.transmission,
        'fuel_type':self.fuel_type,
        'engine_size':self.engine_size,
        'transmission':self.transmission,
        'kilos':self.kilos,
        'car_img_src':'https://www.glovisaa.com'+self.car_img_src,
        'car_color':self.car_color,
        'car_type':self.car_type,
        'car_owner':self.car_owner,
        'car_reputation':self.car_reputation,
        'car_auction_start_price':self.car_auction_start_price
    }


    @classmethod
    def insert_car(cls,car_dict,session):
        car = session.query(cls)\
            .filter(cls.auction_car_id==car_dict.get("auction_car_id"))\
            .filter(cls.auction_id==car_dict.get('auction_id'))\
            .first()
        new_car_dict = {}
        for key in car_dict:
            if hasattr(cls,key):
                new_car_dict[key] = car_dict[key]
        if car: 
            session.query(cls)\
                .filter(cls.auction_car_id==car_dict.get("auction_car_id"))\
                .filter(cls.auction_id==car_dict.get('auction_id'))\
                .update(new_car_dict)
            return car 
        else:
            car = cls(**new_car_dict)
            session.add(car)
            session.commit()
            return car 

class Auction(Base):
    __tablename__ = "auction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    auction_number = Column(Integer, nullable=False)
    auction_loc = Column(String, nullable=False)


    @classmethod
    def upsert_auction(cls,auction_number,auction_loc,session):
        auction = session.query(cls)\
            .filter(cls.auction_number==auction_number)\
            .filter(cls.auction_loc==auction_loc)\
            .first()
        if auction: 
            return auction 
        else:
            auction = cls(auction_number=auction_number,auction_loc=auction_loc)
            session.add(auction)
            session.commit()
            return auction 


    @property
    def to_json(self):
        return {
        "auction_number":self.auction_number,
        "auction_loc":self.auction_loc
    }

