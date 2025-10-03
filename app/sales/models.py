import json

class Sale:
    def __init__(self, id, sale_date, total_amount, items):
        self.id = id
        self.sale_date = sale_date
        self.total_amount = total_amount
        self.items = items
    
    @classmethod
    def from_db_row(cls, row):
        return cls(row[0], row[1], row[2], row[3])

class CartItem:
    def __init__(self, id, name, type, price, quantity=1):
        self.id = id
        self.name = name
        self.type = type  # 'item' or 'service'
        self.price = price
        self.quantity = quantity
    
    @property
    def total(self):
        return self.price * self.quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'price': self.price,
            'quantity': self.quantity,
            'total': self.total
        }