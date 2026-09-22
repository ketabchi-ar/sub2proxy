<p align="center">
  <img src="assets/banner.svg" alt="sub2proxy Banner" width="100%">
</p>

<p align="center">
  <b>Smart Local Proxy & Telegram Gateway (V2Ray & WireGuard to SOCKS5/HTTP)</b><br>
  تبدیل آسان و هوشمند لینک‌های ساب V2Ray و کانفیگ‌های WireGuard به پروکسی محلی پایدار با تفکیک ترافیک
</p>

<p align="center">
  <a href="https://devsponsors.github.io"><img src="https://img.shields.io/badge/DevSponsors-Verified_OSS-6366f1?style=for-the-badge&logo=github" alt="DevSponsors"></a>
  <a href="https://devsponsors.github.io"><img src="https://img.shields.io/badge/Sponsor-DevSponsors_Hub-emerald?style=for-the-badge&logo=github-sponsors" alt="Sponsor"></a>
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20Ubuntu-blue?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## 🇮🇷 راهنمای فارسی

### 💡 پروژه sub2proxy چیست و چه دردی را دوا می‌کند؟
بسیاری از کاربران فنی، برنامه‌نویسان و تریدرها در ایران هنگام کار با فیلترشکن‌ها با مشکلات زیر دست‌وپنجه نرم می‌کنند:
1. **قفل شدن کل سیستم روی VPN:** اکثر کلاینت‌ها اینترنت کل ویندوز یا مک را وارد تونل VPN می‌کنند. در نتیجه سایت‌های بانکی، اداری، درگاه‌های پرداخت، پیام‌رسان‌های داخلی و سرورهای محلی کند، مختل یا تحریم می‌شوند.
2. **پرش مداوم آی‌پی (IP Hopping) و حساسیت تلگرام:** کلاینت‌هایی که فقط بر اساس پینگ لحظه‌ای کار می‌کنند، هر ۲ دقیقه سرور را عوض می‌کنند؛ در نتیجه تلگرام مکرراً سشن عوض می‌کند و ممکن است اکانت مشکوک شناخته یا لیمیت شود.
3. **دردسر کانفیگ دستی ابزارها:** کانفیگ کردن پورت‌های متعدد، تبدیل کانفیگ‌های وایرگارد، و اتصال تلگرام به پروکسی‌های پرسرعت زمان‌بر است.

**sub2proxy** تمام این کارها را در پس‌زمینه انجام می‌دهد: یک پورت پروکسی محلی مستقل و پایدار ایجاد می‌کند، سریع‌ترین سرور را انتخاب کرده و تا زمانی که نسوزد روی همان می‌ماند، و کل اینترنت سیستم شما را آزاد و دست‌نخورده باقی می‌گذارد.

---

### 🌟 توضیح امکانات و دلیل اضافه شدن هر گزینه (چرا گذاشتیم؟)

