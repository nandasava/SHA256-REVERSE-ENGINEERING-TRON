TRON Private Key Scanner

This tool generates random TRON private keys, derives their addresses, and checks for balances on TronGrid.
If an address has funds, the private key, address, and balance are saved, and you receive an email.

Setup Instructions:
1. Install Python (https://www.python.org/downloads/).
2. Install required Python libraries by running:
   pip install ecdsa base58 requests tqdm
3. Edit `linear.py` to set your sender email and App Password in:
   SMTP_USERNAME = "your-sender-email@gmail.com"
   SMTP_PASSWORD = "your-app-password"
4. Double-click `run_scanner.bat` to start the scanner.

Resume After Shutdown:
The scanner saves all scanned keys to `scanned_keys.txt`, so if the computer shuts down, it will resume from where it left off.

Files Included:
- linear.py - Main Python script.
- run_scanner.bat - Windows batch file to launch the scanner.
- scanned_keys.txt - List of all scanned keys (auto-saved).
- funded_keys.txt - List of addresses with funds.

Disclaimer:
This software is for educational and research purposes only.
