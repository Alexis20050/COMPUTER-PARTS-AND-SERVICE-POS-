from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
                            QLabel, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QSpinBox, QHeaderView, QSplitter, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal

from .service import SalesService
from .models import CartItem
from inventory.service import InventoryService
from services.service import ServicesService
from core.utils import format_currency

class SalesTab(QWidget):
    data_updated = pyqtSignal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.sales_service = SalesService(db)
        self.inventory_service = InventoryService(db)
        self.services_service = ServicesService(db)
        self.cart = []
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # CUSTOMER NAME INPUT FIELD - SIMPLE VERSION
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer Name:"))
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Enter customer name (optional)")
        self.customer_input.setMinimumWidth(300)
        customer_layout.addWidget(self.customer_input)
        customer_layout.addStretch()
        
        main_layout.addLayout(customer_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Products and Services
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Items", "Services"])
        self.type_combo.currentTextChanged.connect(self.refresh_available_items)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        left_layout.addLayout(type_layout)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items or services...")
        self.search_input.textChanged.connect(self.search_items)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Available items table
        self.available_table = QTableWidget()
        self.available_table.setColumnCount(4)
        self.available_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Price"])
        self.available_table.doubleClicked.connect(self.add_to_cart_from_table)
        left_layout.addWidget(self.available_table)
        
        # Add to cart controls
        add_cart_layout = QHBoxLayout()
        add_cart_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        self.quantity_spin.setValue(1)
        add_cart_layout.addWidget(self.quantity_spin)
        
        self.add_to_cart_btn = QPushButton("Add to Cart")
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        add_cart_layout.addWidget(self.add_to_cart_btn)
        add_cart_layout.addStretch()
        left_layout.addLayout(add_cart_layout)
        
        # Right side - Cart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Price", "Qty", "Total"])
        right_layout.addWidget(self.cart_table)
        
        # Total and buttons
        total_layout = QHBoxLayout()
        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        
        self.clear_cart_btn = QPushButton("Clear Cart")
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        total_layout.addWidget(self.clear_cart_btn)
        
        self.checkout_btn = QPushButton("Checkout")
        self.checkout_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.checkout_btn.clicked.connect(self.checkout)
        total_layout.addWidget(self.checkout_btn)
        
        right_layout.addLayout(total_layout)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def refresh_data(self):
        self.refresh_available_items()
        self.update_cart_display()
    
    def refresh_available_items(self):
        item_type = self.type_combo.currentText()
        if item_type == "Items":
            items = self.inventory_service.get_all_items()
            self.populate_available_table(items, "item")
        else:
            services = self.services_service.get_all_services()
            self.populate_available_table(services, "service")
    
    def populate_available_table(self, items, item_type):
        self.available_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.available_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.available_table.setItem(row, 1, QTableWidgetItem(item.name))
            self.available_table.setItem(row, 2, QTableWidgetItem(item_type.title()))
            price = item.price
            self.available_table.setItem(row, 3, QTableWidgetItem(format_currency(price)))
    
    def search_items(self):
        search_term = self.search_input.text()
        item_type = self.type_combo.currentText()
        if item_type == "Items":
            items = self.inventory_service.search_items(search_term)
            self.populate_available_table(items, "item")
        else:
            services = self.services_service.search_services(search_term)
            self.populate_available_table(services, "service")
    
    def add_to_cart(self):
        selected_row = self.available_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select an item to add to cart.")
            return
        
        item_id = int(self.available_table.item(selected_row, 0).text())
        item_name = self.available_table.item(selected_row, 1).text()
        item_type = self.available_table.item(selected_row, 2).text().lower()
        price_text = self.available_table.item(selected_row, 3).text().replace('₱', '')
        price = float(price_text)
        quantity = self.quantity_spin.value()
        
        # Check stock for inventory items
        if item_type == "item":
            item = self.inventory_service.get_item_by_id(item_id)
            if item.stock < quantity:
                QMessageBox.warning(self, "Warning", f"Not enough stock! Only {item.stock} available.")
                return
        
        cart_item = CartItem(item_id, item_name, item_type, price, quantity)
        self.cart.append(cart_item)
        self.update_cart_display()
        self.quantity_spin.setValue(1)
    
    def add_to_cart_from_table(self, index):
        self.add_to_cart()
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item.name))
            self.cart_table.setItem(row, 2, QTableWidgetItem(item.type.title()))
            self.cart_table.setItem(row, 3, QTableWidgetItem(format_currency(item.price)))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(item.quantity)))
            self.cart_table.setItem(row, 5, QTableWidgetItem(format_currency(item.total)))
            total += item.total
        self.total_label.setText(f"Total: {format_currency(total)}")
    
    def clear_cart(self):
        if self.cart:
            reply = QMessageBox.question(self, "Clear Cart", "Clear the cart?")
            if reply == QMessageBox.StandardButton.Yes:
                self.cart.clear()
                self.update_cart_display()
                self.customer_input.clear()  # Clear customer name too
    
    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "Warning", "Cart is empty!")
            return
        
        total = sum(item.total for item in self.cart)
        customer_name = self.customer_input.text().strip()
        
        # Create confirmation message with customer name
        confirm_message = f"Total: {format_currency(total)}\n"
        if customer_name:
            confirm_message += f"Customer: {customer_name}\n"
        confirm_message += "\nProceed with checkout?"
        
        reply = QMessageBox.question(self, "Confirm Checkout", confirm_message)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.sales_service.record_sale(self.cart, total, customer_name):
                self.show_receipt(customer_name)
                self.cart.clear()
                self.update_cart_display()
                self.customer_input.clear()  # Clear customer name after checkout
                self.data_updated.emit()
                QMessageBox.information(self, "Success", "Sale completed successfully!")
    
    def show_receipt(self, customer_name):
        receipt_dialog = ReceiptDialog(self.cart, customer_name, self)
        receipt_dialog.exec()

class ReceiptDialog(QDialog):
    def __init__(self, cart_items, customer_name, parent=None):
        super().__init__(parent)
        self.cart_items = cart_items
        self.customer_name = customer_name
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Receipt")
        self.resize(400, 500)
        layout = QVBoxLayout()
        
        header_label = QLabel("COMPUTER PARTS POS - RECEIPT")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header_label)
        
        from core.utils import get_current_date
        date_label = QLabel(f"Date: {get_current_date()}")
        layout.addWidget(date_label)
        
        # CUSTOMER NAME ON RECEIPT
        if self.customer_name:
            customer_label = QLabel(f"Customer: {self.customer_name}")
            customer_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(customer_label)
        
        layout.addWidget(QLabel("=" * 50))
        
        items_text = QTextEdit()
        items_text.setReadOnly(True)
        
        receipt_text = ""
        total = 0
        
        for item in self.cart_items:
            receipt_text += f"{item.name}\n"
            receipt_text += f"  {item.quantity} x {format_currency(item.price)} = {format_currency(item.total)}\n"
            total += item.total
        
        receipt_text += "\n" + "=" * 50 + "\n"
        receipt_text += f"TOTAL: {format_currency(total)}\n"
        receipt_text += "=" * 50 + "\n"
        receipt_text += "Thank you for your business!"
        
        items_text.setText(receipt_text)
        layout.addWidget(items_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)
        self.setLayout(layout)