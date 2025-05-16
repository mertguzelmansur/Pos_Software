from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QGroupBox, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
import os
import json

from src.utils.translator import translate, reload_translations

# Define predefined currencies
CURRENCIES = [
    {"name": "Turkish Lira", "symbol": "₺", "default_position": "after"},
    {"name": "Dollar", "symbol": "$", "default_position": "before"},
    {"name": "Euro", "symbol": "€", "default_position": "after"}
]

# Define available languages
LANGUAGES = [
    {"code": "tr", "name": "Türkçe"},
    {"code": "en", "name": "English"}
]

class SettingsTab(QWidget):
    """Settings tab for application configuration"""
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.settings_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "settings.json"
        )
        
        # Default settings
        self.default_settings = {
            "language": "tr",  # Default to Turkish
            "label_printer": {
                "paper_width": 10.0,
                "paper_height": 5.0,
                "output_directory": os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "labels"
                )
            },
            "currency": {
                "name": "Turkish Lira",
                "symbol": "₺",
                "position": "after"  # "before" or "after"
            },
            "database": {
                "file": os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "tailor_shop.db"
                )
            },
            "ui": {
                "font_size": 10,
                "confirm_on_exit": True,
                "confirm_on_print": True
            }
        }
        
        # Load existing settings or use defaults
        self.settings = self.load_settings()
        
        # Create UI
        layout = QVBoxLayout(self)
        
        # Create tabs for different setting categories
        settings_tabs = QTabWidget()
        
        # Language settings
        language_tab = QWidget()
        language_layout = QFormLayout(language_tab)
        
        self.language_combo = QComboBox()
        for language in LANGUAGES:
            self.language_combo.addItem(f"{language['name']} ({language['code']})")
        
        # Set current language
        current_language = self.settings.get("language", "tr")
        for i, language in enumerate(LANGUAGES):
            if language["code"] == current_language:
                self.language_combo.setCurrentIndex(i)
                break
        
        language_layout.addRow(translate("Language:"), self.language_combo)
        
        settings_tabs.addTab(language_tab, translate("Language"))
        
        # Printer settings
        printer_tab = QWidget()
        printer_layout = QFormLayout(printer_tab)
        
        self.paper_width_spin = QDoubleSpinBox()
        self.paper_width_spin.setRange(1.0, 30.0)
        self.paper_width_spin.setSuffix(" cm")
        self.paper_width_spin.setValue(self.settings["label_printer"]["paper_width"])
        printer_layout.addRow(translate("Paper Width:"), self.paper_width_spin)
        
        self.paper_height_spin = QDoubleSpinBox()
        self.paper_height_spin.setRange(1.0, 30.0)
        self.paper_height_spin.setSuffix(" cm")
        self.paper_height_spin.setValue(self.settings["label_printer"]["paper_height"])
        printer_layout.addRow(translate("Paper Height:"), self.paper_height_spin)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(self.settings["label_printer"]["output_directory"])
        self.output_dir_edit.setReadOnly(True)
        
        self.browse_button = QPushButton(translate("Browse..."))
        self.browse_button.clicked.connect(self.browse_output_dir)
        
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.browse_button)
        
        printer_layout.addRow(translate("Output Directory:"), output_dir_layout)
        
        settings_tabs.addTab(printer_tab, translate("Label Printer"))
        
        # Currency settings
        currency_tab = QWidget()
        currency_layout = QFormLayout(currency_tab)
        
        # Replace text input with dropdown
        self.currency_combo = QComboBox()
        for currency in CURRENCIES:
            # Translate currency name
            translated_name = translate(currency['name'])
            self.currency_combo.addItem(f"{translated_name} ({currency['symbol']})")
        
        # Set current currency
        current_currency = self.settings["currency"].get("name", "Turkish Lira")
        for i, currency in enumerate(CURRENCIES):
            if currency["name"] == current_currency:
                self.currency_combo.setCurrentIndex(i)
                break
        
        self.currency_combo.currentIndexChanged.connect(self.on_currency_changed)
        currency_layout.addRow(translate("Currency:"), self.currency_combo)
        
        self.currency_position_combo = QComboBox()
        self.currency_position_combo.addItems([translate("Before"), translate("After")])
        self.currency_position_combo.setCurrentIndex(
            0 if self.settings["currency"]["position"] == "before" else 1
        )
        currency_layout.addRow(translate("Symbol Position:"), self.currency_position_combo)
        
        # Display current format
        self.currency_example = QLabel()
        self.update_currency_example()
        currency_layout.addRow(translate("Example:"), self.currency_example)
        
        settings_tabs.addTab(currency_tab, translate("Currency"))
        
        # Database settings
        database_tab = QWidget()
        database_layout = QFormLayout(database_tab)
        
        db_path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setText(self.settings["database"]["file"])
        self.db_path_edit.setReadOnly(True)
        
        self.db_browse_button = QPushButton(translate("Browse..."))
        self.db_browse_button.clicked.connect(self.browse_database_file)
        
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(self.db_browse_button)
        
        database_layout.addRow(translate("Database File:"), db_path_layout)
        
        settings_tabs.addTab(database_tab, translate("Database"))
        
        # UI settings
        ui_tab = QWidget()
        ui_layout = QFormLayout(ui_tab)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.settings["ui"]["font_size"])
        ui_layout.addRow(translate("Font Size:"), self.font_size_spin)
        
        self.confirm_exit_check = QCheckBox()
        self.confirm_exit_check.setChecked(self.settings["ui"]["confirm_on_exit"])
        ui_layout.addRow(translate("Confirm on Exit:"), self.confirm_exit_check)
        
        self.confirm_print_check = QCheckBox()
        self.confirm_print_check.setChecked(self.settings["ui"]["confirm_on_print"])
        ui_layout.addRow(translate("Confirm on Print:"), self.confirm_print_check)
        
        settings_tabs.addTab(ui_tab, translate("User Interface"))
        
        layout.addWidget(settings_tabs)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_button = QPushButton(translate("Reset to Defaults"))
        self.reset_button.clicked.connect(self.reset_settings)
        
        self.save_button = QPushButton(translate("Save Settings"))
        self.save_button.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def on_currency_changed(self, index):
        """Update currency position based on selected currency"""
        if 0 <= index < len(CURRENCIES):
            currency = CURRENCIES[index]
            default_position = currency["default_position"]
            self.currency_position_combo.setCurrentIndex(0 if default_position == "before" else 1)
            self.update_currency_example()
    
    def update_currency_example(self):
        """Update the currency example label"""
        index = self.currency_combo.currentIndex()
        if 0 <= index < len(CURRENCIES):
            currency = CURRENCIES[index]
            symbol = currency["symbol"]
            position = "before" if self.currency_position_combo.currentIndex() == 0 else "after"
            
            if position == "before":
                example = f"{symbol}100.00"
            else:
                example = f"100.00 {symbol}"
                
            self.currency_example.setText(example)
    
    def load_settings(self):
        """Load settings from file or use defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Update settings from UI
            # Get selected language
            language_index = self.language_combo.currentIndex()
            if 0 <= language_index < len(LANGUAGES):
                self.settings["language"] = LANGUAGES[language_index]["code"]
                
            self.settings["label_printer"]["paper_width"] = self.paper_width_spin.value()
            self.settings["label_printer"]["paper_height"] = self.paper_height_spin.value()
            self.settings["label_printer"]["output_directory"] = self.output_dir_edit.text()
            
            # Get selected currency
            index = self.currency_combo.currentIndex()
            if 0 <= index < len(CURRENCIES):
                currency = CURRENCIES[index]
                self.settings["currency"]["name"] = currency["name"]
                self.settings["currency"]["symbol"] = currency["symbol"]
            
            self.settings["currency"]["position"] = "before" if self.currency_position_combo.currentIndex() == 0 else "after"
            
            self.settings["database"]["file"] = self.db_path_edit.text()
            
            self.settings["ui"]["font_size"] = self.font_size_spin.value()
            self.settings["ui"]["confirm_on_exit"] = self.confirm_exit_check.isChecked()
            self.settings["ui"]["confirm_on_print"] = self.confirm_print_check.isChecked()
            
            # Ensure output directory exists
            output_dir = self.settings["label_printer"]["output_directory"]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            QMessageBox.information(self, translate("Settings Saved"), translate("Settings saved successfully."))
            self.settings_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, translate("Error"), f"{translate('Failed to save settings:')} {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, translate('Reset Confirmation'),
            translate("Are you sure you want to reset all settings to default values?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings = self.default_settings.copy()
            
            # Update UI with default values
            # Set language
            current_language = self.settings.get("language", "tr")
            for i, language in enumerate(LANGUAGES):
                if language["code"] == current_language:
                    self.language_combo.setCurrentIndex(i)
                    break
                    
            self.paper_width_spin.setValue(self.settings["label_printer"]["paper_width"])
            self.paper_height_spin.setValue(self.settings["label_printer"]["paper_height"])
            self.output_dir_edit.setText(self.settings["label_printer"]["output_directory"])
            
            # Set default currency
            default_currency = self.settings["currency"].get("name", "Turkish Lira")
            for i, currency in enumerate(CURRENCIES):
                if currency["name"] == default_currency:
                    self.currency_combo.setCurrentIndex(i)
                    break
            
            self.currency_position_combo.setCurrentIndex(
                0 if self.settings["currency"]["position"] == "before" else 1
            )
            
            self.update_currency_example()
            
            self.db_path_edit.setText(self.settings["database"]["file"])
            
            self.font_size_spin.setValue(self.settings["ui"]["font_size"])
            self.confirm_exit_check.setChecked(self.settings["ui"]["confirm_on_exit"])
            self.confirm_print_check.setChecked(self.settings["ui"]["confirm_on_print"])
    
    def browse_output_dir(self):
        """Open file dialog to select output directory"""
        current_dir = self.output_dir_edit.text()
        if not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")
        
        directory = QFileDialog.getExistingDirectory(
            self, translate("Select Output Directory"), current_dir
        )
        
        if directory:
            self.output_dir_edit.setText(directory)
    
    def browse_database_file(self):
        """Open file dialog to select database file"""
        current_file = self.db_path_edit.text()
        current_dir = os.path.dirname(current_file) if os.path.exists(current_file) else os.path.expanduser("~")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, translate("Select Database File"), current_dir, 
            translate("SQLite Database (*.db)") + ";;" + translate("All Files (*)")
        )
        
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def get_settings(self):
        """Return the current settings"""
        return self.settings 