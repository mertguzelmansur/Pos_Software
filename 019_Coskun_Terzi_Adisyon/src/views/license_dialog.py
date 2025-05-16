from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QDesktopServices
from PyQt5.QtCore import QUrl

from src.utils.license_manager import LicenseManager
from src.utils.translator import translate

class LicenseDialog(QDialog):
    """
    Dialog for license key activation on first run
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager()
        
        self.setWindowTitle(translate("License Activation"))
        self.setFixedSize(500, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Program title
        title_label = QLabel(translate("Tailor Shop Management System"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Activation instructions
        instructions_label = QLabel(translate("Enter your license key to activate the software:"))
        instructions_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions_label)
        
        # License key input
        key_layout = QHBoxLayout()
        key_layout.setContentsMargins(30, 10, 30, 10)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(translate("License Key (e.g., MGM-210715-ABCDE)"))
        self.key_input.setMinimumWidth(300)
        key_layout.addWidget(self.key_input)
        
        # Activate button
        self.activate_button = QPushButton(translate("Activate"))
        self.activate_button.clicked.connect(self.activate_license)
        key_layout.addWidget(self.activate_button)
        
        layout.addLayout(key_layout)
        
        # Contact info
        contact_label = QLabel(translate("For questions or to purchase a license, contact: mertglm12@gmail.com"))
        contact_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact_label)
        
        # Separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 10, 30, 10)
        
        # Try demo button
        self.trial_button = QPushButton(translate("Try Demo (30 days)"))
        self.trial_button.clicked.connect(self.activate_trial)
        button_layout.addWidget(self.trial_button)
        
        # Exit button
        self.exit_button = QPushButton(translate("Exit"))
        self.exit_button.clicked.connect(self.reject)
        button_layout.addWidget(self.exit_button)
        
        layout.addLayout(button_layout)
        
        # Copyright at the bottom
        copyright_label = QLabel("© " + translate("Program Hakları Saklıdır") + ". 2025")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

    def activate_license(self):
        """Activate with the entered license key"""
        license_key = self.key_input.text().strip()
        if not license_key:
            QMessageBox.warning(
                self, 
                translate("Missing Key"), 
                translate("Please enter a valid license key.")
            )
            return
            
        if self.license_manager.activate_license(license_key):
            QMessageBox.information(
                self, 
                translate("Activation Successful"), 
                translate("Thank you! The software has been successfully activated.")
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                translate("Activation Failed"), 
                translate("The license key is invalid or has already been used.")
            )
    
    def activate_trial(self):
        """Activate a 30-day trial license"""
        # Generate a trial license key
        trial_key = self.license_manager.generate_license_key(is_trial=True)
        
        if self.license_manager.activate_license(trial_key):
            QMessageBox.information(
                self, 
                translate("Trial Activated"), 
                translate("The 30-day trial has been activated. The software will expire after this period.")
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                translate("Activation Failed"), 
                translate("Failed to activate trial. Please contact support.")
            )

    @staticmethod
    def show_activation_dialog(parent=None):
        """
        Show the license activation dialog
        Returns True if the license is valid or activated, False otherwise
        """
        license_manager = LicenseManager()
        
        # First check if license already exists and is valid
        if license_manager.is_license_valid():
            return True
            
        # If no valid license, show activation dialog
        dialog = LicenseDialog(parent)
        result = dialog.exec_()
        
        # Check if license was activated successfully
        return result == QDialog.Accepted and license_manager.is_license_valid() 