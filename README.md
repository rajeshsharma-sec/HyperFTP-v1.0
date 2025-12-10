# HyperFTP v1.0.0

A professional FTP client built with Python featuring a modern GUI interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- **FTP & FTPS Support** - Secure connections with TLS/SSL encryption
- **Dual-Pane Browser** - Navigate local and remote files side-by-side
- **File Operations** - Upload, download, rename, and delete files/folders
- **Connection Manager** - Save and manage multiple FTP connections
- **Transfer Modes** - Support for both passive and active modes
- **Progress Tracking** - Real-time transfer progress with logging
- **Keyboard Shortcuts** - Efficient navigation with hotkeys

## 🚀 Quick Start

### Option 1: Windows Executable (Recommended)

Download the standalone executable - no Python installation required:

1. Go to [Releases](https://github.com/rajeshsharma-sec/HyperFTP-v1.0/releases)
2. Download `HyperFTP.exe`
3. Double-click to run

### Option 2: Run from Source

#### Prerequisites

- Python 3.8 or higher
- tkinter (usually included with Python)

#### Installation

```bash
# Clone the repository
git clone https://github.com/rajeshsharma-sec/HyperFTP-v1.0.git

# Navigate to the directory
cd HyperFTP-v1.0

# Run the application
python HyperFTP.py
```

### Build Executable Yourself

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name "HyperFTP" HyperFTP.py

# Find the executable in dist/ folder
```

## 📖 Usage

1. **Connect to Server**
   - Enter host, port, username, and password
   - Check "Anonymous" for anonymous FTP login
   - Check "TLS/SSL" for secure FTPS connections
   - Click "Connect"

2. **Transfer Files**
   - Double-click folders to navigate
   - Select files and click Upload/Download buttons
   - Use right-click context menu for more options

3. **Keyboard Shortcuts**
   | Shortcut | Action |
   |----------|--------|
   | `Ctrl+N` | New Connection |
   | `Ctrl+U` | Upload Selected |
   | `Ctrl+D` | Download Selected |
   | `F5` | Refresh Local |
   | `F6` | Refresh Remote |

4. **Save Connections**
   - Click "Save Connection" to store current settings
   - Select from dropdown to load saved connections

## 🛠️ Technical Details

- **GUI Framework**: Tkinter with ttk styling
- **FTP Library**: Python's built-in `ftplib`
- **Threading**: Non-blocking file transfers
- **Config Storage**: JSON-based connection profiles

## 📁 Project Structure

```
HyperFTP-v1.0/
├── HyperFTP.py          # Main application source
├── README.md            # Documentation
├── dist/
│   └── HyperFTP.exe     # Windows executable
└── hyperftp_config.json # Saved connections (auto-generated)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**rajeshsharma-sec**

- GitHub: [@rajeshsharma-sec](https://github.com/rajeshsharma-sec)

---

<p align="center">
  Made by rajeshsharma-sec
</p>
