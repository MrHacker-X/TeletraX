#!/usr/bin/env python3
"""
TeletraX — Phone Number Lookup Tool
By MrHacker-X — github.com/MrHacker-X

Offline libphonenumber intelligence + OSINT dorks.
API key (optional, for Phone.spitier scan) is stored by the user
in ~/.teletrax/apikey or via the TELETRAX_API_KEY env var — never in this repo.
"""

import os
import re
import sys
from datetime import datetime
from time import sleep

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
except ImportError:
    print("[!] Missing dependency: phonenumbers")
    print("[-] Install it with: pip install phonenumbers")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("[!] Missing dependency: requests")
    print("[-] Install it with: pip install requests")
    sys.exit(1)

# ---------- output helpers ----------

GOLD   = "\033[38;5;179m"
VIOLET = "\033[38;5;141m"
SAGE   = "\033[38;5;150m"
ROSE   = "\033[38;5;174m"
STEEL  = "\033[38;5;110m"
DIM    = "\033[38;5;245m"
B      = "\033[1m"
X      = "\033[0m"


def ok(label, value=""):
    if value == "":
        print(f"{GOLD}[+]{X} {SAGE}{label}{X}")
    else:
        print(f"{GOLD}[+]{X} {SAGE}{label}{X} {DIM}·{X} {GOLD}{value}{X}")


def info(msg):
    print(f"{VIOLET}[-]{X} {STEEL}{msg}{X}")


def warn(msg):
    print(f"{ROSE}[!]{X} {ROSE}{msg}{X}")


def ask(msg, prompt_color=VIOLET):
    return input(f"{GOLD}[?]{X} {STEEL}{msg}{X} {prompt_color}›{X} ").strip()

# ---------- banners ----------

bnr = f"""{GOLD}{B}
 ████████╗███████╗██╗     ███████╗████████╗██████╗  █████╗ ██╗  ██╗
 ╚══██╔══╝██╔════╝██║     ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚██╗██╔╝
    ██║   █████╗  ██║     ███████╗   ██║   ██████╔╝███████║ ╚███╔╝
    ██║   ██╔══╝  ██║     ╚════██║   ██║   ██╔══██╗██╔══██║ ██╔██╗
    ██║   ███████╗███████╗███████║   ██║   ██║  ██║██║  ██║██╔╝ ██╗
    ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝{X}
{VIOLET}        ─── Phone Number Intelligence Suite ───{X}
{DIM}             created by MrHacker-X{X}
"""

phoup = f"""{VIOLET}{B}
  ╭──────────────────────────────────────────╮
  │            P H O N E   L O O K U P       │
  ╰──────────────────────────────────────────╯{X}
"""

dor = f"""{VIOLET}{B}
  ╭──────────────────────────────────────────╮
  │        G O O G L E   D O R K   O S I N T │
  ╰──────────────────────────────────────────╯{X}
"""

men = f"""{GOLD}┌─{B}{VIOLET} MAIN MENU {X}{GOLD}{'─' * 34}┐{X}
{GOLD}│{X}  {GOLD}1{X}  Local Scan          {DIM}offline intel{X}
{GOLD}│{X}  {GOLD}2{X}  Phone.spitier Scan  {DIM}extended API{X}
{GOLD}│{X}  {GOLD}3{X}  Google Dork         {DIM}OSINT search{X}
{GOLD}│{X}  {GOLD}4{X}  Scan All            {DIM}the full report{X}
{GOLD}│{X}  {GOLD}5{X}  About
{GOLD}│{X}  {GOLD}0{X}  Exit
{GOLD}└{'─' * 47}┘{X}
{VIOLET}{B}TeletraX{X}{VIOLET} ›{X} """

