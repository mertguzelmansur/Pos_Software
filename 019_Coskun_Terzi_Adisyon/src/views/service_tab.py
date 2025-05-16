from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
    QDialog, QMessageBox, QHeaderView, QDoubleSpinBox, QSpinBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import os
import json

from src.models.database import Database
from src.utils.translator import translate, reload_translations

# Import or define the format_price function
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

class ServiceDialog(QDialog):
    """Dialog for adding or editing a service"""
    def __init__(self, parent=None, service=None):
        super().__init__(parent)
        
        self.service = service
        self.database = Database()
        self.settings = load_settings()
        
        if service:
            self.setWindowTitle(translate("Edit Service"))
        else:
            self.setWindowTitle(translate("Add New Service"))
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow(translate("Name:"), self.name_edit)
        
        # Description field
        self.description_edit = QLineEdit()
        form_layout.addRow(translate("Description:"), self.description_edit)
        
        # Price field
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setRange(0, 9999.99)
        self.price_edit.setDecimals(2)
        self.price_edit.setSingleStep(1.0)
        
        # Set currency symbol from settings
        currency_symbol = self.settings.get("currency", {}).get("symbol", "$")
        currency_position = self.settings.get("currency", {}).get("position", "before")
        if currency_position == "before":
            self.price_edit.setPrefix(currency_symbol)
        else:
            self.price_edit.setSuffix(" " + currency_symbol)
            
        form_layout.addRow(translate("Price:"), self.price_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(translate("Save"))
        self.save_button.clicked.connect(self.save_service)
        
        self.cancel_button = QPushButton(translate("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # If editing, populate fields
        if service:
            self.name_edit.setText(service["name"])
            if service.get("description"):
                self.description_edit.setText(service["description"])
            self.price_edit.setValue(service["price"])
    
    def save_service(self):
        """Save service data to database"""
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        price = self.price_edit.value()
        
        # Validate
        if not name:
            QMessageBox.warning(self, translate("Missing Data"), translate("Service name is required."))
            return
        
        # Connect to database
        conn = self.database.connect()
        cursor = conn.cursor()
        
        try:
            if self.service:  # Update existing
                cursor.execute(
                    "UPDATE services SET name=?, description=?, price=? WHERE id=?",
                    (name, description, price, self.service["id"])
                )
            else:  # Add new
                cursor.execute(
                    "INSERT INTO services (name, description, price) VALUES (?, ?, ?)",
                    (name, description, price)
                )
            
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, translate("Error"), f"{translate('Failed to save service:')} {str(e)}")
        finally:
            conn.close()

class SelectServiceDialog(QDialog):
    """Dialog for selecting a service with quantity"""
    def __init__(self, parent=None, service=None):
        super().__init__(parent)
        
        self.service = service
        self.settings = load_settings()
        
        self.setWindowTitle(f"{translate('Add Service: ')}{service['name']}")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Service details
        details_group = QGroupBox(translate("Service Details"))
        details_layout = QFormLayout(details_group)
        
        details_layout.addRow(translate("Name:"), QLabel(service["name"]))
        if service.get("description"):
            details_layout.addRow(translate("Description:"), QLabel(service["description"]))
        details_layout.addRow(translate("Price:"), QLabel(format_price(service['price'], self.settings)))
        
        layout.addWidget(details_group)
        
        # Quantity selection
        quantity_group = QGroupBox(translate("Quantity"))
        quantity_layout = QFormLayout(quantity_group)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self.update_total)
        
        quantity_layout.addRow(translate("Quantity:"), self.quantity_spin)
        
        self.total_label = QLabel(format_price(service['price'], self.settings))
        quantity_layout.addRow(translate("Total:"), self.total_label)
        
        layout.addWidget(quantity_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(translate("Add to Transaction"))
        self.add_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton(translate("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def reload_settings(self):
        """Reload settings and update UI with new translations and currency"""
        self.settings = load_settings()
        
        # Update window title
        self.setWindowTitle(f"{translate('Add Service: ')}{self.service['name']}")
        
        # Update group box titles
        # Find the groupboxes in the dialog
        for widget in self.findChildren(QGroupBox):
            if widget.title() == "Service Details" or widget.title() == "Hizmet Detayları":
                widget.setTitle(translate("Service Details"))
            elif widget.title() == "Quantity" or widget.title() == "Miktar":
                widget.setTitle(translate("Quantity"))
                
        # Update form labels
        for layout in self.findChildren(QFormLayout):
            for i in range(layout.rowCount()):
                label_item = layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label = label_item.widget()
                    if isinstance(label, QLabel):
                        if label.text() == "Quantity:" or label.text() == "Miktar:":
                            label.setText(translate("Quantity:"))
                        elif label.text() == "Total:" or label.text() == "Toplam:":
                            label.setText(translate("Total:"))
                        elif label.text() == "Name:" or label.text() == "İsim:":
                            label.setText(translate("Name:"))
                        elif label.text() == "Description:" or label.text() == "Açıklama:":
                            label.setText(translate("Description:"))
                        elif label.text() == "Price:" or label.text() == "Fiyat:":
                            label.setText(translate("Price:"))
        
        # Update buttons
        self.add_button.setText(translate("Add to Transaction"))
        self.cancel_button.setText(translate("Cancel"))
        
        # Update labels
        self.update_total()
    
    def update_total(self):
        """Update the total price based on quantity"""
        quantity = self.quantity_spin.value()
        total = quantity * self.service["price"]
        self.total_label.setText(format_price(total, self.settings))
    
    def get_quantity(self):
        """Return the selected quantity"""
        return self.quantity_spin.value()

class ServiceTab(QWidget):
    """Service management tab"""
    service_selected = pyqtSignal(dict, int)
    
    def __init__(self):
        super().__init__()
        
        self.database = Database()
        self.settings = load_settings()
        
        layout = QVBoxLayout(self)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(translate("Search:")))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(translate("Enter service name"))
        self.search_edit.returnPressed.connect(self.search_services)
        search_layout.addWidget(self.search_edit)
        
        self.search_button = QPushButton(translate("Search"))
        self.search_button.clicked.connect(self.search_services)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(4)
        self.services_table.setHorizontalHeaderLabels([
            translate("ID"), 
            translate("Name"), 
            translate("Description"), 
            translate("Price")
        ])
        
        # Adjust column widths
        self.services_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.services_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.services_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.services_table.cellDoubleClicked.connect(self.on_service_double_clicked)
        
        layout.addWidget(self.services_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(translate("Add Service"))
        self.add_button.clicked.connect(self.add_service)
        
        self.edit_button = QPushButton(translate("Edit Service"))
        self.edit_button.clicked.connect(self.edit_service)
        
        self.select_button = QPushButton(translate("Select Service"))
        self.select_button.clicked.connect(self.select_service)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.select_button)
        
        layout.addLayout(button_layout)
        
        # Load initial data
        self.load_services()
    
    def reload_settings(self):
        """Reload settings and update UI with new translations and currency"""
        # Reload settings to get new currency format
        self.settings = load_settings()
        
        # Update UI elements with new translations
        self.search_button.setText(translate("Search"))
        self.search_edit.setPlaceholderText(translate("Enter service name"))
        
        # Update table headers
        self.services_table.setHorizontalHeaderLabels([
            translate("ID"), 
            translate("Name"), 
            translate("Description"), 
            translate("Price")
        ])
        
        # Update buttons
        self.add_button.setText(translate("Add Service"))
        self.edit_button.setText(translate("Edit Service"))
        self.select_button.setText(translate("Select Service"))
        
        # Refresh table to show updated currency formatting and translations
        self.populate_table(self.database.get_all_services())
    
    def load_services(self):
        """Load all services from database"""
        services = self.database.get_all_services()
        self.populate_table(services)
    
    def search_services(self):
        """Search for services by name"""
        search_term = self.search_edit.text().strip()
        
        services = []
        if search_term:
            # Search in services table
            conn = self.database.connect()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute(
                "SELECT * FROM services WHERE name LIKE ? OR description LIKE ?",
                (search_pattern, search_pattern)
            )
            
            services = [dict(row) for row in cursor.fetchall()]
            conn.close()
        else:
            # If search is empty, load all services
            services = self.database.get_all_services()
        
        self.populate_table(services)
    
    def populate_table(self, services):
        """Populate table with services"""
        # Always reload settings before displaying to ensure current currency format
        self.settings = load_settings()
        
        self.services_table.setRowCount(len(services))
        
        for i, service in enumerate(services):
            self.services_table.setItem(i, 0, QTableWidgetItem(str(service["id"])))
            self.services_table.setItem(i, 1, QTableWidgetItem(service["name"]))
            self.services_table.setItem(i, 2, QTableWidgetItem(service.get("description", "")))
            
            price_item = QTableWidgetItem(format_price(service["price"], self.settings))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.services_table.setItem(i, 3, price_item)
    
    def get_selected_service(self):
        """Get the currently selected service from the table"""
        selected_rows = self.services_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, translate("No Selection"), translate("Please select a service."))
            return None
        
        row = selected_rows[0].row()
        service_id = int(self.services_table.item(row, 0).text())
        
        return self.database.get_service(service_id)
    
    def add_service(self):
        """Open dialog to add a new service"""
        dialog = ServiceDialog(self)
        if dialog.exec_():
            self.load_services()
    
    def edit_service(self):
        """Open dialog to edit the selected service"""
        service = self.get_selected_service()
        if service:
            dialog = ServiceDialog(self, service)
            if dialog.exec_():
                self.load_services()
    
    def select_service(self):
        """Select a service for transaction with quantity"""
        service = self.get_selected_service()
        if service:
            dialog = SelectServiceDialog(self, service)
            dialog.reload_settings()  # Ensure all text is properly translated
            if dialog.exec_():
                quantity = dialog.get_quantity()
                self.service_selected.emit(service, quantity)
                # Return to the transaction tab
                main_window = self.window()
                if hasattr(main_window, 'tab_widget'):
                    main_window.tab_widget.setCurrentIndex(0)  # Switch to transaction tab
    
    def on_service_double_clicked(self, row, column):
        """Handle double-click on service row"""
        service_id = int(self.services_table.item(row, 0).text())
        service = self.database.get_service(service_id)
        
        if service:
            dialog = SelectServiceDialog(self, service)
            dialog.reload_settings()  # Ensure all text is properly translated
            if dialog.exec_():
                quantity = dialog.get_quantity()
                self.service_selected.emit(service, quantity)
                # Return to the transaction tab
                main_window = self.window()
                if hasattr(main_window, 'tab_widget'):
                    main_window.tab_widget.setCurrentIndex(0)  # Switch to transaction tab 