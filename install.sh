#!/usr/bin/env bash
# ==============================================================================
# sub2proxy - Smart Local Proxy & Telegram Gateway Wizard
# Dual UI: Automatic Web Wizard (with fallback/choice to Terminal Wizard)
# ==============================================================================

set -e

INSTALL_DIR="$HOME/.sub2proxy"
BIN_DIR="$INSTALL_DIR/bin"
UI_DIR="$INSTALL_DIR/ui"
mkdir -p "$BIN_DIR" "$UI_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_WIZARD="$SCRIPT_DIR/web_wizard.py"

# Download web_wizard.py if installed via curl pipe
if [ ! -f "$WEB_WIZARD" ]; then
    WEB_WIZARD="$INSTALL_DIR/web_wizard.py"
    curl -s -L -o "$WEB_WIZARD" "https://raw.githubusercontent.com/ketabchi-ar/sub2proxy/main/web_wizard.py" 2>/dev/null || true
fi

# Detect OS
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"

clear
echo -e "\033[1;36m================================================================\033[0m"
echo -e "\033[1;36m       🚀 sub2proxy - هوشمند‌ساز پروکسی و گیت‌وی محلی تلگرام       \033[0m"
echo -e "\033[1;36m================================================================\033[0m\n"

echo -e "چگونه مایل به ادامه تنظیمات هستید؟ / How would you like to proceed?"
echo -e "  \033[1;32m1) 🌐 ویزارد گرافیکی در مرورگر وب (پیش‌فرض / خودکار باز می‌شود)\033[0m"
echo -e "  \033[1;33m2) 💻 ادامه در همین محیط ترمینال (Text Terminal)\033[0m\n"

# Timeout 6 seconds, default to 1 (Web)
read -t 6 -p "انتخاب شما [1/2] (پیش‌فرض 1 تا ۵ ثانیه دیگر): " CHOICE || CHOICE="1"
echo ""

if [ "$CHOICE" = "2" ]; then
    # Run terminal wizard directly
    exec bash "$SCRIPT_DIR/install_terminal.sh"
else
    # Launch Web Wizard Server
    echo -e "\033[1;34m⏳ در حال بالا آوردن ویزارد تحت وب روی پورت 9999...\033[0m"
    pkill -f "web_wizard.py" 2>/dev/null || true
    python3 "$WEB_WIZARD" &
    SERVER_PID=$!
    sleep 1

    WIZARD_URL="http://127.0.0.1:9999"
    echo -e "\033[1;32m✓ ویزارد وب فعال شد:\033[0m \033[1;36m$WIZARD_URL\033[0m"

    # Open Browser automatically
    if [ "$OS" = "darwin" ]; then
        open "$WIZARD_URL" 2>/dev/null || true
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$WIZARD_URL" 2>/dev/null || true
    fi

    echo -e "\n\033[1;33mنکته:\033[0m اگر مرورگر باز نشد، آدرس بالا را دستی در مرورگر باز کنید."
    echo -e "همچنین اگر سرور بدون دسکتاپ (SSH) است، پورت 9999 را فوروارد کنید یا از گزینه ۲ (ترمینال) استفاده کنید."
    echo -e "\nبرای توقف سرور ویزارد در ترمینال Ctrl+C را بزنید."
    wait $SERVER_PID
fi
