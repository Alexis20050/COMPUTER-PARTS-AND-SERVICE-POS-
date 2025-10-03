class Service:
    def __init__(self, id, name, category, price, description):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.description = description
    
    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3], row[4])