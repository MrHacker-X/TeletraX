#!/bin/bash
# By github.com/MrHacker-X
# TeletraX setup: auto-detects Termux / Linux and installs dependencies.
# No "sudo pip" — uses the system package manager, then pip with a
# PEP 668-safe fallback (venv or --user).

set -u

# ---------- colors (disabled when not a terminal or NO_COLOR is set) ----------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    RD=$'\e[31m'; GR=$'\e[32m'; YL=$'\e[33m'; CY=$'\e[36m'; BW=$'\e[1m'; XX=$'\e[0m'
else
    RD=""; GR=""; YL=""; CY=""; BW=""; XX=""
fi

info() { printf '%s[*]%s %s\n' "$CY" "$XX" "$1"; }
ok()   { printf '%s[+]%s %s\n' "$GR" "$XX" "$1"; }
warn() { printf '%s[!]%s %s\n' "$YL" "$XX" "$1"; }
err()  { printf '%s[x]%s %s\n' "$RD" "$XX" "$1" >&2; }
fail() { err "$1"; exit 1; }

# ---------- sudo helper (only used for system packages) ----------
SUDO=""
if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
fi

# ---------- system detection ----------
detect_system() {
    if [ -n "${TERMUX_VERSION:-}" ] || case "$HOME" in /data/data/com.termux*) true;; *) false;; esac; then
        echo "termux"
        return
    fi
    case "$(uname -s)" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "darwin" ;;
        *)       echo "unknown" ;;
    esac
}

SYSTEM="$(detect_system)"
echo
case "$SYSTEM" in
    termux) ok "Termux detected." ;;
    linux)  ok "Linux detected." ;;
    *)
        err "TeletraX is not available for this system."
        warn "Supported systems: Termux and Linux only."
        echo
        exit 1
        ;;
esac
echo

# ---------- python3 ----------
PY=""
if command -v python3 >/dev/null 2>&1; then
    PY="python3"
else
    info "Installing python3..."
    if [ "$SYSTEM" = "termux" ]; then
        pkg install -y python || fail "python install failed."
    elif command -v apt-get >/dev/null 2>&1; then
        $SUDO apt-get update -y || true
        $SUDO apt-get install -y python3 python3-pip || fail "python3 install failed."
    elif command -v dnf >/dev/null 2>&1; then
        $SUDO dnf install -y python3 python3-pip || fail "python3 install failed."
    elif command -v yum >/dev/null 2>&1; then
        $SUDO yum install -y python3 python3-pip || fail "python3 install failed."
    elif command -v pacman >/dev/null 2>&1; then
        $SUDO pacman -S --noconfirm python python-pip || fail "python install failed."
    elif command -v zypper >/dev/null 2>&1; then
        $SUDO zypper --non-interactive install python3 python3-pip || fail "python3 install failed."
    else
        err "No supported package manager found (apt/dnf/yum/pacman/zypper)."
        warn "Install python3 manually, then re-run this script."
        exit 1
    fi
    command -v python3 >/dev/null 2>&1 || fail "python3 still missing."
    PY="python3"
fi
ok "Using $($PY --version 2>&1)"

# ---------- pip ----------
ensure_pip() {
    command -v pip3 >/dev/null 2>&1 && return 0
    "$PY" -m pip --version >/dev/null 2>&1 && return 0

    info "Installing pip..."
    if [ "$SYSTEM" = "termux" ]; then
        pkg install -y python-pip || return 1
    elif command -v apt-get >/dev/null 2>&1; then
        $SUDO apt-get install -y python3-pip || return 1
    elif command -v dnf >/dev/null 2>&1; then
        $SUDO dnf install -y python3-pip || return 1
    elif command -v pacman >/dev/null 2>&1; then
        $SUDO pacman -S --noconfirm python-pip || return 1
    elif command -v zypper >/dev/null 2>&1; then
        $SUDO zypper --non-interactive install python3-pip || return 1
    fi
    command -v pip3 >/dev/null 2>&1 || "$PY" -m pip --version >/dev/null 2>&1
}

# ---------- dependencies ----------
DEPS=(requests phonenumbers)

install_deps() {
    ensure_pip || fail "pip is not available."
    info "Installing Python dependencies..."
    if "$PY" -m pip install --break-system-packages "${DEPS[@]}" >/dev/null 2>&1; then
        return 0
    elif "$PY" -m pip install "${DEPS[@]}" >/dev/null 2>&1; then
        return 0
    elif "$PY" -m pip install --user "${DEPS[@]}" >/dev/null 2>&1; then
        # ~/.local/bin may not be on PATH yet; harmless if already present
        case ":$PATH:" in
            *":$HOME/.local/bin:"*) ;;
            *) export PATH="$HOME/.local/bin:$PATH" ;;
        esac
        return 0
    fi
    return 1
}

if install_deps; then
    ok "Dependencies installed."
else
    warn "Direct pip install failed (externally managed environment)."
    info "Setting up an isolated venv at .venv ..."
    "$PY" -m venv .venv || fail "Failed to create venv (install python3-venv)."
    # shellcheck disable=SC1091
    . .venv/bin/activate
    pip install "${DEPS[@]}" >/dev/null 2>&1 || fail "Dependency install inside venv failed."
    ok "Dependencies installed inside .venv (activate with: source .venv/bin/activate)"
fi

# ---------- verify ----------
"$PY" -c "import requests, phonenumbers" 2>/dev/null \
    || fail "Verification failed — dependencies are not importable."

# ---------- optional one-time API key setup (interactive runs only) ----------
if [ -t 0 ] && [ "$SYSTEM" != "skip" ]; then
    KEY_FILE="$HOME/.teletrax/apikey"
    if [ ! -s "$KEY_FILE" ]; then
        echo
        info "TeletraX works fully offline for Local Scan and Google Dorks."
        info "The optional Phone.spitier scan needs YOUR OWN free API key."
        printf '%s[?]%s %s[y/N]%s ' "$YL" "$XX" "Set it up now? " "$XX"
        read -r answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            echo
            info "Steps to get your free key:"
            echo "  1 · Open ${BW}https://phone.apitier.com${XX}"
            echo "  2 · Sign Up and create a free account"
            echo "  3 · Confirm your email, then log in"
            echo "  4 · Open the Dashboard / API Keys page"
            echo "  5 · Copy your personal API key"
            echo
            printf '%s[?]%s Paste your API key %s›%s ' "$CY" "$XX" "$CY" "$XX"
            read -r user_key
            if [ -n "$user_key" ]; then
                mkdir -p "$HOME/.teletrax"
                printf '%s\n' "$user_key" > "$KEY_FILE"
                chmod 600 "$KEY_FILE"
                ok "API key saved privately to ~/.teletrax/apikey"
            else
                warn "No key entered — skip. You can add it anytime."
                info "Later: re-run bash setup.sh, or export TELETRAX_API_KEY=your_key"
            fi
        else
            info "Skipped. Local Scan and Google Dorks work without a key."
        fi
    fi
fi

echo
echo "${RD}<========================================>${XX}"
echo "${GR}  TeletraX is ready${XX}"
echo "${BW}  Run:  python3 teletrax.py${XX}"
echo "${RD}<========================================>${XX}"
echo "          Created by: MrHacker-X"
echo "${RD}<========================================>${XX}"
echo

# ---------- optional auto-run ----------
if [ "${1:-}" = "--run" ]; then
    if [ -d ".venv" ] && [ -z "${VIRTUAL_ENV:-}" ]; then
        # shellcheck disable=SC1091
        . .venv/bin/activate
        exec python teletrax.py
    else
        exec "$PY" teletrax.py
    fi
fi