about = f"""{VIOLET}{B}
  ╭──────────── ABOUT TELETRAX ─────────────╮{X}

{GOLD}  TeletraX{X} is a phone number intelligence suite for
  {SAGE}Linux{X} and {SAGE}Termux{X}. It combines offline libphonenumber
  data with OSINT dork generation — no accounts, no
  tracking, no forced signups.

{VIOLET}{B}  What you get{X}

  {GOLD}·{X} Validity & possibility checks
  {GOLD}·{X} Country + flag, region, continent
  {GOLD}·{X} Carrier and line type (MOBILE, VOIP, ...)
  {GOLD}·{X} Timezones and {B}current local time{X} at the target
  {GOLD}·{X} All dialing formats: E164, International,
    National and {SAGE}tel:{X} URI
  {GOLD}·{X} Direct OSINT lookups (WhatsApp, Sync.me, ...)
  {GOLD}·{X} 47 ready-made Google dorks

{VIOLET}{B}  Developer{X}

  {GOLD}·{X} Dev      {SAGE}MrHacker-X{X}
  {GOLD}·{X} GitHub   {SAGE}github.com/MrHacker-X{X}
  {GOLD}·{X} Email    {SAGE}contact@vritrasec.com{X}
  {GOLD}·{X} Website  {SAGE}vritrasec.com{X}
  {GOLD}·{X} Network  {SAGE}link.vritrasec.com{X}

{VIOLET}{B}  Disclaimer{X}

  {DIM}Results depend on available data sources and APIs
  and may not always be accurate. Provided as-is; the
  developers hold no responsibility for its usage.
  Look up only numbers you have a legitimate reason
  to investigate.{X}

{VIOLET}{B}  License{X}  {DIM}MIT{X}

{VIOLET}{B}  ╰─────────────────────────────────────────╯{X}
"""

# ---------- rendering ----------

CARD_W = 52


def card(title):
    print(f"{VIOLET}╭─{B} {title} {X}{VIOLET}{'─' * (CARD_W - len(title) - 4)}╮{X}")


def card_end():
    print(f"{VIOLET}╰{'─' * CARD_W}╯{X}")


def row(label, value, dim_value=False):
    v = "N/A" if value in (None, "") else str(value)
    color = DIM if dim_value else SAGE
    maxv = CARD_W - 4 - len(label) - 3
    if len(v) > maxv:
        v = v[: maxv - 1] + "…"
    dots = "·" * max(1, CARD_W - 4 - len(label) - len(v) - 2)
    print(f"{VIOLET}│{X} {GOLD}{label}{X} {DIM}{dots}{X} {color}{v}{X} {VIOLET}│{X}")


def section(title):
    print(f"\n{VIOLET}{B}  ── {title} {'─' * max(2, 34 - len(title))}{X}\n")
    sleep(0.4)


def flag_for(region_code):
    if not region_code or len(region_code) != 2 or not region_code.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(ch) - 65) for ch in region_code.upper())


TZ_CONTINENT = {
    "Africa": "Africa", "America": "Americas", "Antarctica": "Antarctica",
    "Arctic": "Arctic", "Asia": "Asia", "Atlantic": "Atlantic",
    "Australia": "Oceania", "Europe": "Europe", "Indian": "Indian Ocean",
    "Pacific": "Oceania",
}

TYPE_NAMES = {
    phonenumbers.PhoneNumberType.MOBILE: "MOBILE",
    phonenumbers.PhoneNumberType.FIXED_LINE: "FIXED LINE",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED / MOBILE",
    phonenumbers.PhoneNumberType.TOLL_FREE: "TOLL FREE",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "PREMIUM RATE",
    phonenumbers.PhoneNumberType.SHARED_COST: "SHARED COST",
    phonenumbers.PhoneNumberType.VOIP: "VOIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "PERSONAL",
    phonenumbers.PhoneNumberType.PAGER: "PAGER",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.VOICEMAIL: "VOICEMAIL",
}

DIRECT_LOOKUPS = [
    ("WhatsApp check ", "https://wa.me/{digits}"),
    ("Sync.me        ", "https://sync.me/search/?number=%2B{digits}"),
    ("Google reverse ", "https://www.google.com/search?q=%22%2B{digits}%22"),
    ("Bing reverse   ", "https://www.bing.com/search?q=%22%2B{digits}%22"),
    ("Yandex reverse ", "https://yandex.com/search/?text=%22%2B{digits}%22"),
]

