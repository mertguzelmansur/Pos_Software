## Database Schema for Tailor Shop Management System

```sql
-- Customers table to store all customer information
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(50) NOT NULL,
    Surname VARCHAR(50) NOT NULL,
    PhoneNumber VARCHAR(20) NOT NULL,
    Location VARCHAR(100),
    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastVisitDate DATETIME,
    Notes TEXT
);

-- Services table to store all repair service types
CREATE TABLE Services (
    ServiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    ServiceName VARCHAR(50) NOT NULL,
    Description TEXT,
    Price DECIMAL(10,2) NOT NULL,
    EstimatedCompletionTime INTEGER, -- in hours
    IsActive BOOLEAN DEFAULT 1
);

-- Transactions table for storing main transaction information
CREATE TABLE Transactions (
    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER NOT NULL,
    TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10,2) NOT NULL,
    IsPaid BOOLEAN DEFAULT 0,
    Notes TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Transaction details for storing individual items in a transaction
CREATE TABLE TransactionDetails (
    DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    TransactionID INTEGER NOT NULL,
    ServiceID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL DEFAULT 1,
    UnitPrice DECIMAL(10,2) NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    ClothType VARCHAR(50),
    Status VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Completed, Delivered
    PromisedCompletionDate DATETIME,
    ActualCompletionDate DATETIME,
    FOREIGN KEY (TransactionID) REFERENCES Transactions(TransactionID),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
);

-- Labels table to track printed labels
CREATE TABLE Labels (
    LabelID INTEGER PRIMARY KEY AUTOINCREMENT,
    DetailID INTEGER NOT NULL,
    PrintDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    ReprintCount INTEGER DEFAULT 0,
    FOREIGN KEY (DetailID) REFERENCES TransactionDetails(DetailID)
);

-- Initial data for Services table
INSERT INTO Services (ServiceName, Description, Price) VALUES
('Hem Pants', 'Shortening or lengthening pants', 12.00),
('Replace Zipper', 'Replace broken zipper on pants/skirt', 15.00),
('Patch Repair', 'Apply patch to damaged area', 8.00),
('Button Replacement', 'Replace missing or broken buttons', 5.00),
('Resize Garment', 'Take in or let out garment for better fit', 25.00),
('Sleeve Adjustment', 'Shorten or lengthen sleeves', 18.00);
```

## Sample API Endpoints

```javascript
// Customer Endpoints
GET /api/customers - Get all customers
GET /api/customers/:id - Get specific customer
GET /api/customers/search/:term - Search customers
POST /api/customers - Create new customer
PUT /api/customers/:id - Update customer
DELETE /api/customers/:id - Delete customer

// Service Endpoints
GET /api/services - Get all services
GET /api/services/:id - Get specific service
POST /api/services - Create new service
PUT /api/services/:id - Update service
DELETE /api/services/:id - Delete service

// Transaction Endpoints
GET /api/transactions - Get all transactions
GET /api/transactions/:id - Get specific transaction
GET /api/transactions/customer/:id - Get customer's transactions
POST /api/transactions - Create new transaction
PUT /api/transactions/:id - Update transaction
DELETE /api/transactions/:id - Delete transaction

// Label Endpoints
GET /api/labels/print/:detailId - Generate label for printing
POST /api/labels/reprint/:detailId - Reprint label
```

## Label Template Structure

```json
{
  "template": {
    "size": {
      "width": "10cm",
      "height": "5cm"
    },
    "sections": [
      {
        "type": "header",
        "content": "TAILOR SHOP",
        "style": {
          "font-size": "12pt",
          "font-weight": "bold",
          "text-align": "center"
        }
      },
      {
        "type": "customer-info",
        "fields": ["name", "phone"],
        "style": {
          "font-size": "10pt"
        }
      },
      {
        "type": "service-info",
        "fields": ["service", "cloth-type", "quantity", "price"],
        "style": {
          "font-size": "10pt"
        }
      },
      {
        "type": "dates",
        "fields": ["received-date", "promised-date"],
        "style": {
          "font-size": "9pt"
        }
      },
      {
        "type": "notes",
        "content": "{{ customer_notes }}",
        "style": {
          "font-size": "8pt",
          "font-style": "italic"
        }
      },
      {
        "type": "barcode",
        "content": "{{ transaction_id }}",
        "style": {
          "height": "0.5cm"
        }
      }
    ]
  }
}
```

## Configuration Options

```json
{
  "application": {
    "name": "Tailor Shop Management System",
    "version": "1.0.0"
  },
  "database": {
    "type": "sqlite",
    "path": "./data/tailorshop.db"
  },
  "printing": {
    "defaultPrinter": "DYMO LabelWriter 450",
    "labelWidth": "10cm",
    "labelHeight": "5cm",
    "dpi": 300
  },
  "ui": {
    "theme": "light",
    "language": "en",
    "dateFormat": "MM/DD/YYYY"
  },
  "backup": {
    "enabled": true,
    "frequency": "daily",
    "time": "23:00",
    "location": "./backups/",
    "keepDays": 30
  }
}
```