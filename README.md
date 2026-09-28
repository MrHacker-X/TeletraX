<div align="center">

# ⃤ &nbsp;T E L E T R A X&nbsp; ⃤

### *📞 One number. Every answer. Right in your terminal.*

<br>

<img src="https://img.shields.io/github/stars/MrHacker-X/TeletraX?style=for-the-badge&color=orange">
<img src="https://img.shields.io/github/forks/MrHacker-X/TeletraX?style=for-the-badge&color=purple">
<img src="https://img.shields.io/github/issues/MrHacker-X/TeletraX?style=for-the-badge&color=red">
<img src="https://img.shields.io/github/license/MrHacker-X/TeletraX?style=for-the-badge&color=blue">

<br>

![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-2ea44f?style=flat-square&logo=linux&logoColor=white)
![Runtime](https://img.shields.io/badge/Runtime-python%203-3776AB?style=flat-square&logo=python&logoColor=white)
![Engine](https://img.shields.io/badge/Engine-phonenumbers-8A2BE2?style=flat-square)
![OSINT](https://img.shields.io/badge/OSINT-Google%20Dorks-red?style=flat-square)

[Features](#-features) · [Install](#-installation) · [Usage](#-usage) · [Scan Types](#-scan-types) · [Tech Stack](#-tech-stack)

</div>

---

## 🎯 Why TeletraX?

> Enter a phone number. Get **everything** — validity, country, carrier, region,
> continent, timezone, **live local time at the target** — plus direct OSINT
> lookups and 42 Google dorks to dig deeper. All from a champagne-gold terminal
> dashboard.
>
> **No API signup. No accounts. No tracking.** Just `python3` and curiosity.

## 🖼 Preview

<div align="center">

![Main Menu](https://i.ibb.co/1G1kKnMS/Screenshot-From-2026-09-29-00-08-19.png)

![Scan Previw](https://i.ibb.co/kgKPRMTZ/Screenshot-From-2026-09-29-00-08-39.png)

</div>

---

## 🚀 Quick Start

```bash
git clone https://github.com/MrHacker-X/TeletraX.git
cd TeletraX
bash setup.sh            # auto-detects Termux or Linux — zero questions
python3 teletrax.py      # menu opens 🎉
```

<div align="center">

**…that's the whole tutorial.**

</div>

---

## 📦 Installation

The setup script **auto-detects your system**. No prompts, no config files.

| Your System | Status | Package Manager |
|---|:---:|---|
| 🤖 **Termux** (Android) | ✅ Supported | `pkg` |
| 🐧 **Linux** (Debian / Arch / Fedora / openSUSE) | ✅ Supported | `apt` `dnf` `yum` `pacman` `zypper` |
| 🍎 macOS / 🪟 Windows / BSD | ❌ Refused | — setup exits with a clear message |

<details>
<summary><b>🔍 What the setup actually does</b></summary>

- Detects Termux vs Linux automatically
- Installs **python3 + pip** if missing (via your system's package manager)
- Installs `requests` and `phonenumbers` — **never with `sudo pip`**
- On PEP 668 "externally managed" distros it falls back to `--user`
  and then to an isolated `.venv` automatically
- Verifies everything is importable before declaring success
- Offers a **one-time guided API key setup** for the Phone.spitier scan
  (skip it — Local Scan and Google Dorks work without any key)

</details>

<details>
<summary><b>🔑 About the Phone.spitier API key</b></summary>

TeletraX ships with **no API key** — every user brings their own (it's free):

1. Run `bash setup.sh` and answer `y` when asked to set up the key, or just
   pick a Phone.spitier scan inside the tool — a step-by-step guide appears
2. Sign up at [phone.apitier.com](https://phone.apitier.com) and copy your
   personal key
3. Paste it once — it's stored in `~/.teletrax/apikey` (chmod 600), **outside
   the repo, never committed**

Prefer an environment variable? `export TELETRAX_API_KEY=your_key` — it takes
priority over the stored file.

</details>

<details>
<summary><b>⚡ Noninteractive install</b></summary>

```bash
bash setup.sh          # install only
bash setup.sh --run    # install, then launch TeletraX immediately
```

</details>

---

## 🎮 Usage

```bash
python3 teletrax.py
```

**A real session:**

```txt
┌─ MAIN MENU ──────────────────────────────────┐
│  1  Local Scan          offline intel
│  2  Phone.spitier Scan  extended API
│  3  Google Dork         OSINT search
│  4  Scan All            the full report
│  5  About
│  0  Exit
└───────────────────────────────────────────────┘
TeletraX › 1

[?] Enter phone number  e.g. +91 98765 43210 › +91 98765 43210

  🇮🇳  +91 98765 43210   ✓ VALID

╭─ IDENTITY ────────────────────────────────────╮
│ Country ···························· 🇮🇳 India │
│ Region code ······························ IN │
│ Continent ······························ Asia │
│ Carrier ······························ Airtel │
│ Line type ···························· MOBILE │
╰───────────────────────────────────────────────╯
╭─ TIME & GEO ──────────────────────────────────╮
│ Timezone ······················ Asia/Calcutta │
│ Local time (now) ······ 2026-09-28 23:26:44   │
╰───────────────────────────────────────────────╯
╭─ FORMATS ─────────────────────────────────────╮
│ E164 ·························· +919876543210 │
│ tel: URI ··············· tel:+91-98765-43210  │
╰───────────────────────────────────────────────╯
```

- 🎯 Pick a scan type, then enter the number
- 📋 Smart input: paste the full international number (`+91 98765-43210`,
  `0091...`) and go — the country code is only asked separately when it's missing
- ⌨️ `Ctrl+C` exits cleanly from anywhere

---

## ✨ Features

| | Feature | What you get |
|:---:|---|---|
| ✅ | **Validation** | Valid + possible checks, digit count, national destination code |
| 🌍 | **Country & Region** | Country with 🏳 flag emoji, region code, continent, geo description |
| 📡 | **Carrier & Line Type** | Operator plus MOBILE / FIXED / VOIP / TOLL_FREE / ... classification |
| 🕐 | **Time & Geo** | All timezones for the number **and the current local time at the target** |
| 🔢 | **All Formats** | E164 · International · National dialing · `tel:` URI |
| 🕵️ | **Direct OSINT** | One-click WhatsApp check, Sync.me, Google / Bing / Yandex reverse lookups |
| 🔎 | **47 OSINT Links** | 42 Google dorks (social media, disposable SMS providers, reputation sites, people-search) + 5 direct lookups |
| 🧪 | **Scan All** | Run every scan in one shot |
| 🎨 | **Premium UI** | Champagne-gold / soft-violet palette, boxed card reports, dotted leaders |

---

## 🔍 Scan Types

| Scan | Source | Best for |
|---|---|---|
| **1 · Local Scan** | `phonenumbers` (offline libphonenumber data) | The full intelligence card: validity, flag, country, continent, carrier, line type, timezones, **live local time**, all dialing formats |
| **2 · Phone.spitier Scan** | apitier.com API | Extended carrier/line-type intelligence |
| **3 · Google Dork** | Google | OSINT — find where the number appears across the web |
| **4 · Scan All** | everything | The full report in one pass |

---

## 🧰 Tech Stack

| Layer | Tech |
|---|---|
| 🧠 Engine | [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) (Google libphonenumber port) |
| 🌐 Requests | [requests](https://github.com/psf/requests) |
| 🎨 UI | Premium champagne-gold / soft-violet ANSI palette, boxed card rendering |
| ⚙️ Setup | Pure bash, colored CLI output, venv-aware |

---

## 👤 Developer

| | |
|---|---|
| **Dev** | MrHacker-X |
| **GitHub** | [github.com/MrHacker-X](https://github.com/MrHacker-X) |
| **Email** | contact@vritrasec.com |
| **Website** | [vritrasec.com](https://vritrasec.com) |
| **Network** | [link.vritrasec.com](https://link.vritrasec.com) |

## ⚠️ Disclaimer

> TeletraX provides information based on available data sources and APIs. It
> may not always guarantee accurate results or include information for all
> phone numbers. The tool is provided **as-is**, and the developers hold no
> responsibility for its usage or any consequences that may arise from it.
> Use responsibly and only look up numbers you have a legitimate reason to
> investigate.

## 🤝 Contributing

Found a bug? Have a wild idea? Open an [issue](https://github.com/MrHacker-X/TeletraX/issues)
or fire off a pull request — contributions are always welcome.

## 📜 License

Released under the [MIT License](https://opensource.org/licenses/MIT).

---

<div align="center">

**⃤ TeletraX** — crafted with 📞🟠 by **[MrHacker-X](https://github.com/MrHacker-X)**

⭐ **Found it useful? Star the repo — it helps more than you know.** ⭐

</div>
