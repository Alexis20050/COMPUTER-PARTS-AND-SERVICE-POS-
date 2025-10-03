from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QSpinBox, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from .service import InventoryService
from core.utils import format_currency, validate_price

class InventoryTab(QWidget):
    data_updated = pyqtSignal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.inventory_service = InventoryService(db)
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.search_items)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.search_items)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Category:"))
        search_layout.addWidget(self.category_filter)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Brand", "Category", "Price", "Stock"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Item")
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn = QPushButton("Edit Item")
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn = QPushButton("Delete Item")
        self.delete_btn.clicked.connect(self.delete_item)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def refresh_data(self):
        items = self.inventory_service.get_all_items()
        self.populate_table(items)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        categories = self.inventory_service.get_categories()
        for category in categories:
            self.category_filter.addItem(category)
    
    def populate_table(self, items):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.name))
            self.table.setItem(row, 2, QTableWidgetItem(item.brand))
            self.table.setItem(row, 3, QTableWidgetItem(item.category))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(item.price)))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.stock)))
    
    def search_items(self):
        search_term = self.search_input.text()
        category_filter = self.category_filter.currentText()
        if category_filter == "All Categories":
            category_filter = None
        items = self.inventory_service.search_items(search_term, category_filter)
        self.populate_table(items)
    
    def add_item(self):
        dialog = InventoryItemDialog(self)
        if dialog.exec():
            name, brand, category, price, stock = dialog.get_data()
            if self.inventory_service.add_item(name, brand, category, price, stock):
                QMessageBox.information(self, "Success", "Item added successfully!")
                self.refresh_data()
                self.data_updated.emit()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an item to edit.")
            return
        item_id = int(self.table.item(selected_row, 0).text())
        item = self.inventory_service.get_item_by_id(item_id)
        dialog = InventoryItemDialog(self, item)
        if dialog.exec():
            name, brand, category, price, stock = dialog.get_data()
            if self.inventory_service.update_item(item_id, name, brand, category, price, stock):
                QMessageBox.information(self, "Success", "Item updated successfully!")
                self.refresh_data()
                self.data_updated.emit()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an item to delete.")
            return
        item_id = int(self.table.item(selected_row, 0).text())
        item_name = self.table.item(selected_row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete '{item_name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.inventory_service.delete_item(item_id):
                QMessageBox.information(self, "Success", "Item deleted successfully!")
                self.refresh_data()
                self.data_updated.emit()

class InventoryItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Item" if not self.item else "Edit Item")
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(9999)
        
        if self.item:
            self.name_input.setText(self.item.name)
            self.brand_input.setText(self.item.brand)
            self.category_input.setText(self.item.category)
            self.price_input.setText(str(self.item.price))
            self.stock_input.setValue(self.item.stock)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Brand:", self.brand_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Price:", self.price_input)
        layout.addRow("Stock:", self.stock_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.brand_input.text().strip(),
            self.category_input.text().strip(),
            float(self.price_input.text()),
            self.stock_input.value()
        )
    
    def validate_and_accept(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        if not validate_price(price):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid price.")
            return
        self.accept()