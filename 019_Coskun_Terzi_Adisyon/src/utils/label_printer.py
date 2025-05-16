from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import json
import locale

from src.utils.translator import translate

class LabelPrinter:
    def __init__(self, output_dir=None):
        """Initialize the label printer"""
        self.settings = self._load_settings()
        
        if output_dir is None:
            # Use output directory from settings
            self.output_dir = self.settings.get("label_printer", {}).get("output_directory")
            if not self.output_dir:
                # Fallback to default
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.output_dir = os.path.join(base_dir, "labels")
        else:
            self.output_dir = output_dir
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Define label size from settings
        self.width = self.settings.get("label_printer", {}).get("paper_width", 10) * cm
        self.height = self.settings.get("label_printer", {}).get("paper_height", 5) * cm
        self.styles = getSampleStyleSheet()
        
        # Get currency symbol and position
        self.currency_symbol = self.settings.get("currency", {}).get("symbol", "$")
        self.currency_position = self.settings.get("currency", {}).get("position", "before")
        
        # Get language
        self.language = self.settings.get("language", "tr")
        
        # Register fonts that support Turkish characters
        self._register_fonts()
    
    def _register_fonts(self):
        """Register fonts that support Turkish characters"""
        try:
            # Define font dir
            fonts_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "fonts"
            )
            
            # Check for our downloaded fonts first
            dejavu_files = {
                "DejaVuSans": "DejaVuSans.ttf",
                "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
                "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf"
            }
            
            custom_fonts_available = True
            
            # Check if our font files exist
            for font_name, font_file in dejavu_files.items():
                font_path = os.path.join(fonts_dir, font_file)
                if not os.path.exists(font_path):
                    custom_fonts_available = False
                    break
            
            # Track if any fonts were registered
            fonts_registered = False
            
            if custom_fonts_available:
                # Register our custom fonts
                for font_name, font_file in dejavu_files.items():
                    try:
                        font_path = os.path.join(fonts_dir, font_file)
                        # Check if font already registered
                        if font_name not in pdfmetrics._fonts:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                        fonts_registered = True
                    except Exception as e:
                        print(f"Error registering font {font_name}: {e}")
                
                # Set the main font name if successful
                if fonts_registered:
                    self.font_name = "DejaVuSans"
                else:
                    # Fallback to default
                    self.font_name = "Helvetica"
            else:
                # Fall back to system fonts
                self.font_name = "Helvetica"
                
        except Exception as e:
            print(f"Error in font registration: {e}")
            self.font_name = "Helvetica"
    
    def _load_settings(self):
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
    
    def _format_price(self, price):
        """Format price according to currency settings"""
        if self.currency_position == "before":
            return f"{self.currency_symbol}{price:.2f}"
        else:
            return f"{price:.2f}{self.currency_symbol}"
    
    def _reload_settings(self):
        """Reload settings to ensure we have the latest currency info"""
        self.settings = self._load_settings()
        self.currency_symbol = self.settings.get("currency", {}).get("symbol", "$")
        self.currency_position = self.settings.get("currency", {}).get("position", "before")
        self.language = self.settings.get("language", "tr")
    
    def _format_date(self, date_obj=None):
        """Format date according to language settings"""
        if date_obj is None:
            date_obj = datetime.datetime.now()
        
        # Use different date format based on language
        if self.language == "tr":
            try:
                # Try to set locale for Turkish date
                locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')
            except locale.Error:
                try:
                    # Fallback to Windows locale code
                    locale.setlocale(locale.LC_TIME, 'Turkish_Turkey.1254')
                except locale.Error:
                    # If that fails too, just use the English format
                    return date_obj.strftime("%d.%m.%Y %H:%M")
            
            # Return Turkish formatted date
            return date_obj.strftime("%d.%m.%Y %H:%M")
        else:
            # English date format
            return date_obj.strftime("%Y-%m-%d %H:%M")
    
    def generate_label_pdf(self, customer, services, note=None):
        """
        Generate a PDF label for a customer with specified services
        
        Args:
            customer (dict): Customer information dict (name, surname, phone, location)
            services (list): List of service dicts with name, quantity, price
            note (str, optional): Additional notes for the label
            
        Returns:
            str: Path to the generated PDF file
        """
        # Always reload settings to ensure latest currency format
        self._reload_settings()
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{customer['surname']}_{customer['name']}_{timestamp}.pdf"
        file_path = os.path.join(self.output_dir, file_name)
        
        # Create the PDF canvas
        c = canvas.Canvas(file_path, pagesize=(self.width, self.height))
        
        # Set up the document
        c.setTitle(f"Label - {customer['name']} {customer['surname']}")
        
        # Draw customer details
        c.setFont(self.font_name + "-Bold" if self.font_name != "Helvetica" else "Helvetica-Bold", 12)
        c.drawString(0.5 * cm, 4 * cm, f"{customer['name']} {customer['surname']}")
        
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 10)
        if customer.get('phone'):
            c.drawString(0.5 * cm, 3.5 * cm, f"{translate('Phone')}: {customer['phone']}")
        
        if customer.get('location'):
            c.drawString(0.5 * cm, 3 * cm, f"{translate('Location')}: {customer['location']}")
        
        # Draw service details
        y_position = 2.5 * cm
        c.setFont(self.font_name + "-Bold" if self.font_name != "Helvetica" else "Helvetica-Bold", 10)
        c.drawString(0.5 * cm, y_position, f"{translate('Services')}:")
        y_position -= 0.5 * cm
        
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 9)
        for service in services:
            service_text = f"- {service['name']} x{service['quantity']} ({self._format_price(service['price'])})"
            c.drawString(0.5 * cm, y_position, service_text)
            y_position -= 0.3 * cm
            
            if y_position < 1 * cm:  # Avoid overflowing the label
                break
        
        # Add notes if provided
        if note and y_position > 0.5 * cm:
            c.setFont(self.font_name + "-Oblique" if self.font_name != "Helvetica" else "Helvetica-Oblique", 8)
            c.drawString(0.5 * cm, y_position, f"{translate('Note')}: {note}")
        
        # Add current date at the bottom
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 8)
        current_date = self._format_date()
        c.drawString(0.5 * cm, 0.3 * cm, f"{translate('Date')}: {current_date}")
        
        # Save the PDF
        c.save()
        return file_path
    
    def generate_label_preview(self, customer, services, note=None):
        """
        Generate a PDF label for preview purposes
        Same as generate_label_pdf but stored in a temporary location
        """
        # Always reload settings to ensure latest currency format
        self._reload_settings()
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"preview_{timestamp}.pdf"
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "temp", file_name)
        
        # Ensure temp directory exists
        temp_dir = os.path.dirname(file_path)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Create the PDF using the same logic as generate_label_pdf
        c = canvas.Canvas(file_path, pagesize=(self.width, self.height))
        
        # Set up the document
        c.setTitle(f"Label - {customer['name']} {customer['surname']}")
        
        # Draw customer details
        c.setFont(self.font_name + "-Bold" if self.font_name != "Helvetica" else "Helvetica-Bold", 12)
        c.drawString(0.5 * cm, 4 * cm, f"{customer['name']} {customer['surname']}")
        
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 10)
        if customer.get('phone'):
            c.drawString(0.5 * cm, 3.5 * cm, f"{translate('Phone')}: {customer['phone']}")
        
        if customer.get('location'):
            c.drawString(0.5 * cm, 3 * cm, f"{translate('Location')}: {customer['location']}")
        
        # Draw service details
        y_position = 2.5 * cm
        c.setFont(self.font_name + "-Bold" if self.font_name != "Helvetica" else "Helvetica-Bold", 10)
        c.drawString(0.5 * cm, y_position, f"{translate('Services')}:")
        y_position -= 0.5 * cm
        
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 9)
        for service in services:
            service_text = f"- {service['name']} x{service['quantity']} ({self._format_price(service['price'])})"
            c.drawString(0.5 * cm, y_position, service_text)
            y_position -= 0.3 * cm
            
            if y_position < 1 * cm:  # Avoid overflowing the label
                break
        
        # Add notes if provided
        if note and y_position > 0.5 * cm:
            c.setFont(self.font_name + "-Oblique" if self.font_name != "Helvetica" else "Helvetica-Oblique", 8)
            c.drawString(0.5 * cm, y_position, f"{translate('Note')}: {note}")
        
        # Add current date at the bottom
        c.setFont(self.font_name if self.font_name != "Helvetica" else "Helvetica", 8)
        current_date = self._format_date()
        c.drawString(0.5 * cm, 0.3 * cm, f"{translate('Date')}: {current_date}")
        
        # Save the PDF
        c.save()
        return file_path 