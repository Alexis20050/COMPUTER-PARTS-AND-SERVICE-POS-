import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from core.db import DatabaseManager
from inventory.view import InventoryTab
from services.view import ServicesTab
from sales.view import SalesTab
from dashboard.view import DashboardTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Computer Parts and Services POS System")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tabs = QTabWidget()
        
        self.dashboard_tab = DashboardTab(self.db)
        self.inventory_tab = InventoryTab(self.db)
        self.services_tab = ServicesTab(self.db)
        self.sales_tab = SalesTab(self.db)
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.inventory_tab, "Inventory")
        self.tabs.addTab(self.services_tab, "Services")
        self.tabs.addTab(self.sales_tab, "Sales")
        
        layout.addWidget(self.tabs)
        
        self.inventory_tab.data_updated.connect(self.refresh_all)
        self.services_tab.data_updated.connect(self.refresh_all)
        self.sales_tab.data_updated.connect(self.refresh_all)
    
    def refresh_all(self):
        self.dashboard_tab.refresh_data()
        self.inventory_tab.refresh_data()
        self.services_tab.refresh_data()
        self.sales_tab.refresh_data()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()