## Windows Desktop Application Technology Stack

### Frontend / UI
- **Framework Options:**
  - **WPF (Windows Presentation Foundation)** - Modern UI framework with XAML
  - **Windows Forms** - Simpler but mature framework, easier to develop
  - **Electron** - Web technologies in desktop application wrapper

### Backend / Logic
- **Programming Language:**
  - **C#/.NET** - Microsoft's primary language for Windows development
  - **Python** with desktop frameworks
  - **JavaScript** (if using Electron)

### Database
- **SQLite** - Embedded database, perfect for single-user applications
  - No server installation required
  - Single file database
  - Reliable transaction support
  - Easy backups (just copy the file)

### Printing
- **Windows Printing API**
  - Direct integration with Windows printer drivers
  - Support for thermal label printers (DYMO, Brother, etc.)
  - Print preview capability

### Application Architecture
- **Local Installation:**
  - Installed directly on the shop computer
  - All data stored locally
  - No internet connection required for operation

### Deployment
- **Installation Package:**
  - Windows installer (.msi or .exe)
  - Built-in database initialization
  - Desktop shortcuts
  - Start menu integration

### System Requirements
- **Operating System:** Windows 10 or Windows 11
- **Minimum Hardware:**
  - 4GB RAM
  - 100MB free disk space (plus space for customer database)
  - 1366x768 screen resolution or higher
  - USB port for label printer connection