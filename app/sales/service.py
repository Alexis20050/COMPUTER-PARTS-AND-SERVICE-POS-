from core.db import DatabaseManager
from core.utils import serialize_items, get_current_date
from .models import Sale
import sqlite3

class SalesService:
    def __init__(self, db):
        self.db = db
    
    def record_sale(self, items, total_amount, customer_name=""):
        """Record a new sale with customer name"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Serialize items
            items_json = serialize_items([item.to_dict() for item in items])
            
            # Insert sale record
            cursor.execute(
                "INSERT INTO sales (sale_date, total_amount, items, customer_name) VALUES (?, ?, ?, ?)",
                (get_current_date(), total_amount, items_json, customer_name)
            )
            
            # Update inventory stock
            for item in items:
                if item.type == 'item':
                    self._update_inventory_stock(cursor, item.id, item.quantity)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error recording sale: {e}")
            return False
    
    def _update_inventory_stock(self, cursor, item_id, quantity_sold):
        """Update inventory stock using existing cursor"""
        cursor.execute("SELECT stock FROM inventory WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        if result:
            current_stock = result[0]
            new_stock = current_stock - quantity_sold
            if new_stock < 0:
                new_stock = 0
            cursor.execute("UPDATE inventory SET stock = ? WHERE id = ?", (new_stock, item_id))
    
    def get_today_sales(self):
        """Get sales for today"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales WHERE sale_date = ?", (get_current_date(),))
        sales = [Sale.from_db_row(row) for row in cursor.fetchall()]
        return sales
    
    def get_total_sales_today(self):
        """Get total sales amount for today"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_amount) FROM sales WHERE sale_date = ?", (get_current_date(),))
        result = cursor.fetchone()[0]
        return result if result else 0.0
    
    def get_all_sales(self):
        """Get all sales"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales ORDER BY sale_date DESC, id DESC")
        sales = [Sale.from_db_row(row) for row in cursor.fetchall()]
        return sales