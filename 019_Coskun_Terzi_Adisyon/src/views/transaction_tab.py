from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
    QDialog, QMessageBox, QHeaderView, QGroupBox, QTextEdit,
    QSpinBox, QFileDialog
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

import os
import datetime
import json

from src.models.database import Database
from src.utils.label_printer import LabelPrinter
from src.views.customer_tab import CustomerDialog
from src.utils.translator import translate

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

class TransactionTab(QWidget):
    """Tab for creating new transactions and printing labels"""
    def __init__(self):
        super().__init__()
        
        self.database = Database()
        self.label_printer = LabelPrinter()
        self.settings = load_settings()
        
        # Current transaction data
        self.current_customer = None
        self.transaction_items = []  # List of dicts with service, quantity, price
        self.total_amount = 0.0
        
        # Create UI
        layout = QVBoxLayout(self)
        
        # Customer section
        customer_group = QGroupBox(translate("Customer"))
        customer_layout = QVBoxLayout(customer_group)
        
        # Customer info
        self.customer_info = QLabel(translate("No customer selected"))
        customer_layout.addWidget(self.customer_info)
        
        # Customer buttons
        customer_button_layout = QHBoxLayout()
        
        self.select_customer_button = QPushButton(translate("Select Customer"))
        self.select_customer_button.clicked.connect(self.open_customer_tab)
        
        self.new_customer_button = QPushButton(translate("New Customer"))
        self.new_customer_button.clicked.connect(self.add_new_customer)
        
        customer_button_layout.addWidget(self.select_customer_button)
        customer_button_layout.addWidget(self.new_customer_button)
        customer_layout.addLayout(customer_button_layout)
        
        layout.addWidget(customer_group)
        
        # Services section
        services_group = QGroupBox(translate("Selected Services"))
        services_layout = QVBoxLayout(services_group)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels([
            translate("Service"), 
            translate("Description"), 
            translate("Price"), 
            translate("Quantity"), 
            translate("Total")
        ])
        
        self.services_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.services_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        services_layout.addWidget(self.services_table)
        
        # Service buttons
        service_button_layout = QHBoxLayout()
        
        self.add_service_button = QPushButton(translate("Add Service"))
        self.add_service_button.clicked.connect(self.open_service_tab)
        
        self.remove_service_button = QPushButton(translate("Remove Service"))
        self.remove_service_button.clicked.connect(self.remove_selected_service)
        
        service_button_layout.addWidget(self.add_service_button)
        service_button_layout.addWidget(self.remove_service_button)
        services_layout.addLayout(service_button_layout)
        
        # Total amount
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel(f"{translate('Total')}: $0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        services_layout.addLayout(total_layout)
        
        layout.addWidget(services_group)
        
        # Notes section
        notes_group = QGroupBox(translate("Notes"))
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(translate("Additional notes for this transaction..."))
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.preview_button = QPushButton(translate("Preview Label"))
        self.preview_button.clicked.connect(self.preview_label)
        
        self.print_button = QPushButton(translate("Print Label"))
        self.print_button.clicked.connect(self.print_label)
        
        self.complete_button = QPushButton(translate("Complete Transaction"))
        self.complete_button.clicked.connect(self.complete_transaction)
        
        self.clear_button = QPushButton(translate("Clear Form"))
        self.clear_button.clicked.connect(self.clear_form)
        
        action_layout.addWidget(self.preview_button)
        action_layout.addWidget(self.print_button)
        action_layout.addWidget(self.complete_button)
        action_layout.addWidget(self.clear_button)
        
        layout.addLayout(action_layout)
        
        # Set initial state
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements based on current transaction state"""
        # Always reload settings to ensure currency is up to date
        self.settings = load_settings()
        self.label_printer = LabelPrinter()  # Recreate with updated settings
        
        # Update customer info
        if self.current_customer:
            self.customer_info.setText(
                f"<b>{translate('Name')}:</b> {self.current_customer['name']} {self.current_customer['surname']}<br>"
                f"<b>{translate('Phone')}:</b> {self.current_customer.get('phone', translate('N/A'))}<br>"
                f"<b>{translate('Location')}:</b> {self.current_customer.get('location', translate('N/A'))}"
            )
        else:
            self.customer_info.setText(translate("No customer selected"))
        
        # Update services table
        self.services_table.setRowCount(len(self.transaction_items))
        
        for i, item in enumerate(self.transaction_items):
            service = item["service"]
            quantity = item["quantity"]
            price = service["price"]
            total = price * quantity
            
            self.services_table.setItem(i, 0, QTableWidgetItem(service["name"]))
            self.services_table.setItem(i, 1, QTableWidgetItem(service.get("description", "")))
            
            price_item = QTableWidgetItem(format_price(price, self.settings))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.services_table.setItem(i, 2, price_item)
            
            quantity_item = QTableWidgetItem(str(quantity))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(i, 3, quantity_item)
            
            total_item = QTableWidgetItem(format_price(total, self.settings))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.services_table.setItem(i, 4, total_item)
        
        # Update total amount
        self.calculate_total()
        self.total_label.setText(f"{translate('Total')}: {format_price(self.total_amount, self.settings)}")
        
        # Update button states
        has_customer = self.current_customer is not None
        has_services = len(self.transaction_items) > 0
        
        self.preview_button.setEnabled(has_customer and has_services)
        self.print_button.setEnabled(has_customer and has_services)
        self.complete_button.setEnabled(has_customer and has_services)
        self.remove_service_button.setEnabled(has_services)
    
    def set_customer(self, customer):
        """Set the current customer for the transaction"""
        self.current_customer = customer
        self.update_ui()
    
    def add_service(self, service, quantity=1):
        """Add a service to the transaction"""
        # Check if service already exists in transaction
        for item in self.transaction_items:
            if item["service"]["id"] == service["id"]:
                # Update quantity
                item["quantity"] += quantity
                self.update_ui()
                return
        
        # Add new service
        self.transaction_items.append({
            "service": service,
            "quantity": quantity
        })
        
        self.update_ui()
    
    def remove_selected_service(self):
        """Remove the selected service from the transaction"""
        selected_rows = self.services_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if 0 <= row < len(self.transaction_items):
            del self.transaction_items[row]
            self.update_ui()
    
    def calculate_total(self):
        """Calculate the total amount for the transaction"""
        self.total_amount = sum(
            item["service"]["price"] * item["quantity"]
            for item in self.transaction_items
        )
    
    def open_customer_tab(self):
        """Signal the main window to open the customer tab"""
        # Find the main window (parent of the tab widget)
        main_window = self.window()
        if hasattr(main_window, 'tab_widget'):
            main_window.tab_widget.setCurrentIndex(1)  # Switch to customers tab
    
    def open_service_tab(self):
        """Signal the main window to open the service tab"""
        # Find the main window (parent of the tab widget)
        main_window = self.window()
        if hasattr(main_window, 'tab_widget'):
            main_window.tab_widget.setCurrentIndex(2)  # Switch to services tab
    
    def add_new_customer(self):
        """Open dialog to add a new customer"""
        dialog = CustomerDialog(self)
        if dialog.exec_():
            # Get the newly added customer
            conn = self.database.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM customers ORDER BY id DESC LIMIT 1"
            )
            customer = cursor.fetchone()
            conn.close()
            
            if customer:
                self.set_customer(dict(customer))
    
    def preview_label(self):
        """Generate and show a preview of the label"""
        if not self.current_customer or not self.transaction_items:
            QMessageBox.warning(self, translate("Cannot Preview"), translate("Customer and at least one service are required."))
            return
        
        try:
            notes = self.notes_edit.toPlainText().strip()
            
            # Prepare services for label
            label_services = [
                {
                    "name": item["service"]["name"],
                    "quantity": item["quantity"],
                    "price": item["service"]["price"]
                }
                for item in self.transaction_items
            ]
            
            # Generate preview PDF
            pdf_path = self.label_printer.generate_label_preview(
                self.current_customer,
                label_services,
                notes
            )
            
            # Open the PDF file
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
            
        except Exception as e:
            QMessageBox.critical(self, translate("Preview Error"), f"{translate('Failed to generate preview:')} {str(e)}")
    
    def print_label(self):
        """Print the label"""
        if not self.current_customer or not self.transaction_items:
            QMessageBox.warning(self, translate("Cannot Print"), translate("Customer and at least one service are required."))
            return
        
        # Check if we should confirm printing based on settings
        confirm_on_print = self.settings.get("ui", {}).get("confirm_on_print", True)
        proceed_with_print = True
        
        if confirm_on_print:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, translate('Confirm Printing'),
                translate("Are you sure you want to print the label?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                proceed_with_print = False
        
        if proceed_with_print:
            try:
                notes = self.notes_edit.toPlainText().strip()
                
                # Prepare services for label
                label_services = [
                    {
                        "name": item["service"]["name"],
                        "quantity": item["quantity"],
                        "price": item["service"]["price"]
                    }
                    for item in self.transaction_items
                ]
                
                # Generate PDF
                pdf_path = self.label_printer.generate_label_pdf(
                    self.current_customer,
                    label_services,
                    notes
                )
                
                # Open the PDF file (for now, instead of direct printing)
                QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
                
                # Complete the transaction after printing
                self.complete_transaction()
                
            except Exception as e:
                QMessageBox.critical(self, translate("Print Error"), f"{translate('Failed to print label:')} {str(e)}")
    
    def complete_transaction(self):
        """Save the transaction to the database"""
        if not self.current_customer or not self.transaction_items:
            QMessageBox.warning(self, translate("Cannot Complete"), translate("Customer and at least one service are required."))
            return
        
        try:
            notes = self.notes_edit.toPlainText().strip()
            
            # Create transaction in database
            transaction_id = self.database.create_transaction(
                self.current_customer["id"],
                self.total_amount,
                notes
            )
            
            # Add transaction items
            for item in self.transaction_items:
                self.database.add_transaction_item(
                    transaction_id,
                    item["service"]["id"],
                    item["quantity"],
                    item["service"]["price"]
                )
            
            QMessageBox.information(self, translate("Success"), translate("Transaction completed successfully."))
            
            # Clear the form for next transaction
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(self, translate("Error"), f"{translate('Failed to save transaction:')} {str(e)}")
    
    def clear_form(self):
        """Clear the form for a new transaction"""
        self.current_customer = None
        self.transaction_items = []
        self.total_amount = 0.0
        self.notes_edit.clear()
        self.update_ui()
    
    def reload_settings(self):
        """Reload settings and update UI"""
        self.settings = load_settings()
        self.label_printer = LabelPrinter()
        
        # Update all text elements with current translations
        # Customer section
        self.customer_info.setText(translate("No customer selected") if not self.current_customer else 
            f"<b>{translate('Name')}:</b> {self.current_customer['name']} {self.current_customer['surname']}<br>"
            f"<b>{translate('Phone')}:</b> {self.current_customer.get('phone', translate('N/A'))}<br>"
            f"<b>{translate('Location')}:</b> {self.current_customer.get('location', translate('N/A'))}")
        
        self.select_customer_button.setText(translate("Select Customer"))
        self.new_customer_button.setText(translate("New Customer"))
        
        # Services table
        self.services_table.setHorizontalHeaderLabels([
            translate("Service"), 
            translate("Description"), 
            translate("Price"), 
            translate("Quantity"), 
            translate("Total")
        ])
        
        # Service buttons
        self.add_service_button.setText(translate("Add Service"))
        self.remove_service_button.setText(translate("Remove Service"))
        
        # Action buttons
        self.preview_button.setText(translate("Preview Label"))
        self.print_button.setText(translate("Print Label"))
        self.complete_button.setText(translate("Complete Transaction"))
        self.clear_button.setText(translate("Clear Form"))
        
        # Set placeholder for notes
        self.notes_edit.setPlaceholderText(translate("Additional notes for this transaction..."))
        
        # Refresh the full UI
        self.update_ui() 