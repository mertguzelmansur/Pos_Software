import os
import json

class Translator:
    """Utility class for translating text in the application"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one translator exists"""
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the translator"""
        if self._initialized:
            return
            
        self._initialized = True
        self.translations = {}
        self.reverse_translations = {}  # Added reverse translations dictionary
        self.current_language = "tr"  # Default to Turkish
        
        # Load settings to get the language
        self.load_settings()
        
        # Load translation files
        self.load_translations()
    
    def load_settings(self):
        """Load settings to get the current language"""
        settings_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "settings.json"
        )
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_language = settings.get("language", "tr")
        except Exception:
            # If there's an error, keep the default language
            pass
    
    def load_translations(self):
        """Load translation files"""
        # Path to translation files
        translations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "translations"
        )
        
        # Ensure translations directory exists
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
        
        # Try to load the translation file for the current language
        translation_file = os.path.join(translations_dir, f"{self.current_language}.json")
        
        if os.path.exists(translation_file):
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                    
                    # Create reverse translations dictionary for switching back to English
                    if self.current_language == "tr":
                        self.reverse_translations = {v: k for k, v in self.translations.items()}
            except Exception as e:
                print(f"Error loading translation file: {e}")
        else:
            # If the translation file doesn't exist, create it with the built-in translations
            self.create_translation_files(translations_dir)
            # Try loading again
            if os.path.exists(translation_file):
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations = json.load(f)
                        
                        # Create reverse translations dictionary
                        if self.current_language == "tr":
                            self.reverse_translations = {v: k for k, v in self.translations.items()}
                except Exception:
                    pass
    
    def create_translation_files(self, translations_dir):
        """Create translation files with built-in translations"""
        # Turkish translations
        tr_translations = {
            # General
            "Tailor Shop Management System": "Terzi Pos Sistemi",
            "Ready": "Hazır",
            
            # Tabs
            "New Transaction": "Yeni İşlem",
            "Customers": "Müşteriler",
            "Services": "Hizmetler",
            "Settings": "Ayarlar",
            
            # Customer tab
            "Search:": "Ara:",
            "Enter name, surname or phone": "İsim, soyisim veya telefon girin",
            "Search": "Ara",
            "Name": "İsim",
            "Surname": "Soyisim",
            "Phone": "Telefon",
            "Location": "Konum",
            "Add Customer": "Müşteri Ekle",
            "Edit Customer": "Müşteriyi Düzenle",
            "View History": "Geçmişi Görüntüle",
            "Select for Transaction": "İşlem İçin Seç",
            "No Selection": "Seçim Yok",
            "Please select a customer.": "Lütfen bir müşteri seçin.",
            
            # Customer dialog
            "Add New Customer": "Yeni Müşteri Ekle",
            "Edit Customer": "Müşteriyi Düzenle",
            "Name:": "İsim:",
            "Surname:": "Soyisim:",
            "Phone:": "Telefon:",
            "Location:": "Konum:",
            "Save": "Kaydet",
            "Cancel": "İptal",
            "Missing Data": "Eksik Veri",
            "Name is required.": "İsim gereklidir.",
            "Surname is required.": "Soyisim gereklidir.",
            "Error": "Hata",
            "Failed to save customer:": "Müşteri kaydedilemedi:",
            
            # Transaction tab
            "Customer": "Müşteri",
            "No customer selected": "Müşteri seçilmedi",
            "Select Customer": "Müşteri Seç",
            "New Customer": "Yeni Müşteri",
            "Selected Services": "Seçilen Hizmetler",
            "Service": "Hizmet",
            "Description": "Açıklama",
            "Price": "Fiyat",
            "Quantity": "Miktar",
            "Total": "Toplam",
            "Add Service": "Hizmet Ekle",
            "Remove Service": "Hizmeti Kaldır",
            "Add to Transaction": "İşleme Ekle",
            "Notes": "Notlar",
            "Additional notes for this transaction...": "Bu işlem için ek notlar...",
            "Preview Label": "Etiketi Önizle",
            "Print Label": "Etiketi Yazdır",
            "Complete Transaction": "İşlemi Tamamla",
            "Clear Form": "Formu Temizle",
            "Cannot Preview": "Önizlenemiyor",
            "Customer and at least one service are required.": "Müşteri ve en az bir hizmet gereklidir.",
            "Cannot Print": "Yazdırılamıyor",
            "Confirm Printing": "Yazdırmayı Onayla",
            "Are you sure you want to print the label?": "Etiketi yazdırmak istediğinizden emin misiniz?",
            "Print Error": "Yazdırma Hatası",
            "Failed to print label:": "Etiket yazdırılamadı:",
            "Cannot Complete": "Tamamlanamıyor",
            "Success": "Başarılı",
            "Transaction completed successfully.": "İşlem başarıyla tamamlandı.",
            "Failed to save transaction:": "İşlem kaydedilemedi:",
            "Preview Error": "Önizleme Hatası",
            "Failed to generate preview:": "Önizleme oluşturulamadı:",
            "N/A": "Yok",
            
            # Service tab
            "Enter service name": "Hizmet adını girin",
            "ID": "ID",
            "Add Service": "Hizmet Ekle",
            "Edit Service": "Hizmeti Düzenle",
            "Select Service": "Hizmet Seç",
            "Please select a service.": "Lütfen bir hizmet seçin.",
            
            # Service dialog
            "Add New Service": "Yeni Hizmet Ekle",
            "Edit Service": "Hizmeti Düzenle",
            "Service name is required.": "Hizmet adı gereklidir.",
            "Failed to save service:": "Hizmet kaydedilemedi:",
            "Add Service: ": "Hizmet Ekle: ",
            "Service Details": "Hizmet Detayları",
            
            # History dialog
            "History -": "Geçmiş -",
            "No transaction history available.": "İşlem geçmişi mevcut değil.",
            "No History": "Geçmiş Yok",
            "Transaction Details": "İşlem Detayları",
            "Date:": "Tarih:",
            "Total Amount:": "Toplam Tutar:",
            "Note:": "Not:",
            "Items": "Kalemler",
            "Transaction": "İşlem",
            "Close": "Kapat",
            
            # Confirmation dialogs
            "Confirm Exit": "Çıkışı Onayla",
            "Are you sure you want to exit?": "Çıkmak istediğinizden emin misiniz?",
            
            # Settings tab
            "Language": "Dil",
            "Language:": "Dil:",
            "Label Printer": "Etiket Yazıcısı",
            "Paper Width:": "Kağıt Genişliği:",
            "Paper Height:": "Kağıt Yüksekliği:",
            "Output Directory:": "Çıktı Dizini:",
            "Currency": "Para Birimi",
            "Currency:": "Para Birimi:",
            "Symbol Position:": "Sembol Konumu:",
            "Before": "Önce",
            "After": "Sonra",
            "Example:": "Örnek:",
            "Database": "Veritabanı",
            "Database File:": "Veritabanı Dosyası:",
            "User Interface": "Kullanıcı Arayüzü",
            "Font Size:": "Font Boyutu:",
            "Confirm on Exit:": "Çıkışta Onay:",
            "Confirm on Print:": "Yazdırmada Onay:",
            "Browse...": "Gözat...",
            "Reset to Defaults": "Varsayılanlara Döndür",
            "Save Settings": "Ayarları Kaydet",
            "Settings saved successfully": "Ayarlar başarıyla kaydedildi",
            "Settings Saved": "Ayarlar Kaydedildi",
            "Settings saved successfully.": "Ayarlar başarıyla kaydedildi.",
            "Reset Confirmation": "Sıfırlama Onayı",
            "Are you sure you want to reset all settings to default values?": "Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?",
            "Failed to save settings:": "Ayarlar kaydedilemedi:",
            
            # Currency Names
            "Turkish Lira": "Türk Lirası",
            "Dollar": "Dolar",
            "Euro": "Euro",
            
            # PDF Labels
            "Phone": "Telefon",
            "Location": "Konum",
            "Services": "Hizmetler",
            "Note": "Not",
            "Date": "Tarih",
            
            # File dialogs
            "Select Output Directory": "Çıktı Dizinini Seçin",
            "Select Database File": "Veritabanı Dosyasını Seçin",
            "SQLite Database (*.db)": "SQLite Veritabanı (*.db)",
            "All Files (*)": "Tüm Dosyalar (*)",
        }
        
        # English translations (keys are the same as values)
        en_translations = {key: key for key in tr_translations}
        
        # Save translation files
        translations = {
            "tr": tr_translations,
            "en": en_translations
        }
        
        for lang_code, trans in translations.items():
            file_path = os.path.join(translations_dir, f"{lang_code}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(trans, f, indent=4, ensure_ascii=False)
    
    def translate(self, text):
        """Translate text to current language"""
        if self.current_language == "en":
            # If switching from Turkish to English, check if there's a reverse translation
            return self.reverse_translations.get(text, text)
        else:
            # Otherwise, look up translation as normal
            return self.translations.get(text, text)
    
    def reload(self):
        """Reload translations (call after language change)"""
        self.load_settings()
        self.load_translations()

# Global translator instance
translator = Translator()

def translate(text):
    """Translate text to current language"""
    return translator.translate(text)

def reload_translations():
    """Reload translations (call after language change)"""
    translator.reload() 