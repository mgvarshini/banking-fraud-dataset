"""
Real-World Banking Transaction Dataset Generator
- 10 Accounts | 1 Month | 1500 Transactions | 50 Columns
- Designed for Fraud Detection / AWS Pipeline ingestion
"""

import random
import uuid
import hashlib
import json
import csv
from datetime import datetime, timedelta

random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────
START_DATE = datetime(2026, 10, 1, 0, 0, 0)
END_DATE   = datetime(2026, 10, 31, 23, 59, 59)
NUM_ACCOUNTS     = 10
NUM_TRANSACTIONS = 1500
FRAUD_RATE       = 0.04   # ~4% fraud

ACCOUNT_TYPES   = ["CHECKING", "SAVINGS", "CURRENT", "PREMIUM", "JOINT"]
GENDERS         = ["M", "F", "NB"]
KYC_STATUS      = ["VERIFIED", "PENDING", "FAILED"]
CURRENCIES      = ["USD", "EUR", "GBP", "INR", "AED", "SGD"]
CHANNELS        = ["MOBILE_APP", "WEB", "ATM", "BRANCH", "POS_TERMINAL", "PHONE_BANKING", "API"]
TX_TYPES        = ["DEBIT", "CREDIT", "TRANSFER", "REVERSAL", "REFUND", "FEE", "INTEREST"]
TX_CATEGORIES   = [
    "GROCERY", "FUEL", "UTILITIES", "RENT", "SALARY", "DINING",
    "ENTERTAINMENT", "HEALTHCARE", "INSURANCE", "TRAVEL", "SHOPPING",
    "EDUCATION", "SUBSCRIPTION", "INVESTMENT", "LOAN_EMI", "CHARITY",
    "GOVERNMENT_TAX", "CASH_WITHDRAWAL", "WIRE_TRANSFER", "P2P_PAYMENT"
]
MERCHANT_CATEGORIES = [
    "5411", "5541", "4900", "6011", "5812", "7832",
    "5912", "4511", "5999", "7011", "5200", "8049",
    "6300", "5944", "8211", "7011", "5311", "9311", "6012", "4829"
]
PAYMENT_NETWORKS = ["VISA", "MASTERCARD", "AMEX", "RUPAY", "UPI", "SWIFT", "ACH", "SEPA"]
DEVICE_TYPES    = ["iOS", "Android", "Web_Browser", "ATM_Device", "POS_Terminal", "Unknown"]
AUTH_METHODS    = ["PIN", "BIOMETRIC", "OTP", "PASSWORD", "CONTACTLESS", "CHIP", "SIGNATURE"]
RISK_LEVELS     = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
COUNTRIES       = ["US", "GB", "IN", "AE", "SG", "DE", "FR", "AU", "CA", "JP"]
CITIES_BY_COUNTRY = {
    "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "GB": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
    "IN": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"],
    "AE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "SG": ["Singapore"],
    "DE": ["Berlin", "Munich", "Frankfurt"],
    "FR": ["Paris", "Lyon", "Marseille"],
    "AU": ["Sydney", "Melbourne", "Brisbane"],
    "CA": ["Toronto", "Vancouver", "Montreal"],
    "JP": ["Tokyo", "Osaka", "Nagoya"],
}
DECLINE_CODES = ["00", "00", "00", "00", "00", "51", "05", "14", "54", "57", "61", "65", "96"]
STATUS_OPTIONS = ["APPROVED", "APPROVED", "APPROVED", "APPROVED", "DECLINED", "PENDING", "REVERSED"]

FIRST_NAMES = ["Alice","Bob","Carol","David","Eva","Frank","Grace","Hiro","Iris","James"]
LAST_NAMES  = ["Smith","Patel","Nguyen","Garcia","Kim","Müller","Tanaka","Okafor","Rossi","Singh"]

# ── Generate 10 Accounts ─────────────────────────────────────────────────────
accounts = []
for i in range(NUM_ACCOUNTS):
    country = random.choice(COUNTRIES)
    city    = random.choice(CITIES_BY_COUNTRY[country])
    acc = {
        "account_id"       : f"ACC{str(i+1).zfill(6)}",
        "account_number"   : f"{random.randint(1000000000, 9999999999)}",
        "account_type"     : random.choice(ACCOUNT_TYPES),
        "account_holder"   : f"{FIRST_NAMES[i]} {LAST_NAMES[i]}",
        "holder_dob"       : (datetime(1990,1,1) - timedelta(days=random.randint(0,10000))).strftime("%Y-%m-%d"),
        "holder_gender"    : random.choice(GENDERS),
        "kyc_status"       : random.choice(KYC_STATUS),
        "credit_score"     : random.randint(580, 850),
        "account_currency" : random.choice(CURRENCIES),
        "account_country"  : country,
        "account_city"     : city,
        "monthly_income"   : round(random.uniform(3000, 25000), 2),
        "account_balance"  : round(random.uniform(500, 150000), 2),
        "is_high_value"    : random.random() < 0.2,
    }
    accounts.append(acc)

