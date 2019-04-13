from models.models import Base,Car,Auction 
from sqlalchemy import func



class CarAuctionDao:


    @staticmethod
    def car_auction_stats(session,auction_number,auction_loc):
        query_result = session.query(
            Car.car_brand,
            Car.car_name,
            func.count(Car.id).label('car_count'),
            func.avg(Car.car_auction_start_price).label('average_price'),
            func.max(Car.car_auction_start_price).label('max_car_price'),
            func.min(Car.car_auction_start_price).label('min_car_price'),
            func.avg(Car.kilos).label('average_car_kilos'),
            func.max(Car.kilos).label('max_car_kilos'),
            func.min(Car.kilos).label('min_car_kilos'),
        ) \
        .filter(Car.auction_id==Auction.id) \
        .group_by(Car.car_brand,Car.car_name) \
        .filter(Auction.auction_number==auction_number) \
        .filter(Auction.auction_loc==auction_loc) \
        .all()
        query_data_list = []
        for query_data in query_result:
            result_map = {}
            result_map['car_brand'] = query_data[0]
            result_map['car_name'] = query_data[1]
            result_map['car_count'] = query_data[2]
            result_map['average_car_price'] = float(query_data[3])
            result_map['max_car_price'] = float(query_data[4])
            result_map['min_car_price'] = float(query_data[5])
            result_map['average_car_kilos'] = float(query_data[6])
            result_map['max_car_kilos'] = float(query_data[7])
            result_map['min_car_kilos'] = float(query_data[8])
            query_data_list.append(result_map)

        return query_data_list
    

    @staticmethod
    def get_specific_car_auction_data(session,auction_number,auction_loc):
        query_result = session.query(
            Car,
            Auction
        ) \
        .filter(Car.auction_id==Auction.id) \
        .filter(Auction.auction_number==auction_number) \
        .filter(Auction.auction_loc==auction_loc) \
        .order_by(Car.car_brand)\
        .order_by(Car.car_name)\
        .order_by(Car.car_auction_start_price)\
        .all()
        result_list = []
        for (car,auction) in query_result:
            result_map = {}
            result_map.update(car.to_json)
            result_map.update(auction.to_json)
            result_list.append(result_map)


        return result_list 
