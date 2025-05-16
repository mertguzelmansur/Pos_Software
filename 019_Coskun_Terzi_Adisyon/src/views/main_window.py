from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase

import os
import json

from src.views.customer_tab import CustomerTab
from src.views.service_tab import ServiceTab
from src.views.transaction_tab import TransactionTab
from src.views.settings_tab import SettingsTab
from src.views.about_tab import AboutTab
from src.utils.translator import translate, reload_translations

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(translate("Tailor Shop Management System"))
        self.setMinimumSize(800, 600)
        
        # Set up font that supports Turkish characters
        self.setup_fonts()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Apply initial font size
        self.apply_font_settings()
        
        # Create the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tab pages
        self.customer_tab = CustomerTab()
        self.service_tab = ServiceTab()
        self.transaction_tab = TransactionTab()
        self.settings_tab = SettingsTab()
        self.about_tab = AboutTab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.transaction_tab, translate("New Transaction"))
        self.tab_widget.addTab(self.customer_tab, translate("Customers"))
        self.tab_widget.addTab(self.service_tab, translate("Services"))
        self.tab_widget.addTab(self.settings_tab, translate("Settings"))
        self.tab_widget.addTab(self.about_tab, translate("About"))
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.statusBar().showMessage(translate("Ready"))
        
        # Connect signals
        self.customer_tab.customer_selected.connect(self.on_customer_selected)
        self.service_tab.service_selected.connect(self.transaction_tab.add_service)
        self.settings_tab.settings_saved.connect(self.on_settings_saved)
    
    def setup_fonts(self):
        """Setup fonts that properly support Turkish characters"""
        # Check for fonts with Turkish support
        font_db = QFontDatabase()
        font_families = font_db.families()
        
        # Preferred fonts in order of preference
        preferred_fonts = ["Arial", "Calibri", "Segoe UI", "DejaVu Sans", "Tahoma"]
        
        # Find the first available preferred font
        selected_font = None
        for font in preferred_fonts:
            if font in font_families:
                selected_font = font
                break
        
        # If no preferred font found, use system default
        if not selected_font:
            return
            
        # Set the application font
        font = QFont(selected_font)
        QApplication.instance().setFont(font)
    
    def load_settings(self):
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
    
    def apply_font_settings(self):
        """Apply font settings to the entire application"""
        font_size = self.settings.get("ui", {}).get("font_size", 10)
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)
    
    def on_customer_selected(self, customer):
        """
        Handle customer selection from customer tab
        Switch to transaction tab and set the selected customer
        """
        self.tab_widget.setCurrentIndex(0)  # Switch to transaction tab
        self.transaction_tab.set_customer(customer)
    
    def on_settings_saved(self):
        """Handle settings saved event"""
        # Reload settings
        self.settings = self.load_settings()
        
        # Reload translations
        reload_translations()
        
        # Update window title and tab names
        self.setWindowTitle(translate("Tailor Shop Management System"))
        self.tab_widget.setTabText(0, translate("New Transaction"))
        self.tab_widget.setTabText(1, translate("Customers"))
        self.tab_widget.setTabText(2, translate("Services"))
        self.tab_widget.setTabText(3, translate("Settings"))
        self.tab_widget.setTabText(4, translate("About"))
        
        # Apply font settings
        self.apply_font_settings()
        
        # Refresh all tabs with new settings
        self.service_tab.reload_settings()
        self.transaction_tab.reload_settings()
        self.customer_tab.reload_settings() if hasattr(self.customer_tab, 'reload_settings') else None
        self.about_tab.reload_settings() if hasattr(self.about_tab, 'reload_settings') else None
        
        # Refresh any open dialogs
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'reload_settings') and widget.isVisible():
                widget.reload_settings()
        
        # Force a complete UI refresh by recreating the tab pages if language changed
        old_language = getattr(self, '_previous_language', None)
        current_language = self.settings.get("language", "tr")
        
        if old_language and old_language != current_language:
            # Store the current tab index
            current_tab = self.tab_widget.currentIndex()
            
            # Remove all tabs
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
            
            # Recreate tabs
            self.tab_widget.addTab(self.transaction_tab, translate("New Transaction"))
            self.tab_widget.addTab(self.customer_tab, translate("Customers"))
            self.tab_widget.addTab(self.service_tab, translate("Services"))
            self.tab_widget.addTab(self.settings_tab, translate("Settings"))
            self.tab_widget.addTab(self.about_tab, translate("About"))
            
            # Restore the current tab
            self.tab_widget.setCurrentIndex(current_tab)
        
        # Remember the current language for next time
        self._previous_language = current_language
        
        self.statusBar().showMessage(translate("Settings saved successfully"), 3000)  # Show message for 3 seconds
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Check if we should confirm on exit
        confirm_on_exit = self.settings.get("ui", {}).get("confirm_on_exit", True)
        
        if confirm_on_exit:
            reply = QMessageBox.question(
                self, translate('Confirm Exit'),
                translate("Are you sure you want to exit?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 