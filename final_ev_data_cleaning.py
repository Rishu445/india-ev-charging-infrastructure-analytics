"""
FINAL EV CHARGING DATA CLEANING PIPELINE

Input : ev_charging_stations_india.csv
Output: ev_charging_stations_india_final_consistent.csv
Audit : ev_charging_state_city_corrections_final.csv

Design goals
------------
1. Normalize state/city/name/address text.
2. Recover selected missing address/coordinate values from previously verified
   project corrections.
3. Correct corrupted state values using station-specific evidence and a
   canonical city -> state reference.
4. Correct high-confidence city mistakes (e.g. Guwahati rows labeled Delhi,
   KSEBL station rows labeled Thiruvananthapuram, etc.).
5. Remove exact and hidden duplicates after corrections.
6. Validate that canonical cities do not map to multiple states.

This script uses only the Python standard library so it can be rerun without
pandas/openpyxl.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "ev_charging_stations_india.csv"
OUTPUT = BASE_DIR / "ev_charging_stations_india_final_consistent.csv"
AUDIT = BASE_DIR / "ev_charging_state_city_corrections_final.csv"

# ---------------------------------------------------------------------------
# 1. Previously verified normalization / recovery dictionaries.
# ---------------------------------------------------------------------------
STATE_MAP = {
    "maharashra": "Maharashtra", "maharashtra": "Maharashtra",
    "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "taminadu": "Tamil Nadu",
    "telengana": "Telangana", "hyderabadu00a0": "Telangana",
    "westbengal": "West Bengal", "west bengal": "West Bengal",
    "punjab": "Punjab", "chattisgarh": "Chhattisgarh",
    "uttarkhand": "Uttarakhand", "uttrakhand": "Uttarakhand", "uttarakhand": "Uttarakhand",
    "andhra pradesh": "Andhra Pradesh", "andhrapradesh": "Andhra Pradesh", "andra pradesh": "Andhra Pradesh",
    "jammu": "Jammu and Kashmir", "jammu & kashmir": "Jammu and Kashmir", "jammu and kashmir": "Jammu and Kashmir",
    "pondicherry": "Puducherry", "puducherry": "Puducherry", "karala": "Kerala", "harayana": "Haryana",
    "delhi ncr": "Delhi", "hyderabad": "Telangana", "ernakulam": "Kerala", "kochi": "Kerala",
    "limbdi": "Gujarat", "bhubhaneswar": "Odisha", "jajpur": "Odisha", "rajahmundry": "Andhra Pradesh",
    "hisar": "Haryana", "chikhali": "Maharashtra", "andaman": "Andaman and Nicobar Islands",
}

CITY_MAP = {
    "bangalore": "Bengaluru", "banglore": "Bengaluru", "bengaluru": "Bengaluru",
    "gurgaon": "Gurugram", "gurugram": "Gurugram",
    "new delhi": "New Delhi", "newdelhi": "New Delhi",
    "chennai": "Chennai", "hyderabad": "Hyderabad", "ahmedabad": "Ahmedabad", "pune": "Pune",
    "jaipur": "Jaipur", "kolkata": "Kolkata", "bhubaneswar": "Bhubaneswar", "bhubhaneswar": "Bhubaneswar",
    "kochi": "Kochi", "cochin": "Kochi", "trivandrum": "Thiruvananthapuram",
    "thiruvanthapuram": "Thiruvananthapuram", "thiruvananthapuram": "Thiruvananthapuram",
    "calicut": "Kozhikode", "kozhikode": "Kozhikode", "vizag": "Visakhapatnam", "visakhapatnam": "Visakhapatnam",
    "trichy": "Tiruchirappalli", "tiruchirappalli": "Tiruchirappalli", "mysore": "Mysuru", "mysuru": "Mysuru",
    "madras": "Chennai", "navi mumbai": "Navi Mumbai", "greater noida": "Greater Noida", "noida": "Noida",
    "shabhad": "Shahabad", "shahabad": "Shahabad", "hyderbad": "Hyderabad", "kosi kalan": "Kosi Kalan",
    "vasai-virar": "Vasai-Virar", "pimpri-chinchwad": "Pimpri-Chinchwad", "pimpri chinchwad": "Pimpri-Chinchwad",
    "belgavi": "Belagavi", "belgaum": "Belgaum", "kasargod": "Kasaragod", "anantapur": "Anantapur",
    "ananthapur": "Anantapur", "tirupathi": "Tirupati", "tirupati": "Tirupati", "mangalore": "Mangalore",
    "mangaluru": "Mangalore", "hubli": "Hubli", "thrissur": "Thrissur", "trichur": "Thrissur",
}

COORDINATE_FIXES = {
    "Jamoliwala AC Charging Station": (30.388600, 78.065400),
    "Ather Space - Dehradun": (30.3382561, 78.058454),
    "Shankar Motors, Patliputra Industrial Area": (25.634199, 85.105510),
    "Key Motors, Bannerghatta Road": (12.889141, 77.597289),
}

COORDINATE_FILLS = {
    "SAR Motors": (26.111076, 91.767921),
    "Panvel Industrial Fastners, Mum-Pune Expressway": (19.022480, 73.098990),
    "IOCL - Jopadevi Petroleum, Talegaon-Chakan Rd": (18.742876, 73.770292),
    "Gokulam Park Munnar, Power House Road": (10.029793, 77.045859),
}

ADDRESS_FILLS = {
    "AARGO CSC MINTO ROAD": "CSC NDMC CENTER MINTO ROAD OPPOSITE K BLOCK, NEW DELHI,NEW DELHI,110001",
    "AARGO ASLI PAPPU DHABA": "NEAR KOTWAN POLICE CHOWKI,UP BORDER,KOSI KALAN,KOSI KOTWAN,UTTAR PRADESH",
    "Statiq RnD Centre DC Charging Station": "Statiq RnD Centre, Plot 80A, Phase V, Udyog Vihar, Sector 19, Gurugram, Haryana 122017",
    "Hotel The Executive Inn AC Charging Station": "Hotel The Executive Inn, Near Ratnakar Bank, Nagar, Manmad Rd, opp. Indian Oil Petrol Pump, Shirdi, Maharashtra 423109, India",
    "Hotel Bliss County DC Charging Station": "Hotel Bliss County, Mumbai - Agra National Hwy, Dhule, Maharashtra 414006",
    "Savoy Suites Manesar": "R 75, Sector 1 Main Rd, Sector 1, IMT Manesar, Gurugram, Haryana 122052, India",
    "MV EV DC Charging Station": "Vakil Estate, Dahanu Road East, Dahanu, Maharashtra 401602, India",
    "Jamoliwala AC Charging Station": "Jamoliwala, Dehradun, Uttarakhand, India",
    "Bhajan Singh Da Dhabha DC Charging Station": "Toll Plaza, Old Mumbai - Pune Hwy, near Somatane Phata, Varsoli, Talegaon Dabhade, Maharashtra, India",
    "Hotel Prabhat Palace DC Charging Station": "Hotel Prabhat Palace, Jammu Road, Post Office, Katra, Jammu and Kashmir 182301, India",
    "Mehak Garden Charging Station": "Mehak Garden Subway Restaurant, Sirsa R/o Huda 416, Sector-20, Sirsa, Haryana 125055, India",
    "Savoy Suites Noida": "Entrance Gate, Near Parking Area, A-79A, Metro Station Road, Noida, Uttar Pradesh 201301, India",
    "Savoy Suites Greater Noida": "Savoy Suites Pari Chowk, Ansal Plaza, Noida-Greater Noida Expressway, Amit Nagar, Sadarpur, Greater Noida, Uttar Pradesh 201310",
    "Hotel Highway King Shahpura DC Charging Station": "Hotel Highwayking Shahpura, Main Delhi-Jaipur Highway NH-8, near Paota, Village Antela, Shahpura, Rajasthan 303119, India",
    "Aman Hotel Kurukshetra DC Charging Station": "Aman Hotel, NH-1, GT Karnal Rd, Sidhu Dhani, Kurukshetra, Shahabad, Haryana 136135, India",
    "Evershine Tower Jaipur DC Charging Station": "F-1, Amrapali Marg, Vaishali Nagar, Jaipur, Rajasthan 302021, India",
    "Hotel Shree Veg Solapur DC Charging Station": "Hotel Shree Veg, Solapur - Pune Hwy, Bhadalwadi, Baramati, Maharashtra 413104, India",
    "Asli Pappu Dhaba Kosi Kalan DC Charging Station": "Asli Pappu Dhaba, Near Kotwan Police Chowki, UP Border, Kosi Kalan, Uttar Pradesh 281403, India",
    "140% Veg Gulshan Dhaba Kotwan DC Charging Station": "140% Veg Gulshan Dhaba, Kotwan, Mathura, Uttar Pradesh 281403, India",
    "ChargePit eMobility Charging Station": "Swastha Homoeopathy, Shop no 1, Metro9, Rahatni, Pune, Maharashtra, India",
    "Manipal Charging Station": "Industrial Area, Manipal, Karnataka 576104, India",
    "PADMASHREE Charging Station": "Betkeri Road, Kotebagilu, Mudbidri, Karnataka 574227, India",
    "Park Plaza Gurgaon DC Charging Station": "B-BLOCK, Sushant Lok Phase I, Sector 43, Gurugram, Haryana 122002, India",
    "AARGO GOLDEN GALAXY HOTEL": "GOLDEN GALAXY HOTELS & RESORTS, 6 Kms from Mathura Rd, Ballabhgarh, Faridabad, Haryana 121004, India",
    "Bramavara Charging Station": "Bramavara, Karnataka 576213, India",
}

# ---------------------------------------------------------------------------
# 2. High-confidence state/city corrections uncovered in the final QA pass.
# ---------------------------------------------------------------------------
STATION_CITY_OVERRIDES = {
    "Neelkanth Star DC Charging Station": "Karnal",
    "Mindra D S Fasteners Charging Station": "Rajkot",
    "Ganpati Petro DC Charging Station Hisar": "Hisar",
    "Ganpati Petro AC Charging Station Hisar": "Hisar",
    "AMC AC Charging Station": "Pimpri-Chinchwad",
    "Mindra EV Charger Shott": "Ahmedabad",
    "Rani Bagh Resort DC Charging Station": "Beawar",
    "The Forum Fiza Mall AC Charging Station Mangalore": "Mangalore",
    "Hotel Reddison Square Katra AC Charging Station": "Katra",
    "Hotel Mount View International AC Charging Station": "Katra",
    "Hotel Dolphin AC Charging Station": "Katra",
    "DMIPL EV Charging Station, Ludhiana": "Ludhiana",
    "HP PETROL PUMP - SAI PETROLEUM,MUMBAI": "Mumbai",
    "ShriSamarth DC Charging Station, Beed": "Beed",
    "Noma Talkies": "Secunderabad",
    "Adani Shantigram": "Ahmedabad",
    "Tiruppur Sree Annapoorna": "Tiruppur",
    "Inox R21": "Gandhinagar",
    "Inox R16": "Gandhinagar",
    "Ather Space, Thane": "Thane",
    "Devaragam Hotel": "Guruvayur",
    "KVR Dream vehicles, Vidya Nagar": "Kasaragod",
    "Orange Auto, Karkhana": "Secunderabad",
    "Yaksh The Art People, Delhi-Jaipur Highway": "Jaipur",
    "Trimurti Petroleum, Panvel": "Panvel",
    "Hotel Aishwarya Bhavan (Safa Electric)": "Tindivanam",
    "KSEBL OLAI": "Kollam",
    "KSEBL PALARIVATTOM": "Kochi",
    "KSEBL VIYYUR": "Thrissur",
    "KSEBL NALLALAM": "Kozhikode",
    "KSEBL CHOVVA": "Kannur",
    "MG BENGALURU": "Bengaluru",
    "Sri Durga Bhavan Elite (Devika Yogaraajan Charging Station)": "Pallikonda",
    "Adyar Ananda Bhavan I Navakkarai": "Coimbatore",
    "Gokulam Sabari, Guruvayur": "Guruvayur",
    "Panchjanya Motors, Bhosari": "Pimpri-Chinchwad",
    "Croma, Kompally": "Secunderabad",
    "Exotikka Restaurant": "Anantapur",
    "Hotel Kalyan Grand I Vandalur": "Chennai",
    "GJ | Chikhali | Chikhli - Hotel Empire": "Chikhli",
    "GJ | Limbdi | HFM (Highway Food Mall)": "Limbdi",
    "Circle Test Station Goa": "Margao",
    "Peep Kitchen": "Panaji",
    "Blive HO": "Panaji",
    "Ather Space Goa": "Porvorim",
    "Antares Restaurant and Beach Club": "Vagator",
    "Highway King Behror Delhi Side DC Charging Station": "Behror",
    "Suket Cafe DC Charging Station Sundar Nagar": "Sundar Nagar",
    "Suket Cafe AC Charging Station Sundar Nagar": "Sundar Nagar",
    "Hans Resort DC Charging Station Rewari": "Rewari",
    "Saviruchi Veg DC Charging Station Mysore": "Malavalli",
    "HPCL - Badarpur Service Station, Gazipur": "Delhi",
    "Tellus Power DC Charging Station": "Pune",
    "Mke Rental Circle Station": "Bengaluru",
    "Decathlon Anubhava": "Bengaluru",
    "Unnati Social Foundation": "Pune",
    "Magenta, Hosur Road": "Bengaluru",
    "Decathlon Bannerghatta": "Bengaluru",
    "Turf Trident": "Chennai",
    "Ather Space - Gujranwala Town": "Delhi",
    "Ather Space - Janakpuri": "Delhi",
    "Ather Space - Lalbagh": "Lucknow",
    "Ather Space Surat": "Surat",
    "Ather Space Ahmedabad": "Ahmedabad",
    "Ranthal Gardens Restaurant": "Thiruvananthapuram",
    "Sihla Energy Sihla Energy": "Malappuram",
    "KSEB NEMOM": "Thiruvananthapuram",
    "Gokul Oottupura NH 47 Veetarian Restaurant": "Kochi",
    "Sree Gokulam Motors, Edapally": "Kochi",
    "Sree Gokulam Motors, Kolancherry": "Kochi",
    "IOCL - SR Adhoc u00e2u0080u0093 COCO, Vytilla": "Kochi",
    "CoastLine Garages, NH 47 Muttom": "Aluva",
    "The Fern An Ecotel Hotel": "Lonavala",
    "UK 27, The Fern": "Belagavi",
    "HPCL Autocare Sajgaon": "Khopoli",
    "Paschim Vidyut Vitaran Pologround": "Indore",
    "D square Mall": "Shoolagiri",
    "Hotel Bliss | Tirupati": "Tirupati",
    "IOCL - JRO Pongam, Thrissur": "Koratty",
    "AARGO GOLDEN GALAXY HOTEL": "Faridabad",
    "Hotel Shree Veg Solapur DC Charging Station": "Baramati",
    "Asli Pappu Dhaba Kosi Kalan DC Charging Station": "Kosi Kalan",
    "140% Veg Gulshan Dhaba Kotwan DC Charging Station": "Kosi Kalan",
    "PADMASHREE Charging Station": "Mudbidri",
    "Park Plaza Gurgaon DC Charging Station": "Gurugram",
    "Savoy Suites Manesar": "Gurugram",
    "Savoy Suites Greater Noida": "Greater Noida",
    "Savoy Suites Noida": "Noida",
    "Nandavan DC Charging Station Nagoan": "Alibag",
    "Bikanerwala, NH 48 Panchgaon": "Gurugram",
    "MH | Nashik | Nashik | Car mall": "Nashik",
}

STATION_STATE_OVERRIDES = {
    "Royal Global University": "Assam",
    "SAR Motors": "Assam",
    "R R Sales": "Assam",
    "Ather Space, Guwahati": "Assam",
    "Ather Service Centre": "Assam",
    "Mindra D S Fasteners Charging Station": "Gujarat",
    "Highway King Behror Delhi Side DC Charging Station": "Rajasthan",
    "Suket Cafe DC Charging Station Sundar Nagar": "Himachal Pradesh",
    "Suket Cafe AC Charging Station Sundar Nagar": "Himachal Pradesh",
    "Hans Resort DC Charging Station Rewari": "Haryana",
    "Saviruchi Veg DC Charging Station Mysore": "Karnataka",
    "The Forum Fiza Mall AC Charging Station Mangalore": "Karnataka",
    "Ashutosh Motors, near NHPC Godown": "Assam",
    "ShriSamarth DC Charging Station, Beed": "Maharashtra",
    "Hotel Reddison Square Katra AC Charging Station": "Jammu and Kashmir",
    "Hotel Mount View International AC Charging Station": "Jammu and Kashmir",
    "Hotel Dolphin AC Charging Station": "Jammu and Kashmir",
    "Circle Test Station Goa": "Goa",
    "KSEBL CHOVVA": "Kerala",
    "KSEBL VIYYUR": "Kerala",
    "KSEBL PALARIVATTOM": "Kerala",
    "KSEBL NALLALAM": "Kerala",
    "HP PETROL PUMP - SAI PETROLEUM,MUMBAI": "Maharashtra",
    "Ganpati Petro DC Charging Station Hisar": "Haryana",
    "Ganpati Petro AC Charging Station Hisar": "Haryana",
    "HPCL - Badarpur Service Station, Gazipur": "Delhi",
}

# Canonical city -> state reference used to enforce consistency.
CITY_STATE = {
    # Karnataka
    "Bengaluru": "Karnataka", "Mysuru": "Karnataka", "Mangalore": "Karnataka", "Hubli": "Karnataka",
    "Belgaum": "Karnataka", "Belagavi": "Karnataka", "Manipal": "Karnataka", "Malavalli": "Karnataka",
    "Mudbidri": "Karnataka", "Brahmavara": "Karnataka",
    # Tamil Nadu
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Tiruchirappalli": "Tamil Nadu", "Tiruppur": "Tamil Nadu",
    "Madurai": "Tamil Nadu", "Salem": "Tamil Nadu", "Vellore": "Tamil Nadu", "Tindivanam": "Tamil Nadu",
    "Avinashi": "Tamil Nadu", "Vandalur": "Tamil Nadu", "Shoolagiri": "Tamil Nadu", "Pallikonda": "Tamil Nadu",
    "Villupuram": "Tamil Nadu", "Karur": "Tamil Nadu", "Kanchipuram": "Tamil Nadu", "Hosur": "Tamil Nadu",
    "Walayar": "Tamil Nadu",
    # Telangana
    "Hyderabad": "Telangana", "Secunderabad": "Telangana", "Warangal": "Telangana",
    # Gujarat
    "Ahmedabad": "Gujarat", "Rajkot": "Gujarat", "Surat": "Gujarat", "Gandhinagar": "Gujarat", "Limbdi": "Gujarat",
    "Navsari": "Gujarat", "Changodar": "Gujarat", "Chikhli": "Gujarat", "Shela": "Gujarat",
    # Maharashtra
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nashik": "Maharashtra", "Nagpur": "Maharashtra", "Thane": "Maharashtra",
    "Navi Mumbai": "Maharashtra", "Panvel": "Maharashtra", "Vasai-Virar": "Maharashtra", "Lonavala": "Maharashtra",
    "Beed": "Maharashtra", "Latur": "Maharashtra", "Sangli": "Maharashtra", "Mahad": "Maharashtra", "Dahanu": "Maharashtra",
    "Bhadalwadi": "Maharashtra", "Pimpri-Chinchwad": "Maharashtra", "Indapur": "Maharashtra", "Khopoli": "Maharashtra",
    "Kolhapur": "Maharashtra", "Alibag": "Maharashtra", "Panchgaon": "Haryana",
    # Delhi / Haryana / Rajasthan / UP
    "Delhi": "Delhi", "New Delhi": "Delhi", "Gurugram": "Haryana", "Karnal": "Haryana", "Hisar": "Haryana",
    "Kurukshetra": "Haryana", "Shahabad": "Haryana", "Faridabad": "Haryana", "Rewari": "Haryana",
    "Jaipur": "Rajasthan", "Behror": "Rajasthan", "Beawar": "Rajasthan", "Udaipur": "Rajasthan", "Shahpura": "Rajasthan", "Achrol": "Rajasthan",
    "Noida": "Uttar Pradesh", "Greater Noida": "Uttar Pradesh", "Ghaziabad": "Uttar Pradesh", "Lucknow": "Uttar Pradesh",
    "Muzaffarnagar": "Uttar Pradesh", "Gajraula": "Uttar Pradesh", "Kosi Kalan": "Uttar Pradesh", "Khatauli": "Uttar Pradesh",
    "Mathura": "Uttar Pradesh", "Agra": "Uttar Pradesh",
    # Kerala
    "Kochi": "Kerala", "Ernakulam": "Kerala", "Thiruvananthapuram": "Kerala", "Kollam": "Kerala", "Kozhikode": "Kerala",
    "Kannur": "Kerala", "Thrissur": "Kerala", "Guruvayur": "Kerala", "Aluva": "Kerala", "Malappuram": "Kerala",
    "Palakkad": "Kerala", "Nemom": "Kerala", "Alappuzha": "Kerala", "Kasaragod": "Kerala", "Koratty": "Kerala",
    # AP / Bihar / Assam / Odisha / WB / Punjab / MP / Goa
    "Visakhapatnam": "Andhra Pradesh", "Tirupati": "Andhra Pradesh", "Anantapur": "Andhra Pradesh",
    "Gaya": "Bihar", "Patna": "Bihar", "Nagaon": "Assam", "Guwahati": "Assam", "Bhubaneswar": "Odisha", "Jajpur": "Odisha",
    "Cuttack": "Odisha", "Kolkata": "West Bengal", "Bayamari": "West Bengal", "Chandigarh": "Chandigarh", "Indore": "Madhya Pradesh",
    "Ludhiana": "Punjab", "Goa": "Goa", "Margao": "Goa", "Panaji": "Goa", "Porvorim": "Goa", "Vagator": "Goa",
}

STATE_NAMES = sorted(set(CITY_STATE.values()) | set(STATE_MAP.values()) | {
    "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Odisha", "Puducherry",
    "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Chandigarh",
    "Andaman and Nicobar Islands"
}, key=len, reverse=True)
STATE_PATTERNS = [(s, re.compile(r"(?i)(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])")) for s in STATE_NAMES]


def clean_text(value: str | None) -> str:
    value = (value or "").replace("\xa0", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def canon_state(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    key = value.casefold()
    return STATE_MAP.get(key, " ".join(w.capitalize() for w in key.split()))


def canon_city(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    key = value.casefold()
    return CITY_MAP.get(key, " ".join(w.capitalize() for w in key.split()))


def address_state(address: str) -> str:
    """Find a likely terminal state mention without mistaking e.g. Punjab National Bank for Punjab."""
    address = clean_text(address)
    if not address:
        return ""
    hits: list[tuple[int, str]] = []
    for state, pattern in STATE_PATTERNS:
        for match in pattern.finditer(address):
            tail = address[match.end(): match.end() + 14]
            if re.search(r"\b\d{6}\b", tail) or match.end() >= len(address) - 45:
                if state == "Punjab" and re.search(r"Punjab\s+National\s+Bank", address[match.start():match.start() + 40], re.I):
                    continue
                hits.append((match.start(), state))
    return sorted(hits)[-1][1] if hits else ""


def normalize_coordinates(value: str):
    value = clean_text(value).rstrip(",")
    if not value:
        return None
    try:
        return round(float(value), 6)
    except ValueError:
        return None


def correction_reason(old_state: str, old_city: str, new_state: str, new_city: str, station: str, address: str) -> str:
    if old_city != new_city and station in STATION_CITY_OVERRIDES:
        return "High-confidence station/address locality correction"
    if old_state != new_state and station in STATION_STATE_OVERRIDES:
        return "Station-specific state correction"
    if old_city != new_city and new_city in CITY_STATE:
        return "Canonical city normalization / locality correction"
    if old_state != new_state and new_city in CITY_STATE:
        return "Canonical city-to-state consistency correction"
    ast = address_state(address)
    if old_state != new_state and ast == new_state:
        return "Terminal state evidence in address"
    return "Normalization"


def load_raw() -> list[dict[str, str]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean_records(raw_rows: list[dict[str, str]]):
    cleaned: list[dict] = []
    audit: list[dict] = []

    for raw in raw_rows:
        name = clean_text(raw.get("name"))
        old_state = canon_state(raw.get("state"))
        old_city = canon_city(raw.get("city"))
        address = clean_text(raw.get("address"))
        latitude = normalize_coordinates(raw.get("lattitude"))
        longitude = normalize_coordinates(raw.get("longitude"))

        if name in COORDINATE_FIXES:
            latitude, longitude = COORDINATE_FIXES[name]
        elif name in COORDINATE_FILLS and (latitude is None or longitude is None):
            latitude, longitude = COORDINATE_FILLS[name]

        if not address and name in ADDRESS_FILLS:
            address = ADDRESS_FILLS[name]

        # City correction first, so state can follow the corrected city.
        city = STATION_CITY_OVERRIDES.get(name, old_city)
        city = canon_city(city)

        # Terminal address evidence is strong, then station-specific overrides,
        # then canonical city -> state mapping, then the source state.
        state = address_state(address) or old_state
        if name in STATION_STATE_OVERRIDES:
            state = STATION_STATE_OVERRIDES[name]
        if city in CITY_STATE:
            state = CITY_STATE[city]

        # Special Tata Power rows: same station name appears across multiple places.
        if name == "Tata Power":
            if "Pune-Solapur Highway" in address or "Hotel Swamiraj" in address:
                city, state = "Indapur", "Maharashtra"
            elif "Hirapur Chaukadi" in address or "Hirapur" in address:
                city, state = "Ahmedabad", "Gujarat"

        # A few known locality corrections need a specific state after city correction.
        if city in CITY_STATE:
            state = CITY_STATE[city]

        row = {
            "name": name,
            "state": state,
            "city": city,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
        }

        if old_state != state or old_city != city:
            audit.append({
                "name": name,
                "old_state": old_state,
                "old_city": old_city,
                "new_state": state,
                "new_city": city,
                "reason": correction_reason(old_state, old_city, state, city, name, address),
                "address": address,
            })

        cleaned.append(row)

    return cleaned, audit


def deduplicate(rows: list[dict]) -> tuple[list[dict], int]:
    out = []
    seen = set()
    removed = 0
    for row in rows:
        if not row["address"] or row["latitude"] is None or row["longitude"] is None:
            removed += 1
            continue
        key = (
            clean_text(row["name"]).casefold(),
            clean_text(row["state"]).casefold(),
            clean_text(row["city"]).casefold(),
            clean_text(row["address"]).casefold(),
            round(float(row["latitude"]), 6),
            round(float(row["longitude"]), 6),
        )
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        row["latitude"] = round(float(row["latitude"]), 6)
        row["longitude"] = round(float(row["longitude"]), 6)
        out.append(row)
    return out, removed


def validate(rows: list[dict]) -> None:
    assert rows, "No rows remain after cleaning"
    assert all(all(row[k] not in (None, "") for k in ["name", "state", "city", "address"]) for row in rows)
    assert all(6 <= float(row["latitude"]) <= 37.5 for row in rows)
    assert all(68 <= float(row["longitude"]) <= 97.5 for row in rows)

    city_states = defaultdict(set)
    for row in rows:
        city_states[row["city"]].add(row["state"])

    multi_state = {city: sorted(states) for city, states in city_states.items() if len(states) > 1}
    assert not multi_state, f"City-to-state inconsistency remains: {multi_state}"


def save_csv(rows: list[dict], path: Path) -> None:
    fields = ["name", "state", "city", "address", "latitude", "longitude"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_audit(audit_rows: list[dict], path: Path) -> None:
    fields = ["name", "old_state", "old_city", "new_state", "new_city", "reason", "address"]
    # Keep only the final value per station/address/state-city transformation.
    seen = set()
    final = []
    for r in audit_rows:
        key = tuple(r[f] for f in fields)
        if key not in seen:
            seen.add(key)
            final.append(r)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(final)


def main() -> None:
    raw = load_raw()
    cleaned, audit = clean_records(raw)
    final, removed = deduplicate(cleaned)
    validate(final)
    save_csv(final, OUTPUT)
    save_audit(audit, AUDIT)

    print(f"Input rows: {len(raw):,}")
    print(f"Final rows: {len(final):,}")
    print(f"Removed unresolved/duplicate rows: {removed:,}")
    print(f"State/city corrections logged: {len(audit):,}")
    print(f"States: {len(set(r['state'] for r in final))}")
    print(f"Cities: {len(set(r['city'] for r in final))}")
    print(f"Saved final CSV: {OUTPUT}")
    print(f"Saved correction audit: {AUDIT}")


if __name__ == "__main__":
    main()
