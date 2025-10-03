from core.db import DatabaseManager
from .models import InventoryItem

class InventoryService:
    def __init__(self, db):
        self.db = db
    
    def get_all_items(self):
        """Get all inventory items"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY name")
        items = [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return items
    
    def get_item_by_id(self, item_id):
        """Get item by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        # REMOVED: conn.close()
        return InventoryItem.from_db_row(row) if row else None
    
    def add_item(self, name, brand, category, price, stock):
        """Add new inventory item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, brand, category, price, stock) VALUES (?, ?, ?, ?, ?)",
            (name, brand, category, price, stock)
        )
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def update_item(self, item_id, name, brand, category, price, stock):
        """Update inventory item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventory SET name=?, brand=?, category=?, price=?, stock=? WHERE id=?",
            (name, brand, category, price, stock, item_id)
        )
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def delete_item(self, item_id):
        """Delete inventory item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def search_items(self, search_term, category_filter=None):
        """Search inventory items"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM inventory WHERE name LIKE ?"
        params = [f'%{search_term}%']
        
        if category_filter and category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)
        
        query += " ORDER BY name"
        cursor.execute(query, params)
        items = [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return items
    
    def get_low_stock_items(self, threshold=5):
        """Get items with low stock"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE stock < ? ORDER BY stock", (threshold,))
        items = [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return items
    
    def get_categories(self):
        """Get all unique categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM inventory WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return categories
    
    def update_stock(self, item_id, new_stock):
        """Update item stock"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET stock=? WHERE id=?", (new_stock, item_id))
        conn.commit()
        # REMOVED: conn.close()
        return True