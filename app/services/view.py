from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QTextEdit, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from .service import ServicesService
from core.utils import format_currency, validate_price

class ServicesTab(QWidget):
    data_updated = pyqtSignal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.services_service = ServicesService(db)
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search services...")
        self.search_input.textChanged.connect(self.search_services)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.search_services)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Category:"))
        search_layout.addWidget(self.category_filter)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Description"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Service")
        self.add_btn.clicked.connect(self.add_service)
        self.edit_btn = QPushButton("Edit Service")
        self.edit_btn.clicked.connect(self.edit_service)
        self.delete_btn = QPushButton("Delete Service")
        self.delete_btn.clicked.connect(self.delete_service)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def refresh_data(self):
        services = self.services_service.get_all_services()
        self.populate_table(services)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        categories = self.services_service.get_categories()
        for category in categories:
            self.category_filter.addItem(category)
    
    def populate_table(self, services):
        self.table.setRowCount(len(services))
        for row, service in enumerate(services):
            self.table.setItem(row, 0, QTableWidgetItem(str(service.id)))
            self.table.setItem(row, 1, QTableWidgetItem(service.name))
            self.table.setItem(row, 2, QTableWidgetItem(service.category))
            self.table.setItem(row, 3, QTableWidgetItem(format_currency(service.price)))
            self.table.setItem(row, 4, QTableWidgetItem(service.description))
    
    def search_services(self):
        search_term = self.search_input.text()
        category_filter = self.category_filter.currentText()
        if category_filter == "All Categories":
            category_filter = None
        services = self.services_service.search_services(search_term, category_filter)
        self.populate_table(services)
    
    def add_service(self):
        dialog = ServiceDialog(self)
        if dialog.exec():
            name, category, price, description = dialog.get_data()
            if self.services_service.add_service(name, category, price, description):
                QMessageBox.information(self, "Success", "Service added successfully!")
                self.refresh_data()
                self.data_updated.emit()
    
    def edit_service(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select a service to edit.")
            return
        service_id = int(self.table.item(selected_row, 0).text())
        service = self.services_service.get_service_by_id(service_id)
        dialog = ServiceDialog(self, service)
        if dialog.exec():
            name, category, price, description = dialog.get_data()
            if self.services_service.update_service(service_id, name, category, price, description):
                QMessageBox.information(self, "Success", "Service updated successfully!")
                self.refresh_data()
                self.data_updated.emit()
    
    def delete_service(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select a service to delete.")
            return
        service_id = int(self.table.item(selected_row, 0).text())
        service_name = self.table.item(selected_row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete '{service_name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.services_service.delete_service(service_id):
                QMessageBox.information(self, "Success", "Service deleted successfully!")
                self.refresh_data()
                self.data_updated.emit()

class ServiceDialog(QDialog):
    def __init__(self, parent=None, service=None):
        super().__init__(parent)
        self.service = service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add Service" if not self.service else "Edit Service")
        self.resize(500, 400)
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(150)
        
        if self.service:
            self.name_input.setText(self.service.name)
            self.category_input.setText(self.service.category)
            self.price_input.setText(str(self.service.price))
            self.description_input.setText(self.service.description)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Price:", self.price_input)
        layout.addRow("Description:", self.description_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.category_input.text().strip(),
            float(self.price_input.text()),
            self.description_input.toPlainText().strip()
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