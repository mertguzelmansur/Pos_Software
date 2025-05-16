from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from src.utils.translator import translate

class AboutDialog(QDialog):
    """
    About dialog showing program information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(translate("About Program"))
        self.resize(400, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Program title
        title_label = QLabel(translate("Tailor Shop Management System"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Author information
        author_label = QLabel("Mert Güzelmansur")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)
        
        # Email
        email_label = QLabel("mertglm12@gmail.com")
        email_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(email_label)
        
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
        
        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout) 