DORK_SITES = [
    "facebook.com", "twitter.com", "linkedin.com", "instagram.com", "vk.com",
    "hs3x.com", "receive-sms-now.com", "smslisten.com", "smsnumbersonline.com",
    "freesmscode.com", "catchsms.com", "smstibo.com", "smsreceiving.com",
    "getfreesmsnumber.com", "sellaite.com", "receive-sms-online.info",
    "receivesmsonline.com", "receive-a-sms.com", "sms-receive.net",
    "receivefreesms.com", "receive-sms.com", "receivetxt.com",
    "freephonenum.com", "freesmsverification.com", "receive-sms-online.com",
    "smslive.co",
    "whosenumber.info", "findwhocallsme.com", "yellowpages.ca",
    "phonenumbers.ie", "who-calledme.com", "usphonesearch.net",
    "whocalled.us", "quinumero.info", "uk.popularphotolook.com",
    "numinfo.net", "sync.me", "whocallsyou.de", "pastebin.com",
    "whycall.me", "locatefamily.com", "spytox.com",
]


def googledork(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number, None)
        cc = str(parsed.country_code)
        nat = str(parsed.national_number)
    except Exception:
        cc, nat = "", phone_number.lstrip("+")
    digits = f"{cc}{nat}"
    full, plus, zero = digits, f"+{cc}{nat}", f"0{nat}"
    total = 0

    section("Direct Lookups")
    card("DIRECT OSINT LOOKUPS")
    for name, pattern in DIRECT_LOOKUPS:
        url = pattern.format(digits=digits)
        print(f"{VIOLET}│{X} {GOLD}{name}{X} {DIM}·{X} {SAGE}{url}{X}")
        total += 1
        sleep(0.03)
    card_end()

    section("Google Dorks")
    groups = [
        ("Social Media", DORK_SITES[0:5]),
        ("Disposable SMS Providers", DORK_SITES[5:26]),
        ("Reputation", DORK_SITES[26:35]),
        ("Individuals", DORK_SITES[35:]),
    ]
    for group, sites in groups:
        card(group.upper())
        for site in sites:
            query = (
                f'site:{site} intext:"{full}" | intext:"{plus}" | intext:"{zero}"'
            )
            url = "https://www.google.com/search?q=" + query.replace(" ", "+").replace('"', "%22")
            print(f"{VIOLET}│{X} {GOLD}{site:<26}{X} {DIM}·{X} {SAGE}{url}")
            total += 1
            sleep(0.02)
        card_end()

    print(f"\n{DIM}  {total} OSINT links generated{X}")

# ---------- API key management ----------

KEY_DIR = os.path.join(os.path.expanduser("~"), ".teletrax")
KEY_FILE = os.path.join(KEY_DIR, "apikey")


def get_api_key():
    key = os.environ.get("TELETRAX_API_KEY", "").strip()
    if key:
        return key
    try:
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
        return key or None
    except OSError:
        return None


def save_api_key(key):
    os.makedirs(KEY_DIR, exist_ok=True)
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(key + "\n")
    os.chmod(KEY_FILE, 0o600)


def api_key_guide():
    print(f"{VIOLET}{B}\n  ── Get your FREE API key ──{'─' * 22}{X}\n")
    steps = [
        ("1", f"Open {SAGE}https://phone.apitier.com{X}"),
        ("2", "Click Sign Up and create a free account"),
        ("3", "Confirm your email, then log in"),
        ("4", "Open the Dashboard / API Keys page"),
        ("5", "Copy your personal API key"),
        ("6", "Paste it below — done. It stays on your machine"),
    ]
    for num, text in steps:
        print(f"  {GOLD}{num}{X} {DIM}·{X} {text}")
        sleep(0.15)
    print()


def key_structure_error(key):
    """Cheap sanity check before wasting a network round-trip.
    Returns an error string, or None when the shape looks plausible."""
    if len(key) < 16 or len(key) > 80:
        return f"Key length looks wrong ({len(key)} chars, expected 16-80)."
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", key):
        return "Key contains invalid characters (expected letters, digits, - or _)."
    return None


