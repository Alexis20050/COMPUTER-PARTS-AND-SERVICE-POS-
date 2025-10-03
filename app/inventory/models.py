class InventoryItem:
    def __init__(self, id, name, brand, category, price, stock):
        self.id = id
        self.name = name
        self.brand = brand
        self.category = category
        self.price = price
        self.stock = stock
    
    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3], row[4], row[5])