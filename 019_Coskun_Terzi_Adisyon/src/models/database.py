import sqlite3
import os
import datetime

class Database:
    def __init__(self, db_file="tailor_shop.db"):
        # Determine the absolute path for the database file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, db_file)
        self.connection = None
        self.create_tables()
    
    def connect(self):
        """Establish connection to the SQLite database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Services table (predefined repair types)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
        ''')
        
        # Transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
        ''')
        
        # Transaction items table (individual service items in a transaction)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            service_id INTEGER,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
        ''')
        
        # Insert default services if the services table is empty
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            default_services = [
                ("Paça Düzeltme", "Paça boylarını kısaltma veya uzatma", 15.0),
                ("Düğme Değiştirme", "Eksik veya kırık düğmeleri değiştirme", 5.0),
                ("Fermuar Tamiri", "Bozuk fermuarları tamir etme veya değiştirme", 20.0),
                ("Yama Uygulama", "Hasarlı bölgelere yama uygulama", 25.0),
                ("Dikiş Tamiri", "Yırtık veya gevşek dikişleri düzeltme", 10.0),
                ("Tadilat", "Kıyafet boyutu veya şeklini değiştirme", 30.0),
                ("Bel Ayarı", "Pantolon veya eteklerin bel ayarını düzeltme", 22.0),
                ("Kol Kısaltma", "Kol boyunu kısaltma", 18.0)
            ]
            cursor.executemany(
                "INSERT INTO services (name, description, price) VALUES (?, ?, ?)",
                default_services
            )
        
        conn.commit()
        conn.close()
    
    # Customer methods
    def add_customer(self, name, surname, phone=None, location=None):
        """Add a new customer to the database"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, surname, phone, location) VALUES (?, ?, ?, ?)",
            (name, surname, phone, location)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return customer_id
    
    def update_customer(self, customer_id, name, surname, phone, location):
        """Update an existing customer's information"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET name=?, surname=?, phone=?, location=? WHERE id=?",
            (name, surname, phone, location, customer_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def search_customers(self, search_term):
        """Search for customers by name, surname, or phone number"""
        conn = self.connect()
        cursor = conn.cursor()
        search_pattern = f"%{search_term}%"
        cursor.execute(
            """
            SELECT * FROM customers 
            WHERE name LIKE ? OR surname LIKE ? OR phone LIKE ?
            ORDER BY surname, name
            """,
            (search_pattern, search_pattern, search_pattern)
        )
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers
    
    def get_customer(self, customer_id):
        """Retrieve customer by ID"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        return dict(customer) if customer else None
    
    # Service methods
    def get_all_services(self):
        """Get all available repair services"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services ORDER BY name")
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return services
    
    def get_service(self, service_id):
        """Get a specific service by ID"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id=?", (service_id,))
        service = cursor.fetchone()
        conn.close()
        return dict(service) if service else None
    
    # Transaction methods
    def create_transaction(self, customer_id, total_amount, note=None):
        """Create a new transaction"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (customer_id, total_amount, note) VALUES (?, ?, ?)",
            (customer_id, total_amount, note)
        )
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id
    
    def add_transaction_item(self, transaction_id, service_id, quantity, price):
        """Add an item to a transaction"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transaction_items (transaction_id, service_id, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (transaction_id, service_id, quantity, price)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_customer_history(self, customer_id):
        """Get transaction history for a specific customer"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get all transactions for the customer
        cursor.execute(
            """
            SELECT t.id, t.total_amount, t.created_at, t.note
            FROM transactions t
            WHERE t.customer_id = ?
            ORDER BY t.created_at DESC
            """,
            (customer_id,)
        )
        transactions = [dict(row) for row in cursor.fetchall()]
        
        # For each transaction, get the items
        for transaction in transactions:
            cursor.execute(
                """
                SELECT ti.id, ti.quantity, ti.price, s.name as service_name, s.description
                FROM transaction_items ti
                JOIN services s ON ti.service_id = s.id
                WHERE ti.transaction_id = ?
                """,
                (transaction['id'],)
            )
            transaction['items'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return transactions 