# ── Helper Functions ─────────────────────────────────────────────────────────
def random_timestamp(start, end):
    delta = end - start
    secs  = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=secs)

def random_ip():
    return f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def random_lat_lon(country):
    bounds = {
        "US":(24.5,49.0,-125.0,-66.0), "GB":(49.9,60.8,-8.6,1.8),
        "IN":(8.1,37.1,68.2,97.4),     "AE":(22.6,26.1,51.6,56.4),
        "SG":(1.25,1.47,103.6,104.0),  "DE":(47.3,55.1,5.9,15.0),
        "FR":(41.3,51.1,-5.1,9.6),     "AU":(-43.6,-10.7,113.3,153.6),
        "CA":(42.0,83.0,-141.0,-52.6), "JP":(30.4,45.5,130.0,145.8),
    }
    b = bounds.get(country, (0,60,-180,180))
    lat = round(random.uniform(b[0], b[1]), 6)
    lon = round(random.uniform(b[2], b[3]), 6)
    return lat, lon

def generate_merchant_name(category):
    prefixes = ["Global","Premier","City","Metro","National","Online","Express","Smart","Quick","Fast"]
    suffixes = {
        "GROCERY":["Mart","Superstore","Fresh","Bazaar"],
        "FUEL":["Petrol","Fuels","Gas Station","Energy"],
        "DINING":["Kitchen","Bistro","Café","Restaurant","Eats"],
        "SHOPPING":["Store","Boutique","Mall","Shop"],
        "TRAVEL":["Airways","Hotels","Travel","Voyages"],
        "HEALTHCARE":["Pharmacy","Clinic","Health","MedCare"],
    }
    suf_list = suffixes.get(category, ["Services","Corp","Ltd","Group"])
    return f"{random.choice(prefixes)} {random.choice(suf_list)}"

