import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
    QDialog, QMessageBox, QHeaderView, QTabWidget, QGroupBox,
    QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from src.models.database import Database
from src.utils.translator import translate, reload_translations

# Import function to format currency
def load_settings():
    """Load settings from file"""
    settings_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "settings.json"
    )
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def format_price(price, settings=None):
    """Format price with currency symbol based on settings"""
    if settings is None:
        settings = load_settings()
    
    currency_symbol = settings.get("currency", {}).get("symbol", "$")
    currency_position = settings.get("currency", {}).get("position", "before")
    
    if currency_position == "before":
        return f"{currency_symbol}{price:.2f}"
    else:
        return f"{price:.2f}{currency_symbol}"

class CustomerDialog(QDialog):
    """Dialog for adding or editing a customer"""
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        
        self.customer = customer
        self.database = Database()
        
        if customer:
            self.setWindowTitle(translate("Edit Customer"))
        else:
            self.setWindowTitle(translate("Add New Customer"))
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow(translate("Name:"), self.name_edit)
        
        # Surname field
        self.surname_edit = QLineEdit()
        form_layout.addRow(translate("Surname:"), self.surname_edit)
        
        # Phone field
        self.phone_edit = QLineEdit()
        form_layout.addRow(translate("Phone:"), self.phone_edit)
        
        # Location field
        self.location_edit = QLineEdit()
        form_layout.addRow(translate("Location:"), self.location_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(translate("Save"))
        self.save_button.clicked.connect(self.save_customer)
        
        self.cancel_button = QPushButton(translate("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # If editing, populate fields
        if customer:
            self.name_edit.setText(customer["name"])
            self.surname_edit.setText(customer["surname"])
            if customer.get("phone"):
                self.phone_edit.setText(customer["phone"])
            if customer.get("location"):
                self.location_edit.setText(customer["location"])
    
    def save_customer(self):
        """Save customer data to database"""
        name = self.name_edit.text().strip()
        surname = self.surname_edit.text().strip()
        phone = self.phone_edit.text().strip()
        location = self.location_edit.text().strip()
        
        # Validate
        if not name:
            QMessageBox.warning(self, translate("Missing Data"), translate("Name is required."))
            return
            
        if not surname:
            QMessageBox.warning(self, translate("Missing Data"), translate("Surname is required."))
            return
        
        try:
            if self.customer:  # Update existing
                self.database.update_customer(
                    self.customer["id"], name, surname, phone, location
                )
            else:  # Add new
                self.database.add_customer(name, surname, phone, location)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, translate("Error"), f"{translate('Failed to save customer:')} {str(e)}")
    
    def reload_settings(self):
        """Reload settings and update translations"""
        # Update window title
        if self.customer:
            self.setWindowTitle(translate("Edit Customer"))
        else:
            self.setWindowTitle(translate("Add New Customer"))
        
        # Update form labels
        form_layout = self.findChild(QFormLayout)
        if form_layout:
            # Update the form labels
            for i in range(form_layout.rowCount()):
                label_item = form_layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label = label_item.widget()
                    if label.text() == "Name:":
                        label.setText(translate("Name:"))
                    elif label.text() == "Surname:":
                        label.setText(translate("Surname:"))
                    elif label.text() == "Phone:":
                        label.setText(translate("Phone:"))
                    elif label.text() == "Location:":
                        label.setText(translate("Location:"))
        
        # Update buttons
        self.save_button.setText(translate("Save"))
        self.cancel_button.setText(translate("Cancel"))

class CustomerHistoryDialog(QDialog):
    """Dialog for viewing customer history"""
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        
        self.settings = load_settings()
        self.customer = customer  # Store the customer for reload_settings
        
        self.setWindowTitle(f"{translate('History -')} {customer['name']} {customer['surname']}")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Customer info section
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"<b>{translate('Name')}:</b> {customer['name']} {customer['surname']}"))
        if customer.get('phone'):
            info_layout.addWidget(QLabel(f"<b>{translate('Phone')}:</b> {customer['phone']}"))
        if customer.get('location'):
            info_layout.addWidget(QLabel(f"<b>{translate('Location')}:</b> {customer['location']}"))
        layout.addLayout(info_layout)
        
        # Transaction history table
        self.history_tabs = QTabWidget()
        layout.addWidget(self.history_tabs)
        
        # Get transaction history from database
        database = Database()
        transactions = database.get_customer_history(customer['id'])
        
        # If no transactions, show a message
        if not transactions:
            no_history = QWidget()
            no_layout = QVBoxLayout(no_history)
            no_layout.addWidget(QLabel(translate("No transaction history available.")))
            self.history_tabs.addTab(no_history, translate("No History"))
            
        # Add a tab for each transaction
        for transaction in transactions:
            transaction_tab = QWidget()
            tab_layout = QVBoxLayout(transaction_tab)
            
            # Transaction details
            details_group = QGroupBox(translate("Transaction Details"))
            details_layout = QFormLayout(details_group)
            details_layout.addRow(translate("Date:"), QLabel(transaction['created_at']))
            
            # Use the format_price function to format the total with correct currency
            total_formatted = format_price(transaction['total_amount'], self.settings)
            details_layout.addRow(translate("Total Amount:"), QLabel(total_formatted))
            
            if transaction.get('note'):
                note_edit = QTextEdit()
                note_edit.setPlainText(transaction['note'])
                note_edit.setReadOnly(True)
                note_edit.setMaximumHeight(60)
                details_layout.addRow(translate("Note:"), note_edit)
            
            tab_layout.addWidget(details_group)
            
            # Items table
            items_group = QGroupBox(translate("Items"))
            items_layout = QVBoxLayout(items_group)
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels([
                translate("Service"), 
                translate("Description"), 
                translate("Quantity"), 
                translate("Price")
            ])
            
            items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            items_table.setRowCount(len(transaction['items']))
            
            for i, item in enumerate(transaction['items']):
                items_table.setItem(i, 0, QTableWidgetItem(item['service_name']))
                items_table.setItem(i, 1, QTableWidgetItem(item['description']))
                items_table.setItem(i, 2, QTableWidgetItem(str(item['quantity'])))
                
                # Format individual item prices with correct currency
                price_formatted = format_price(item['price'], self.settings)
                items_table.setItem(i, 3, QTableWidgetItem(price_formatted))
            
            items_layout.addWidget(items_table)
            tab_layout.addWidget(items_group)
            
            # Add the tab
            date_str = transaction['created_at'].split(' ')[0]
            self.history_tabs.addTab(transaction_tab, f"{translate('Transaction')} {date_str}")
        
        # Close button
        self.close_button = QPushButton(translate("Close"))
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
    
    def reload_settings(self):
        """Reload settings and update translations"""
        self.settings = load_settings()
        
        # Update window title
        if hasattr(self, 'customer'):
            self.setWindowTitle(f"{translate('History -')} {self.customer['name']} {self.customer['surname']}")
        
        # Update the close button text
        self.close_button.setText(translate("Close"))
        
        # Update tab labels if tabs exist
        if hasattr(self, 'history_tabs'):
            # Check for "No History" tab
            if self.history_tabs.count() == 1 and not hasattr(self, 'transactions_by_id'):
                self.history_tabs.setTabText(0, translate("No History"))

