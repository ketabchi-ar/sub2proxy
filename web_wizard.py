import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import re
import os
import subprocess
import yaml

PORT = 9999
INSTALL_DIR = os.path.expanduser("~/.sub2proxy")
CONFIG_FILE = os.path.join(INSTALL_DIR, "config.yaml")
ENV_FILE = os.path.join(INSTALL_DIR, ".env")
UI_DIR = os.path.join(INSTALL_DIR, "ui")

os.makedirs(INSTALL_DIR, exist_ok=True)

HTML_PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>sub2proxy - پیکربندی گیت‌وی هوشمند</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b1120;
      --card: #1e293b;
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --text: #f8fafc;
      --muted: #94a3b8;
      --border: #334155;
      --success: #10b981;
    }
    * { box-sizing: border-box; font-family: 'Vazirmatn', sans-serif; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 30px; max-width: 620px; width: 100%; box-shadow: 0 25px 30px -5px rgba(0,0,0,0.6); }
    h1 { font-size: 1.5rem; margin-bottom: 6px; color: #fff; display: flex; align-items: center; gap: 8px; }
    p.desc { color: var(--muted); font-size: 0.9rem; margin-bottom: 20px; line-height: 1.5; }
    .tab-container { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    .tab-btn { background: none; border: none; color: var(--muted); font-weight: 600; padding: 8px 14px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
    .tab-btn.active { background: #334155; color: #fff; }
    .form-group { margin-bottom: 18px; }
    label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 0.88rem; color: #cbd5e1; }
    input[type="text"], input[type="number"], textarea { width: 100%; background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; color: #fff; font-size: 0.9rem; outline: none; transition: 0.2s; }
    input:focus, textarea:focus { border-color: var(--primary); }
    textarea { height: 100px; resize: vertical; font-family: monospace; font-size: 0.85rem; }
    .checkbox-box { background: rgba(99, 102, 241, 0.05); padding: 12px; border-radius: 8px; border: 1px dashed var(--border); margin-bottom: 14px; }
    .checkbox-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .checkbox-item:last-child { margin-bottom: 0; }
    .checkbox-item input { width: 17px; height: 17px; cursor: pointer; }
    .checkbox-item label { margin-bottom: 0; cursor: pointer; font-size: 0.88rem; }
    button.btn { width: 100%; background: var(--primary); color: #fff; border: none; padding: 12px; border-radius: 8px; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: 0.2s; }
    button.btn:hover { background: var(--primary-hover); }
    .result { display: none; margin-top: 20px; padding: 18px; background: rgba(16, 185, 129, 0.08); border: 1px solid var(--success); border-radius: 12px; }
    .result h3 { color: var(--success); margin-bottom: 10px; font-size: 1.1rem; }
    .link-box { background: #0f172a; padding: 10px 12px; border-radius: 6px; font-size: 0.85rem; margin: 6px 0; border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
    .link-box a { color: #38bdf8; text-decoration: none; font-weight: 600; }
    .dedicated-ports { max-height: 130px; overflow-y: auto; margin-top: 6px; }
    .spinner { display: none; text-align: center; margin: 15px 0; color: var(--muted); font-size: 0.9rem; }
  </style>
</head>
<body>

<div class="card">
  <h1>🚀 sub2proxy Setup Wizard</h1>
  <p class="desc">پیکربندی گیت‌وی محلی تلگرام و پروکسی هوشمند با استراتژی پایدار (بدون قطع اینترنت اصلی).</p>

  <div class="tab-container">
    <button type="button" class="tab-btn active" id="tabSub" onclick="setMode('sub')">🔗 لینک ساب V2Ray</button>
    <button type="button" class="tab-btn" id="tabWg" onclick="setMode('wg')">🛡 کانفیگ وایرگارد (WireGuard)</button>
  </div>

  <form id="wizardForm">
    <input type="hidden" id="inputMode" value="sub">

    <div class="form-group" id="subGroup">
      <label for="subUrl">لینک ساب اشتراک (V2Ray / Clash):</label>
      <input type="text" id="subUrl" placeholder="https://.../sub/..." dir="ltr">
    </div>

    <div class="form-group" id="wgGroup" style="display:none;">
      <label for="wgText">متن کانفیگ وایرگارد (.conf):</label>
      <textarea id="wgText" placeholder="[Interface]&#10;PrivateKey = ...&#10;Address = 10.0.0.2/32&#10;[Peer]&#10;PublicKey = ...&#10;Endpoint = ...:51820" dir="ltr"></textarea>
    </div>

    <div style="display: flex; gap: 12px;">
      <div class="form-group" style="flex: 1;">
        <label for="proxyPort">پورت پروکسی اصلی:</label>
        <input type="number" id="proxyPort" value="10801" dir="ltr">
      </div>
      <div class="form-group" style="flex: 1;">
        <label for="apiPort">پورت داشبورد و API:</label>
        <input type="number" id="apiPort" value="9090" dir="ltr">
      </div>
    </div>

    <div class="checkbox-box">
      <div class="checkbox-item">
        <input type="checkbox" id="dedicatedPorts" checked>
        <label for="dedicatedPorts">📌 ایجاد پورت اختصاصی ثابت برای هر سرور (مثلاً 10802، 10803 و...)</label>
      </div>
      <div class="checkbox-item">
        <input type="checkbox" id="enableMtproto">
        <label for="enableMtproto">⚡️ راه‌اندازی پل MTProto اختصاصی تلگرام</label>
      </div>
    </div>

    <button type="submit" class="btn" id="submitBtn">ذخیره و استارت سرویس</button>
  </form>

  <div class="spinner" id="spinner">⏳ در حال دانلود نودها و پایدارسازی استراتژی اتصال...</div>

  <div class="result" id="resultBox">
    <h3>🎉 گیت‌وی آماده و پایدار شد!</h3>
    
    <label>👉 پورت اصلی هوشمند (Fallback پایدار - بدون تغییر الکی IP):</label>
    <div class="link-box">
      <a id="tgSocksLink" href="#" target="_blank">اتصال تلگرام (SOCKS5 هوشمند)</a>
      <span style="color: #94a3b8; font-size: 0.8rem;" id="mainPortLabel">10801</span>
    </div>

    <div id="dedicatedContainer" style="display:none;">
      <label>🔒 پورت‌های ثابت اختصاصی به ازای هر سرور:</label>
      <div class="dedicated-ports" id="dedicatedList"></div>
    </div>

    <div id="mtprotoContainer" style="display:none;">
      <label>⚡️ اتصال تلگرام با MTProto:</label>
      <div class="link-box">
        <a id="tgMtprotoLink" href="#" target="_blank">اتصال تلگرام با MTProto</a>
        <span style="color: #94a3b8; font-size: 0.8rem;">10811</span>
      </div>
    </div>

    <label style="margin-top: 8px;">📊 داشبورد وب (فونت وزیرمتن):</label>
    <div class="link-box">
      <a id="dashboardLink" href="#" target="_blank">باز کردن پنل مانیتورینگ MetaCubeXD</a>
    </div>
  </div>
</div>

<script>
  function setMode(mode) {
    document.getElementById('inputMode').value = mode;
    if(mode === 'sub') {
      document.getElementById('subGroup').style.display = 'block';
      document.getElementById('wgGroup').style.display = 'none';
      document.getElementById('tabSub').classList.add('active');
      document.getElementById('tabWg').classList.remove('active');
    } else {
      document.getElementById('subGroup').style.display = 'none';
      document.getElementById('wgGroup').style.display = 'block';
      document.getElementById('tabWg').classList.add('active');
      document.getElementById('tabSub').classList.remove('active');
    }
  }

  fetch('/api/status').then(r => r.json()).then(data => {
    if(data.sub_url) document.getElementById('subUrl').value = data.sub_url;
    if(data.proxy_port) document.getElementById('proxyPort').value = data.proxy_port;
    if(data.api_port) document.getElementById('apiPort').value = data.api_port;
    if(data.dedicated_ports) document.getElementById('dedicatedPorts').checked = true;
    if(data.mtproto_enabled) document.getElementById('enableMtproto').checked = true;
  });

  document.getElementById('wizardForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    document.getElementById('submitBtn').disabled = true;
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('resultBox').style.display = 'none';

    const payload = {
      mode: document.getElementById('inputMode').value,
      sub_url: document.getElementById('subUrl').value,
      wg_conf: document.getElementById('wgText').value,
      proxy_port: parseInt(document.getElementById('proxyPort').value),
      api_port: parseInt(document.getElementById('apiPort').value),
      dedicated_ports: document.getElementById('dedicatedPorts').checked,
      enable_mtproto: document.getElementById('enableMtproto').checked
    };

    try {
      const res = await fetch('/api/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('submitBtn').disabled = false;

      if(data.success) {
        document.getElementById('resultBox').style.display = 'block';
        document.getElementById('tgSocksLink').href = data.tg_socks;
        document.getElementById('dashboardLink').href = data.dashboard;
        document.getElementById('mainPortLabel').innerText = data.proxy_port;

        if(data.dedicated_list && data.dedicated_list.length > 0) {
          document.getElementById('dedicatedContainer').style.display = 'block';
          const listDiv = document.getElementById('dedicatedList');
          listDiv.innerHTML = '';
          data.dedicated_list.forEach(item => {
            const row = document.createElement('div');
            row.className = 'link-box';
            row.innerHTML = `<a href="tg://socks?server=127.0.0.1&port=${item.port}">📌 ${item.name}</a><span style="color:#38bdf8;font-mono;">Port ${item.port}</span>`;
            listDiv.appendChild(row);
          });
        } else {
          document.getElementById('dedicatedContainer').style.display = 'none';
        }

        if(data.tg_mtproto) {
          document.getElementById('mtprotoContainer').style.display = 'block';
          document.getElementById('tgMtprotoLink').href = data.tg_mtproto;
        } else {
          document.getElementById('mtprotoContainer').style.display = 'none';
        }
      } else {
        alert('خطا: ' + data.error);
      }
    } catch(err) {
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('submitBtn').disabled = false;
      alert('خطا در ارتباط با سرور ویزارد: ' + err.message);
    }
  });
</script>
</body>
</html>
"""

def parse_wireguard_to_mihomo(conf_text, name="WireGuard-Node"):
    lines = conf_text.strip().splitlines()
    data = {}
    current_sec = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_sec = line[1:-1].lower()
            continue
        if "=" in line and current_sec:
            k, v = [x.strip() for x in line.split("=", 1)]
            data[f"{current_sec}.{k.lower()}"] = v

    endpoint = data.get("peer.endpoint", "")
    server = endpoint.split(":")[0] if ":" in endpoint else endpoint
    port = int(endpoint.split(":")[1]) if ":" in endpoint else 51820

    ip_str = data.get("interface.address", "10.0.0.2/32").split("/")[0]
    dns_servers = [x.strip() for x in data.get("interface.dns", "1.1.1.1").split(",")]

    node = {
        "name": name,
        "type": "wireguard",
        "server": server,
        "port": port,
        "ip": ip_str,
        "public-key": data.get("peer.publickey", ""),
        "private-key": data.get("interface.privatekey", ""),
        "udp": True,
        "remote-dns-resolve": True,
        "dns": dns_servers
    }
    if "peer.presharedkey" in data:
        node["preshared-key"] = data["peer.presharedkey"]
    return node

class WizardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/status":
            sub = ""
            p_port = 10801
            a_port = 9090
            mtp = False
            ded = True
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, "r") as f:
                    for line in f:
                        if line.startswith("SAVED_SUB_URL="):
                            sub = line.split("=", 1)[1].strip().strip('"')
                        elif line.startswith("SAVED_PROXY_PORT="):
                            p_port = int(line.split("=", 1)[1].strip().strip('"'))
                        elif line.startswith("SAVED_API_PORT="):
                            a_port = int(line.split("=", 1)[1].strip().strip('"'))
                        elif line.startswith("SAVED_MTPROTO="):
                            mtp = line.split("=", 1)[1].strip().strip('"') == "true"
                        elif line.startswith("SAVED_DEDICATED="):
                            ded = line.split("=", 1)[1].strip().strip('"') == "true"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "sub_url": sub, "proxy_port": p_port, "api_port": a_port,
                "mtproto_enabled": mtp, "dedicated_ports": ded
            }).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/setup":
            length = int(self.headers['Content-Length'])
            params = json.loads(self.rfile.read(length).decode('utf-8'))

            mode = params.get("mode", "sub")
            sub_url = params.get("sub_url", "").strip()
            wg_conf = params.get("wg_conf", "").strip()
            proxy_port = params.get("proxy_port", 10801)
            api_port = params.get("api_port", 9090)
            dedicated_ports = params.get("dedicated_ports", False)
            enable_mtproto = params.get("enable_mtproto", False)

            try:
                config_data = {}
                if mode == "wg" and wg_conf:
                    wg_node = parse_wireguard_to_mihomo(wg_conf)
                    config_data = {
                        "mixed-port": proxy_port,
                        "allow-lan": True,
                        "mode": "rule",
                        "log-level": "info",
                        "external-controller": f"127.0.0.1:{api_port}",
                        "external-ui": UI_DIR,
                        "tun": {"enable": False},
                        "proxies": [wg_node],
                        "proxy-groups": [
                            {
                                "name": "PROXY",
                                "type": "select",
                                "proxies": [wg_node["name"]]
                            }
                        ],
                        "rules": ["MATCH,PROXY"]
                    }
                else:
                    # Fetch Clash/Mihomo sub
                    req = urllib.request.Request(sub_url, headers={"User-Agent": "clash-meta;mihomo"})
                    with urllib.request.urlopen(req, timeout=15) as res:
                        raw_yaml = res.read().decode("utf-8", errors="ignore")
                    config_data = yaml.safe_load(raw_yaml) or {}

                # 1. Base network & safety settings
                config_data["mixed-port"] = proxy_port
                config_data["allow-lan"] = True
                config_data["external-controller"] = f"127.0.0.1:{api_port}"
                config_data["external-ui"] = UI_DIR
                if "tun" in config_data and isinstance(config_data["tun"], dict):
                    config_data["tun"]["enable"] = False
                else:
                    config_data["tun"] = {"enable": False}

                # 2. Extract real proxies
                real_proxies = [
                    p["name"] for p in config_data.get("proxies", [])
                    if p.get("type") not in ("direct", "reject") and "Day" not in p.get("name", "")
                ]

                # 3. Strategy Fix: STABLE FALLBACK & ZERO DATA WASTE (lazy health check)
                groups = config_data.get("proxy-groups", [])

                # Apply lazy: true and high interval to prevent data drain
                for g in groups:
                    if g.get("type") in ("url-test", "fallback", "load-balance"):
                        g["lazy"] = True
                        g["interval"] = 1800  # check every 30m only when traffic active

                stable_tg_group = {
                    "name": "🛡 Stable-Telegram",
                    "type": "fallback",
                    "url": "https://api.telegram.org",
                    "interval": 1800,
                    "lazy": True,
                    "proxies": real_proxies
                }
                
                # Update or prepend groups
                has_stable = False
                for g in groups:
                    if g.get("name") == "PROXY":
                        # Point PROXY to fallback group first
                        if "🛡 Stable-Telegram" not in g.get("proxies", []):
                            g["proxies"].insert(0, "🛡 Stable-Telegram")
                    if g.get("name") == "🛡 Stable-Telegram":
                        has_stable = True
                if not has_stable:
                    groups.insert(0, stable_tg_group)

                config_data["proxy-groups"] = groups

                # 4. Multi-inbound: Dedicated ports for each server (10802, 10803, ...)
                dedicated_list = []
                listeners = []
                if dedicated_ports and real_proxies:
                    current_p = proxy_port + 1
                    for p_name in real_proxies:
                        if current_p >= proxy_port + 20: # max 20 dedicated ports
                            break
                        # Clean ascii name for group/listener
                        clean_group_name = f"DIRECT-{current_p}"
                        groups.append({
                            "name": clean_group_name,
                            "type": "select",
                            "proxies": [p_name]
                        })
                        listeners.append({
                            "name": f"in-{current_p}",
                            "type": "mixed",
                            "port": current_p,
                            "listen": "127.0.0.1",
                            "rule": f"MATCH,{clean_group_name}"
                        })
                        dedicated_list.append({"name": p_name, "port": current_p})
                        current_p += 1

                if listeners:
                    config_data["listeners"] = listeners

                # Write out final config
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)

                # Save .env
                with open(ENV_FILE, "w", encoding="utf-8") as f:
                    f.write(f'SAVED_SUB_URL="{sub_url}"\nSAVED_PROXY_PORT="{proxy_port}"\nSAVED_API_PORT="{api_port}"\nSAVED_MTPROTO="{"true" if enable_mtproto else "false"}"\nSAVED_DEDICATED="{"true" if dedicated_ports else "false"}"\n')

                # Restart mihomo daemon
                subprocess.run(["brew", "services", "restart", "mihomo"], capture_output=True)

                mtproto_link = None
                if enable_mtproto:
                    mtproto_port = proxy_port + 10
                    mtproto_secret = "ee112233445566778899aabbccddeeff7777772e676f6f676c652e636f6d"
                    mtproto_link = f"tg://proxy?server=127.0.0.1&port={mtproto_port}&secret={mtproto_secret}"

                resp_data = {
                    "success": True,
                    "proxy_port": proxy_port,
                    "tg_socks": f"tg://socks?server=127.0.0.1&port={proxy_port}",
                    "dashboard": f"http://127.0.0.1:{api_port}/ui/",
                    "dedicated_list": dedicated_list,
                    "tg_mtproto": mtproto_link
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp_data).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WizardHandler) as httpd:
        httpd.serve_forever()
