import sqlite3
import os
import shutil

# Önce veritabanını yedekleyelim
print("Veritabanı yedekleniyor...")
shutil.copy2("tailor_shop.db", "tailor_shop_backup.db")
print("Yedekleme tamamlandı: tailor_shop_backup.db")

# Veritabanına bağlan
conn = sqlite3.connect("tailor_shop.db")
cursor = conn.cursor()

# Eski servis isimlerini ve açıklamalarını Türkçeleştir
service_translations = [
    {"old_name": "Hem Adjustment", "new_name": "Paça Düzeltme", "new_desc": "Paça boylarını kısaltma veya uzatma"},
    {"old_name": "Button Replacement", "new_name": "Düğme Değiştirme", "new_desc": "Eksik veya kırık düğmeleri değiştirme"},
    {"old_name": "Zipper Repair", "new_name": "Fermuar Tamiri", "new_desc": "Bozuk fermuarları tamir etme veya değiştirme"},
    {"old_name": "Patch Application", "new_name": "Yama Uygulama", "new_desc": "Hasarlı bölgelere yama uygulama"},
    {"old_name": "Seam Repair", "new_name": "Dikiş Tamiri", "new_desc": "Yırtık veya gevşek dikişleri düzeltme"},
    {"old_name": "Alteration", "new_name": "Tadilat", "new_desc": "Kıyafet boyutu veya şeklini değiştirme"},
    {"old_name": "Waist Adjustment", "new_name": "Bel Ayarı", "new_desc": "Pantolon veya eteklerin bel ayarını düzeltme"},
    {"old_name": "Sleeve Shortening", "new_name": "Kol Kısaltma", "new_desc": "Kol boyunu kısaltma"}
]

# Çevirileri güncelle
for service in service_translations:
    cursor.execute(
        "UPDATE services SET name = ?, description = ? WHERE name = ?",
        (service["new_name"], service["new_desc"], service["old_name"])
    )
    print(f"Güncellendi: {service['old_name']} -> {service['new_name']}")

# İşlemi kaydet
conn.commit()

# Servisleri listele
print("\nGüncellenmiş servis listesi:")
cursor.execute("SELECT name, description FROM services")
for row in cursor.fetchall():
    print(f"- {row[0]}: {row[1]}")

conn.close()
print("\nİşlem tamamlandı.") 