from app.models import Station
from app import db

def get_all_stations():
    return Station.query.order_by(Station.id).all()

# 1. On ajoute price_per_hour dans les paramètres (avec 5.0 par défaut au cas où)
def create_station(name, type_pc, specs, price_per_hour=5.0, image_url='https://placehold.co/600x400/1e1e1e/FFF?text=PC+Gamer'):
    
    # 2. On l'ajoute lors de la création de l'objet Station
    new_station = Station(
        name=name, 
        type=type_pc, 
        specs=specs,
        price_per_hour=price_per_hour,
        image_url=image_url
    )
    
    db.session.add(new_station)
    db.session.commit()
    return new_station

def delete_station(station_id):
    station = Station.query.get(station_id)
    if station:
        db.session.delete(station)
        db.session.commit()
        return True
    return False