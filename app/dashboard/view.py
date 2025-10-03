from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QTableWidget, QTableWidgetItem, QGroupBox,
                            QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from inventory.service import InventoryService
from sales.service import SalesService
from services.service import ServicesService
from core.utils import format_currency

class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.inventory_service = InventoryService(db)
        self.sales_service = SalesService(db)
        self.services_service = ServicesService(db)
        self.init_ui()
        self.refresh_data()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Stats grid
        stats_group = QGroupBox("Today's Overview")
        stats_layout = QGridLayout()
        
        self.sales_label = self.create_stat_box("Total Sales Today", "₱0.00")
        self.inventory_label = self.create_stat_box("Items in Inventory", "0")
        self.low_stock_label = self.create_stat_box("Low Stock Items", "0")
        self.services_label = self.create_stat_box("Available Services", "0")
        
        stats_layout.addWidget(self.sales_label, 0, 0)
        stats_layout.addWidget(self.inventory_label, 0, 1)
        stats_layout.addWidget(self.low_stock_label, 1, 0)
        stats_layout.addWidget(self.services_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Low stock alerts
        alerts_group = QGroupBox("Low Stock Alerts (Stock < 5)")
        alerts_layout = QVBoxLayout()
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Stock"])
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        alerts_layout.addWidget(self.low_stock_table)
        
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)
        
        self.setLayout(layout)
    
    def create_stat_box(self, title, value):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        group.setLayout(layout)
        return group
    
    def refresh_data(self):
        # Update stats
        total_sales = self.sales_service.get_total_sales_today()
        self.sales_label.layout().itemAt(0).widget().setText(format_currency(total_sales))
        
        inventory_count = len(self.inventory_service.get_all_items())
        self.inventory_label.layout().itemAt(0).widget().setText(str(inventory_count))
        
        low_stock_count = len(self.inventory_service.get_low_stock_items())
        self.low_stock_label.layout().itemAt(0).widget().setText(str(low_stock_count))
        
        services_count = len(self.services_service.get_all_services())
        self.services_label.layout().itemAt(0).widget().setText(str(services_count))
        
        # Update low stock table
        low_stock_items = self.inventory_service.get_low_stock_items()
        self.low_stock_table.setRowCount(len(low_stock_items))
        
        for row, item in enumerate(low_stock_items):
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(item.name))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(item.category))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(format_currency(item.price)))
            self.low_stock_table.setItem(row, 4, QTableWidgetItem(str(item.stock)))