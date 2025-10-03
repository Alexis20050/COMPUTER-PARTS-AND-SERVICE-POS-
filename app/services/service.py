from core.db import DatabaseManager
from .models import Service

class ServicesService:
    def __init__(self, db):
        self.db = db
    
    def get_all_services(self):
        """Get all services"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services ORDER BY name")
        services = [Service.from_db_row(row) for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return services
    
    def get_service_by_id(self, service_id):
        """Get service by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = cursor.fetchone()
        # REMOVED: conn.close()
        return Service.from_db_row(row) if row else None
    
    def add_service(self, name, category, price, description):
        """Add new service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO services (name, category, price, description) VALUES (?, ?, ?, ?)",
            (name, category, price, description)
        )
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def update_service(self, service_id, name, category, price, description):
        """Update service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE services SET name=?, category=?, price=?, description=? WHERE id=?",
            (name, category, price, description, service_id)
        )
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def delete_service(self, service_id):
        """Delete service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM services WHERE id=?", (service_id,))
        conn.commit()
        # REMOVED: conn.close()
        return True
    
    def search_services(self, search_term, category_filter=None):
        """Search services"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM services WHERE name LIKE ?"
        params = [f'%{search_term}%']
        
        if category_filter and category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)
        
        query += " ORDER BY name"
        cursor.execute(query, params)
        services = [Service.from_db_row(row) for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return services
    
    def get_categories(self):
        """Get all unique categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM services WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        # REMOVED: conn.close()
        return categories