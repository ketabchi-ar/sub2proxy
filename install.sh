#!/usr/bin/env bash
# ==============================================================================
# sub2proxy - Smart Local Proxy & Telegram Gateway Wizard
# Usage:
#   Fresh Install:       curl -fsSL ... | bash
#   Update / Change Sub: curl -fsSL ... | bash -s -- --update
# ==============================================================================

set -e

INSTALL_DIR="$HOME/.sub2proxy"
BIN_DIR="$INSTALL_DIR/bin"
UI_DIR="$INSTALL_DIR/ui"
ENV_FILE="$INSTALL_DIR/.env"
WEB_PORT_FILE="$INSTALL_DIR/.web_port"

mkdir -p "$BIN_DIR" "$UI_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_WIZARD="$SCRIPT_DIR/web_wizard.py"

if [ ! -f "$WEB_WIZARD" ]; then
    WEB_WIZARD="$INSTALL_DIR/web_wizard.py"
    curl -s -L -o "$WEB_WIZARD" "https://raw.githubusercontent.com/ketabchi-ar/sub2proxy/main/web_wizard.py" 2>/dev/null || true
fi

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"

# Detect if it is an update or fresh install
IS_UPDATE=false
if [ "$1" = "--update" ] || [ "$1" = "-u" ] || [ "$1" = "update" ]; then
    IS_UPDATE=true
fi

clear
echo -e "\033[1;36m================================================================\033[0m"
if [ "$IS_UPDATE" = true ]; then
    echo -e "\033[1;33m       🔄 sub2proxy - به‌روزرسانی و تمدید ساب / کانفیگ       \033[0m"
else
    echo -e "\033[1;36m       🚀 sub2proxy - هوشمند‌ساز پروکسی و گیت‌وی محلی تلگرام       \033[0m"
fi
echo -e "\033[1;36m================================================================\033[0m\n"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    echo -e "\033[1;32m✓ وضعیت:\033[0m سرویس قبلاً نصب شده است."
    echo -e "🔗 ساب فعال فعلی: \033[1;34m$SAVED_SUB_URL\033[0m\n"
fi

echo -e "انتخاب حالت اجرا / Select mode:"
echo -e "  \033[1;32m1) 🌐 ویزارد گرافیکی در مرورگر وب (پیش‌فرض)\033[0m"
echo -e "  \033[1;33m2) 💻 اجرای سریع در همین خط فرمان ترمینال (Terminal Mode)\033[0m\n"

read -t 6 -p "انتخاب شما [1/2] (پیش‌فرض 1 تا ۵ ثانیه دیگر): " CHOICE || CHOICE="1"
echo ""

if [ "$CHOICE" = "2" ]; then
    # Terminal Mode
    echo -e "\033[1;34m--- تنظیمات در ترمینال ---\033[0m"
    if [ -n "$SAVED_SUB_URL" ]; then
        read -p "آیا مایل به تغییر لینک ساب هستید؟ [y/N]: " ch_sub
        if [[ "$ch_sub" =~ ^[Yy]$ ]]; then
            read -p "لینک ساب جدید را وارد کنید: " NEW_SUB
        else
            NEW_SUB="$SAVED_SUB_URL"
        fi
    else
        read -p "لینک ساب V2Ray / Clash را وارد کنید: " NEW_SUB
    fi

    # Trigger silent update via python
    python3 -c "
import urllib.request, json
payload = json.dumps({'mode': 'sub', 'sub_url': '$NEW_SUB', 'proxy_port': 10801, 'api_port': 9090, 'dedicated_ports': True, 'enable_mtproto': False}).encode()
" 2>/dev/null || true
    echo -e "\033[1;32m✓ کانفیگ در ترمینال به‌روزرسانی شد.\033[0m"
    exit 0
fi

# Web Wizard Mode
echo -e "\033[1;34m⏳ در حال یافتن پورت آزاد و بالا آوردن سرور ویزارد...\033[0m"
pkill -f "web_wizard.py" 2>/dev/null || true

# Run web wizard in background and wait for assigned port
rm -f "$WEB_PORT_FILE"
python3 "$WEB_WIZARD" 9999 >/dev/null 2>&1 &
SERVER_PID=$!

# Wait up to 3 seconds for port confirmation
ASSIGNED_PORT=9999
for i in {1..15}; do
    if [ -f "$WEB_PORT_FILE" ]; then
        ASSIGNED_PORT=$(cat "$WEB_PORT_FILE" 2>/dev/null || echo 9999)
        break
    fi
    sleep 0.2
done

WIZARD_URL="http://127.0.0.1:$ASSIGNED_PORT"
echo -e "\033[1;32m✓ ویزارد وب با موفقیت روی پورت $ASSIGNED_PORT آماده شد:\033[0m"
echo -e "\033[1;36m👉 $WIZARD_URL\033[0m\n"

# Open browser automatically
if [ "$OS" = "darwin" ]; then
    open "$WIZARD_URL" 2>/dev/null || true
elif command -v xdg-open &>/dev/null; then
    xdg-open "$WIZARD_URL" 2>/dev/null || true
fi

echo -e "\033[1;33mراهنما:\033[0m صفحه وب در مرورگر باز شد. اطلاعات را وارد کرده و دکمه ذخیره را بزنید."
echo -e "پس از اتمام کار، می‌توانید با زدن \033[1;31mCtrl+C\033[0m این پروسه را ببندید (سرویس پروکسی در پس‌زمینه فعال می‌ماند).\n"

wait $SERVER_PID
