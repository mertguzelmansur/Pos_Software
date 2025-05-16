from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.utils.translator import translate
from src.utils.license_manager import LicenseManager

class AboutTab(QWidget):
    """
    About tab showing program information.
    """
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Program title
        title_label = QLabel(translate("Tailor Shop Management System"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # License information
        self.license_info = self.get_license_info()
        license_layout = QHBoxLayout()
        license_layout.setAlignment(Qt.AlignCenter)
        
        license_label = QLabel(f"{translate('License Status')}: ")
        license_font = QFont()
        license_font.setBold(True)
        license_label.setFont(license_font)
        
        self.license_status_label = QLabel(self.license_info["status_text"])
        if self.license_info["is_valid"]:
            self.license_status_label.setStyleSheet("color: green;")
        else:
            self.license_status_label.setStyleSheet("color: red;")
        
        license_layout.addWidget(license_label)
        license_layout.addWidget(self.license_status_label)
        layout.addLayout(license_layout)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Author information with label
        author_layout = QHBoxLayout()
        author_layout.setAlignment(Qt.AlignCenter)
        
        # Developer label now on the left
        developer_label = QLabel(f"{translate('Developer')} - ")
        developer_font = QFont()
        developer_font.setPointSize(10)
        developer_font.setItalic(True)
        developer_label.setFont(developer_font)
        
        author_label = QLabel("Mert Güzelmansur")
        author_font = QFont()
        author_font.setPointSize(12)
        author_label.setFont(author_font)
        
        author_layout.addWidget(developer_label)
        author_layout.addWidget(author_label)
        layout.addLayout(author_layout)
        
        # Email with contact label
        email_layout = QHBoxLayout()
        email_layout.setAlignment(Qt.AlignCenter)
        
        # Contact label now on the left
        contact_label = QLabel(f"{translate('Contact')} - ")
        contact_font = QFont()
        contact_font.setPointSize(10)
        contact_font.setItalic(True)
        contact_label.setFont(contact_font)
        
        email_label = QLabel("mertglm12@gmail.com")
        
        email_layout.addWidget(contact_label)
        email_layout.addWidget(email_label)
        layout.addLayout(email_layout)
        
        # Separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)
        
        # Copyright information
        copyright_label = QLabel(f"© {translate('All Rights Reserved')}. 2025")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        layout.addStretch()

    def get_license_info(self):
        """Get license information to display"""
        license_manager = LicenseManager()
        license_status = license_manager.get_license_info()
        
        is_valid = license_status["status"] == "Active"
        
        # Create readable status text
        status_text = ""
        if is_valid:
            if license_status["is_trial"]:
                if license_status["expiry_date"]:
                    status_text = f"{translate('Trial License')} - {translate('Valid until')} {license_status['expiry_date']}"
                else:
                    status_text = translate('Trial License')
            else:
                status_text = translate('Full License')
        else:
            if license_status["status"] == "Not Licensed":
                status_text = translate('Not Licensed')
            else:
                status_text = translate('License Invalid')
        
        return {
            "is_valid": is_valid,
            "is_trial": license_status["is_trial"],
            "status_text": status_text,
            "expiry_date": license_status.get("expiry_date", "")
        }
        
    def reload_settings(self):
        """Reload settings to update translations"""
        # Update license information
        self.license_info = self.get_license_info()
        self.license_status_label.setText(self.license_info["status_text"])
        
        # Find and update all labels with translations
        for widget in self.findChildren(QLabel):
            # Update program title
            if widget.text().startswith(translate("Tailor Shop Management System")):
                widget.setText(translate("Tailor Shop Management System"))
            # Update license status label
            elif widget.text().startswith(f"{translate('License Status')}"):
                widget.setText(f"{translate('License Status')}: ")
            # Update developer label
            elif widget.text().endswith(" - ") and (widget.text().startswith("Geliştirici") or widget.text().startswith("Developer")):
                widget.setText(f"{translate('Developer')} - ")
            # Update contact label
            elif widget.text().endswith(" - ") and (widget.text().startswith("İletişim") or widget.text().startswith("Contact")):
                widget.setText(f"{translate('Contact')} - ")
            # Update copyright information
            elif "©" in widget.text():
                widget.setText(f"© {translate('All Rights Reserved')}. 2025") 