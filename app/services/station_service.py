from app.models import Station
from app import db

def get_all_stations():
    return Station.query.order_by(Station.id).all()

def create_station(name, type_pc, specs):
    new_station = Station(name=name, type=type_pc, specs=specs)
    db.session.add(new_station)
    db.session.commit()
    return new_station