| امکان / گزینه | چرا این گزینه را گذاشتیم؟ (مزیت فنی) |
| :--- | :--- |
| **۱. استراتژی اتصال پایدار (Fallback Anti-Hopping)** | در حالت پیش‌فرض `url-test`، با جابه‌جایی ۱۰ میلی‌ثانیه‌ای پینگ، سرور عوض می‌شود. ما آن را روی **`fallback`** تنظیم کردیم تا آی‌پی شما ثابت بماند و فقط در صورت قطعی واقعی سوئیچ کند تا تلگرام و صرافی‌ها به تغییر مکرر کشور مشکوک نشوند. |
| **۲. عدم درگیر کردن کل سیستم (`tun: false`)** | کارت شبکه مجازی غیرفعال است؛ بنابراین سایت‌های شتاب، بانک‌ها، اسنپ، بورس و دانلودهای ایرانی مستقیم و با حداکثر سرعت کار می‌کنند و فقط تلگرام یا برنامه‌ای که شما بخواهید از پروکسی رد می‌شود. |
| **۳. پشتیبانی نیتیو از کانفیگ وایرگارد (WireGuard)** | وایرگارد به خودی خود VPN کل سیستم است. sub2proxy متن خام `.conf` را دریافت کرده و به یک پورت SOCKS5 تبدیل می‌کند؛ بدون نیاز به نصب کلاینت وایرگارد یا ایجاد کارت شبکه تونل. |
| **۴. پورت‌های اختصاصی ثابت به ازای هر سرور (Dedicated Ports)** | اگر برای کارهای خاص (مثلاً تست با سرور یک کشور مشخص مثل آلمان) بخواهید همیشه یک IP ثابت داشته باشید، علاوه بر پورت هوشمند اصلی، پورت‌های ثابتی مثل `10802`، `10803` و... برای هر تک‌سرور در اختیار شماست. |
| **۵. ویزارد تحت وب محلی (`http://127.0.0.1:9999`)** | برای اینکه کاربر درگیر خط فرمان و دستکاری فایل‌های YAML نشود، محیط گرافیکی کامل تحت وب با فونت استاندارد **وزیرمتن** طراحی شد. |
| **۶. سازگاری دوگانه مک و سرور لینوکس (LaunchAgent / Systemd)** | در مک به صورت سرویس `LaunchAgent` و در اوبونتو/دبیان به صورت `Systemd` پس‌زمینه نصب می‌شود؛ یعنی سیستم یا سرور ری‌استارت هم شود، پروکسی شما خودکار بالا می‌آید. |

---

### 📸 تصاویر محیط نرم‌افزار

<p align="center">
  <b>ویزارد گرافیکی تحت وب (Web Setup Wizard)</b><br>
  <img src="assets/web_wizard.png" alt="Web Wizard Screenshot" width="90%">
</p>

<p align="center">
  <b>پنل مانیتورینگ زنده سرورها (با فونت وزیرمتن)</b><br>
  <img src="assets/dashboard.png" alt="Dashboard Screenshot" width="90%">
</p>

---

### 🚀 نصب و اجرای سریع (۱ خط دستور)

کافیست در ترمینال macOS یا Ubuntu دستور زیر را اجرا کنید:

```bash
curl -fsSL https://raw.githubusercontent.com/ketabchi-ar/sub2proxy/main/install.sh | bash
```

یا اجرای دستی پس از کلون مخزن:
```bash
git clone https://github.com/ketabchi-ar/sub2proxy.git
cd sub2proxy
chmod +x install.sh
./install.sh
```

---

## 🇬🇧 English Documentation

### 💡 What is sub2proxy?
**sub2proxy** is a lightweight, zero-footprint local proxy gateway built on top of the ultra-fast Go-based Mihomo core. It turns remote V2Ray subscription links or WireGuard configurations into stable local SOCKS5/HTTP proxies (`127.0.0.1:10801`) without modifying the host network routing or intercepting domestic traffic.

### 🌟 Key Features & Architectural Rationale

1. **Anti-Hopping Fallback Routing:** Avoids frequent IP jumps that trigger security alerts or rate-limits in Telegram and financial apps. Stays connected to the primary healthy node and switches only upon actual disconnection.
2. **Zero System Interference:** Bypasses local system DNS and network interfaces. Domestic traffic, streaming, and banking stay direct and unaffected.
3. **Native WireGuard Inbound Support:** Converts raw WireGuard `[Interface]` configuration files into local SOCKS5 proxies without needing kernel tun devices.
4. **Per-Node Dedicated Multi-Inbound Ports:** In addition to the smart auto-fallback port (`10801`), dedicated static ports (`10802`, `10803`, ...) are assigned to each specific upstream server.
5. **Interactive Web Setup & Local Dashboard:** Features a clean browser-based configuration wizard (`http://127.0.0.1:9999`) and a built-in MetaCubeXD monitoring dashboard with Persian typography.
6. **Production-Ready Daemonization:** Runs out-of-the-box as a native `LaunchAgent` on macOS or a `systemd` service on Linux (Ubuntu/Debian).

### 📥 Quick Start
```bash
curl -fsSL https://raw.githubusercontent.com/ketabchi-ar/sub2proxy/main/install.sh | bash
```

---

## 📜 License
Released under the [MIT License](LICENSE).
