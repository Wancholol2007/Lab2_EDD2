
class Airport:
    def __init__(self, code:str, name:str, city:str, country:str, latitude:float, longitude:float):
        self.code = code.strip().upper()
        self.name = name.strip()
        self.city = city.strip()
        self.country = country.strip()
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __repr__(self):
        return f"<Airport {self.code} - {self.city}, {self.country}>"
    
    def __eq__(self, other):
        if not isinstance(other, Airport):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)
    
    def info (self) -> dict:
        return {"Code": self.code, "Name": self.name, "City": self.city, "Country": self.country, "Latitude": self.latitude, "Longitude": self.longitude}
    