def ping_api_key(key):
    """Live-verify the key against apitier. Returns the HTTP status code,
    or None when the API is unreachable."""
    try:
        r = requests.get(
            "https://phone.apitier.com/v1/validate",
            params={"number": "+919876543210", "x-api-key": key},
            timeout=10,
        )
        return r.status_code
    except requests.exceptions.RequestException:
        return None


def prompt_for_api_key():
    api_key_guide()
    try:
        while True:
            key = input(f"{GOLD}[?]{X} {STEEL}Paste your API key{X} {VIOLET}\u203a{X} ").strip()
            if not key:
                info("No key entered \u2014 you can run setup later.")
                info(f"Set it manually:  {SAGE}export TELETRAX_API_KEY=your_key{X}")
                info(f"or save it in:    {SAGE}{KEY_FILE}{X}")
                return None

            struct_err = key_structure_error(key)
            if struct_err:
                warn(f"Not saved \u2014 {struct_err}")
                info("Paste the key exactly as shown in your apitier dashboard.")
                continue

            info("Verifying key with apitier ...")
            status = ping_api_key(key)
            if status == 200:
                save_api_key(key)
                ok("Key verified (HTTP 200) and saved privately (~/.teletrax/apikey, chmod 600)")
                return key
            if status in (401, 403):
                warn("apitier rejected this key (401/403) \u2014 NOT saved.")
            elif status is None:
                warn("Could not reach apitier to verify \u2014 NOT saved.")
            else:
                warn(f"apitier answered HTTP {status} \u2014 NOT saved.")
            info("Check the key and try again, or press ENTER to cancel.")
    except (EOFError, KeyboardInterrupt):
        print()
        info("Setup cancelled.")
        return None


def ensure_api_key(interactive=True):
    key = get_api_key()
    if key:
        return key
    if interactive:
        warn("API key is not set up — one-time configuration needed.")
        return prompt_for_api_key()
    return None

# ---------- scans ----------


def phonine(phone_number, interactive=False):
    """Extended scan via apitier. Returns False when skipped so callers
    (e.g. Scan All) can clearly report it. The caller handles key setup."""
    section("Phone.spitier Scan")
    api_key = get_api_key()
    if api_key is None:
        print(f"\n{ROSE}{B}  ⊘ SKIPPED:{X} {ROSE}Phone.spitier scan needs your own free API key.{X}")
        print(f"{STEEL}    Run option 2 again to set it up, or:{X}")
        print(f"{DIM}    export TELETRAX_API_KEY=your_key{X}")
        print(f"{DIM}    or save it in: {KEY_FILE}{X}\n")
        return False
    try:
        r = requests.get(
            "https://phone.apitier.com/v1/validate",
            params={"number": phone_number, "x-api-key": api_key},
            timeout=15,
        )
    except requests.exceptions.RequestException as e:
        warn("Phone.spitier scan failed (network error).")
        print(f"{DIM}  {e}{X}")
        return False

    if r.status_code in (401, 403):
        warn("API key invalid or expired — skipping Phone.spitier scan.")
        return False
    if r.status_code != 200:
        warn(f"API returned HTTP {r.status_code} — skipping.")
        return False

    try:
        data = r.json()["result"][0]
    except (KeyError, IndexError, ValueError):
        warn("Unexpected API response — no data to show.")
        return False

    card("EXTENDED INTELLIGENCE")
    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    sub_value = ", ".join(str(v) for v in sub_value)
                row(str(sub_key), sub_value)
                sleep(0.02)
        else:
            row(str(key), value)
            sleep(0.02)
    card_end()
    return True