# ── Generate 1500 Transactions ────────────────────────────────────────────────
transactions = []
for _ in range(NUM_TRANSACTIONS):
    acc        = random.choice(accounts)
    ts         = random_timestamp(START_DATE, END_DATE)
    tx_type    = random.choice(TX_TYPES)
    category   = random.choice(TX_CATEGORIES)
    channel    = random.choice(CHANNELS)
    network    = random.choice(PAYMENT_NETWORKS)
    device     = random.choice(DEVICE_TYPES)
    auth       = random.choice(AUTH_METHODS)
    country    = acc["account_country"]
    lat, lon   = random_lat_lon(country)
    city       = random.choice(CITIES_BY_COUNTRY[country])

    # Amount logic: fraud transactions tend to be higher amounts
    is_fraud   = random.random() < FRAUD_RATE
    if is_fraud:
        amount = round(random.uniform(800, 15000), 2)
    else:
        amount = round(random.expovariate(1/150), 2)
        amount = min(amount, 9999.99)

    currency   = acc["account_currency"]
    status     = random.choice(STATUS_OPTIONS)
    decline_code = random.choice(DECLINE_CODES) if status == "DECLINED" else "00"
    merchant   = generate_merchant_name(category)
    merchant_id= f"MID{random.randint(100000,999999)}"
    mcc        = random.choice(MERCHANT_CATEGORIES)
    response_ms= random.randint(80, 4500)
    risk_score = round(random.uniform(0.8, 1.0), 4) if is_fraud else round(random.uniform(0.0, 0.45), 4)
    risk_level = "CRITICAL" if risk_score > 0.85 else ("HIGH" if risk_score > 0.65 else ("MEDIUM" if risk_score > 0.35 else "LOW"))
    ip_address = random_ip()
    device_fp  = hashlib.md5(f"{acc['account_id']}{device}{ip_address}".encode()).hexdigest()[:16]
    session_id = str(uuid.uuid4())
    tx_id      = f"TXN{uuid.uuid4().hex[:12].upper()}"
    ref_num    = f"REF{random.randint(10000000,99999999)}"
    fee        = round(amount * random.uniform(0.001, 0.025), 2) if tx_type not in ["INTEREST","REFUND"] else 0.0
    tax        = round(amount * random.uniform(0.0, 0.12), 2)
    net_amount = round(amount - fee - tax, 2)
    balance_after = round(acc["account_balance"] - amount if tx_type == "DEBIT" else acc["account_balance"] + amount, 2)
    velocity_1h= random.randint(1, 20) if is_fraud else random.randint(1, 5)
    velocity_24h= random.randint(velocity_1h, 80) if is_fraud else random.randint(velocity_1h, 15)
    distance_km= round(random.uniform(100, 8000), 1) if is_fraud else round(random.uniform(0, 150), 1)
    is_intl    = country != acc["account_country"] or random.random() < 0.1
    is_recurring = random.random() < 0.15
    is_high_risk_country = country in ["IR","KP","SY","MM"] or (is_fraud and random.random() < 0.3)

    row = {
        # ── Identity & Account ──────────────────────────────
        "transaction_id"         : tx_id,
        "account_id"             : acc["account_id"],
        "account_number_masked"  : f"****{acc['account_number'][-4:]}",
        "account_type"           : acc["account_type"],
        "account_holder_name"    : acc["account_holder"],
        "kyc_status"             : acc["kyc_status"],
        "credit_score"           : acc["credit_score"],
        "is_high_value_customer" : acc["is_high_value"],

        # ── Transaction Core ────────────────────────────────
        "transaction_datetime"   : ts.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_date"       : ts.strftime("%Y-%m-%d"),
        "transaction_time"       : ts.strftime("%H:%M:%S"),
        "day_of_week"            : ts.strftime("%A"),
        "hour_of_day"            : ts.hour,
        "transaction_type"       : tx_type,
        "transaction_category"   : category,
        "transaction_status"     : status,
        "decline_code"           : decline_code,
        "reference_number"       : ref_num,
        "session_id"             : session_id,

        # ── Financials ──────────────────────────────────────
        "transaction_amount"     : amount,
        "currency_code"          : currency,
        "transaction_fee"        : fee,
        "tax_amount"             : tax,
        "net_amount"             : net_amount,
        "account_balance_after"  : balance_after,
        "monthly_income"         : acc["monthly_income"],

        # ── Merchant ────────────────────────────────────────
        "merchant_name"          : merchant,
        "merchant_id"            : merchant_id,
        "merchant_category_code" : mcc,
        "merchant_country"       : country,
        "merchant_city"          : city,

        # ── Channel & Device ────────────────────────────────
        "channel"                : channel,
        "payment_network"        : network,
        "device_type"            : device,
        "auth_method"            : auth,
        "ip_address"             : ip_address,
        "device_fingerprint"     : device_fp,
        "response_time_ms"       : response_ms,

        # ── Geolocation ─────────────────────────────────────
        "geo_latitude"           : lat,
        "geo_longitude"          : lon,
        "transaction_country"    : country,
        "transaction_city"       : city,
        "is_international"       : is_intl,
        "distance_from_home_km"  : distance_km,

        # ── Risk & Fraud Signals ────────────────────────────
        "risk_score"             : risk_score,
        "risk_level"             : risk_level,
        "velocity_last_1h"       : velocity_1h,
        "velocity_last_24h"      : velocity_24h,
        "is_high_risk_country"   : is_high_risk_country,
        "is_recurring_merchant"  : is_recurring,
        "is_fraud"               : is_fraud,
        "fraud_type"             : (random.choice(["CARD_NOT_PRESENT","ACCOUNT_TAKEOVER","SYNTHETIC_ID","MONEY_LAUNDERING","FRIENDLY_FRAUD"]) if is_fraud else "NONE"),
    }
    transactions.append(row)

# Sort by timestamp
transactions.sort(key=lambda x: x["transaction_datetime"])

# ── Write CSV ────────────────────────────────────────────────────────────────
OUTPUT_PATH = r"C:\Users\varsh\.gemini\antigravity\scratch\banking_dataset\banking_transactions_1500.csv"
fieldnames  = list(transactions[0].keys())

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(transactions)

# ── Summary ──────────────────────────────────────────────────────────────────
fraud_count    = sum(1 for t in transactions if t["is_fraud"])
total_volume   = sum(t["transaction_amount"] for t in transactions)
print(f"[DONE] Dataset generated: {OUTPUT_PATH}")
print(f"   Rows          : {len(transactions)}")
print(f"   Columns       : {len(fieldnames)}")
print(f"   Fraud txns    : {fraud_count} ({fraud_count/len(transactions)*100:.1f}%)")
print(f"   Total Volume  : {total_volume:,.2f}")
print(f"   Date Range    : {transactions[0]['transaction_date']} -> {transactions[-1]['transaction_date']}")
print(f"\n-- Column Names ({len(fieldnames)}) --")
for i, col in enumerate(fieldnames, 1):
    print(f"  {i:02d}. {col}")