class CustomerTab(QWidget):
    """Customer management tab"""
    customer_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.database = Database()
        
        # Create a timer for delayed search while typing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.search_customers)
        
        layout = QVBoxLayout(self)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(translate("Search:")))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(translate("Enter name, surname or phone"))
        self.search_edit.returnPressed.connect(self.search_customers)
        # Connect text changed signal to start the search timer
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_edit)
        
        self.search_button = QPushButton(translate("Search"))
        self.search_button.clicked.connect(self.search_customers)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Customers table - remove ID column
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)  # Reduced from 5 to 4
        self.customers_table.setHorizontalHeaderLabels([
            translate("Name"), 
            translate("Surname"), 
            translate("Phone"), 
            translate("Location")
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.cellDoubleClicked.connect(self.on_customer_double_clicked)
        
        layout.addWidget(self.customers_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(translate("Add Customer"))
        self.add_button.clicked.connect(self.add_customer)
        
        self.edit_button = QPushButton(translate("Edit Customer"))
        self.edit_button.clicked.connect(self.edit_customer)
        
        self.view_history_button = QPushButton(translate("View History"))
        self.view_history_button.clicked.connect(self.view_customer_history)
        
        self.select_button = QPushButton(translate("Select for Transaction"))
        self.select_button.clicked.connect(self.select_customer)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.view_history_button)
        button_layout.addWidget(self.select_button)
        
        layout.addLayout(button_layout)
        
        # Initial load
        self.load_customers()
        
    def reload_settings(self):
        """Reload settings and update UI with new translations"""
        # Update UI elements with new translations
        self.search_button.setText(translate("Search"))
        self.search_edit.setPlaceholderText(translate("Enter name, surname or phone"))
        
        # Update table headers
        self.customers_table.setHorizontalHeaderLabels([
            translate("Name"), 
            translate("Surname"), 
            translate("Phone"), 
            translate("Location")
        ])
        
        # Update buttons
        self.add_button.setText(translate("Add Customer"))
        self.edit_button.setText(translate("Edit Customer"))
        self.view_history_button.setText(translate("View History"))
        self.select_button.setText(translate("Select for Transaction"))
        
        # Refresh display
        self.load_customers()
    
    def on_search_text_changed(self):
        """Handle search text changes and start the search timer"""
        # Reset the timer to delay the search by 300ms
        # This prevents excessive database queries while typing
        self.search_timer.start(300)  # 300ms delay
    
    def load_customers(self):
        """Load all customers into the table"""
        customers = self.database.search_customers("")
        self.populate_table(customers)
    
    def search_customers(self):
        """Search customers based on search text"""
        search_text = self.search_edit.text().strip()
        customers = self.database.search_customers(search_text)
        self.populate_table(customers)
    
    def populate_table(self, customers):
        """Populate table with customers"""
        self.customers_table.setRowCount(len(customers))
        
        for i, customer in enumerate(customers):
            # Start at column 0 for Name (skip ID column)
            self.customers_table.setItem(i, 0, QTableWidgetItem(customer["name"]))
            self.customers_table.setItem(i, 1, QTableWidgetItem(customer["surname"]))
            self.customers_table.setItem(i, 2, QTableWidgetItem(customer.get("phone", "")))
            self.customers_table.setItem(i, 3, QTableWidgetItem(customer.get("location", "")))
            
            # Store customer ID as item data for row 0
            self.customers_table.item(i, 0).setData(Qt.UserRole, customer["id"])
    
    def get_selected_customer(self):
        """Get the currently selected customer from the table"""
        selected_rows = self.customers_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, translate("No Selection"), translate("Please select a customer."))
            return None
        
        row = selected_rows[0].row()
        customer_id = int(self.customers_table.item(row, 0).data(Qt.UserRole))
        
        return self.database.get_customer(customer_id)
    
    def add_customer(self):
        """Open dialog to add a new customer"""
        dialog = CustomerDialog(self)
        if dialog.exec_():
            self.load_customers()
    
    def edit_customer(self):
        """Open dialog to edit the selected customer"""
        customer = self.get_selected_customer()
        if customer:
            dialog = CustomerDialog(self, customer)
            if dialog.exec_():
                self.load_customers()
    
    def view_customer_history(self):
        """Open dialog to view selected customer's history"""
        customer = self.get_selected_customer()
        if customer:
            dialog = CustomerHistoryDialog(self, customer)
            dialog.exec_()
    
    def select_customer(self):
        """Emit signal with selected customer for transaction"""
        customer = self.get_selected_customer()
        if customer:
            self.customer_selected.emit(customer)
    
    def on_customer_double_clicked(self, row, column):
        """Handle double-click on customer row"""
        customer_id = int(self.customers_table.item(row, 0).data(Qt.UserRole))
        customer = self.database.get_customer(customer_id)
        
        if customer:
            self.customer_selected.emit(customer) 