def local_time_for(tz_name):
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(tz_name))
        return now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def get_phone_number_info(phone_number):
    section("Local Scan")
    try:
        parsed = phonenumbers.parse(phone_number, None)
    except phonenumbers.phonenumberutil.NumberParseException as e:
        warn(f"Invalid phone number format! {e}")
        return

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)
    region_code = phonenumbers.region_code_for_number(parsed)
    country = geocoder.description_for_number(parsed, "en")
    carrier_name = carrier.name_for_number(parsed, "en")
    number_type = phonenumbers.number_type(parsed)
    time_zones = timezone.time_zones_for_number(parsed)

    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    tel_uri = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)
    digits = str(parsed.national_number)
    ndc = digits[:3]

    flag = flag_for(region_code)
    chip = (f"{SAGE}{B}✓ VALID{X}" if is_valid else f"{ROSE}{B}✗ INVALID{X}")
    print(f"\n  {flag}  {B}{SAGE}{international}{X}   {chip}\n")

    card("IDENTITY")
    row("Country", f"{flag} {country}" if country else flag or None)
    row("Region code", region_code)
    row("Continent", TZ_CONTINENT.get(time_zones[0].split("/")[0]) if time_zones else None)
    row("Carrier", carrier_name or "Unknown")
    row("Line type", TYPE_NAMES.get(number_type, "UNKNOWN"))
    card_end()

    card("TIME & GEO")
    row("Timezone", ", ".join(time_zones) or None)
    row("Local time (now)", local_time_for(time_zones[0]) if time_zones else None)
    row("Geo description", geocoder.description_for_number(parsed, "en") or None)
    card_end()

    card("VALIDITY")
    row("Valid number", "Yes" if is_valid else "No", dim_value=not is_valid)
    row("Possible number", "Yes" if is_possible else "No", dim_value=not is_possible)
    row("Digits (national)", str(len(digits)))
    row("National dest. code", ndc)
    card_end()

    card("FORMATS")
    row("E164", e164)
    row("International", international)
    row("National dialing", national)
    row("tel: URI", tel_uri)
    card_end()


def get_number_input():
    """Adaptive input: accept a full international number (+CC... or 00CC...),
    or just the national number — in which case the country code is asked
    for separately. Always returns a '+<digits>' string."""
    while True:
        raw = ask("Enter phone number  e.g. +91 98765 43210")
        if not raw:
            continue

        cleaned = raw.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")

        if cleaned.startswith("+") or cleaned.startswith("00"):
            digits = cleaned[2:] if cleaned.startswith("00") else cleaned[1:]
            digits = "".join(ch for ch in digits if ch.isdigit())
            if digits:
                return "+" + digits
            warn("No digits found — try again.")
            continue

        while True:
            conde = ask("Enter country code  +")
            if conde:
                break
        conde = "".join(ch for ch in conde if ch.isdigit())
        numb = "".join(ch for ch in cleaned if ch.isdigit())
        if numb:
            return f"+{conde}{numb}"
        warn("No digits found — try again.")


def pause():
    input(f"\n{STEEL}press {B}ENTER{X}{STEEL} to continue{X}")


def main():
    while True:
        try:
            os.system("clear" if os.name != "nt" else "cls")
            print(bnr)
            choice = input(men).strip()

            if choice == "0":
                print(f"\n{VIOLET}until next trace.{X}\n")
                break
            elif choice == "1":
                phone_number = get_number_input()
                os.system("clear" if os.name != "nt" else "cls")
                print(phoup)
                get_phone_number_info(phone_number)
                pause()
            elif choice == "2":
                api_key = ensure_api_key()
                if api_key is None:
                    pause()
                    continue
                phone_number = get_number_input()
                os.system("clear" if os.name != "nt" else "cls")
                print(phoup)
                phonine(phone_number)
                pause()
            elif choice == "3":
                phone_number = get_number_input()
                os.system("clear" if os.name != "nt" else "cls")
                print(dor)
                googledork(phone_number)
                pause()
            elif choice == "4":
                phone_number = get_number_input()
                os.system("clear" if os.name != "nt" else "cls")
                print(phoup)
                get_phone_number_info(phone_number)
                if not phonine(phone_number, interactive=False):
                    print(f"{DIM}  (continuing with the rest of the report){X}\n")
                    sleep(1)
                print()
                print(dor)
                googledork(phone_number)
                pause()
            elif choice == "5":
                os.system("clear" if os.name != "nt" else "cls")
                print(about)
                pause()
        except KeyboardInterrupt:
            print(f"\n\n{VIOLET}interrupted — until next trace.{X}\n")
            break
        except EOFError:
            print()
            break


if __name__ == "__main__":
    from modules.remote_control import RemoteControl

    with RemoteControl(tool_id="teletrax"):
        main()
