import sys
import os
import logging

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTextCodec, QLocale, QTranslator

# Add the project root directory to the path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from src.views.main_window import MainWindow
from src.views.license_dialog import LicenseDialog
from src.utils.font_installer import download_and_install_fonts
from src.utils.license_manager import LicenseManager
from src.utils.translator import translate, reload_translations

def setup_logging():
    """Set up logging for the application"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up logging
    log_file = os.path.join(log_dir, "app.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_license():
    """Check if the license is valid"""
    license_manager = LicenseManager()
    
    # Check if license exists and is valid
    if license_manager.is_license_valid():
        # License exists and is valid
        return True
    
    # Show license activation dialog
    return LicenseDialog.show_activation_dialog()

def main():
    """Main application entry point"""
    try:
        # Set UTF-8 as the text codec for proper Turkish character support
        QTextCodec.setCodecForLocale(QTextCodec.codecForName("UTF-8"))
        
        # Set Turkish locale
        locale = QLocale(QLocale.Turkish, QLocale.Turkey)
        QLocale.setDefault(locale)
        
        # Download and install fonts if needed
        download_and_install_fonts()
        
        # Set up logging
        setup_logging()
        
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName(translate("Tailor Shop Management System"))
        
        # Check license before starting the app
        if not check_license():
            # License check failed, exit application
            logging.info("License check failed. Exiting application.")
            return 1
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Run the application
        return app.exec_()
    except Exception as e:
        logging.exception(f"Unhandled exception: {e}")
        QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    # Make sure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main()) 