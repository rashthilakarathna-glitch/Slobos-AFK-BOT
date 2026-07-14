# 🤖 ATERNOS MINECRAFT 1.20 BOT - AUTO-JOIN

**⚡ Starts Server + Auto-Joins + Keep-Alive**

**🎮 Server: `1234-Qf37.aternos.me:45024`**

## 🎮 AUTO-JOIN FEATURE

Bot will:
1. 🚀 Start your server
2. ⏳ Wait 10 seconds
3. 🎮 **Auto-join as your player**
4. 📡 Keep-alive every 1 minute
5. ♾️ Server stays ONLINE

## 📱 Quick Start

```bash
git clone https://github.com/rashthilakarathna-glitch/Slobos-AFK-BOT
cd Slobos-AFK-BOT
pip install -r requirements.txt
python aternos_bot.py
```

Answer 4 questions:
- Aternos username
- Aternos password
- Server ID
- **Minecraft username (for auto-join)**

Bot starts → **Auto-joins server!** ✅

## 🎮 What Happens

```
🔐 Logging in...
✅ Login successful!

🚀 Starting server...
✅ Server starting!

⏳ Waiting 10 seconds...

✅ SERVER SHOULD BE ONLINE NOW!
🎮 SERVER: 1234-Qf37.aternos.me:45024

🤖 Auto-joining server as YourUsername...
✅ Minecraft should open - join server!

🔄 Sending keep-alive every 1 minute
📡 Keep-alive #1
✅ Keep-alive #1
📡 Keep-alive #2
✅ Keep-alive #2
...
```

## ⏱️ Timeline

- **5 sec** - Login
- **2 sec** - Start command
- **10 sec** - Boot wait
- **0-5 sec** - Auto-join server
- **~22 sec** - YOU'RE IN! ✅

## 🔧 Config

Edit `config.py`:

```python
ATERNOS_USERNAME = "your_username"
ATERNOS_PASSWORD = "your_password"
SERVER_ID = "your_server_id"
KEEP_ALIVE_INTERVAL = 1
MINECRAFT_USERNAME = "YourMinecraftName"
```

## 📍 Server ID

Find at: `aternos.org/server/YOUR_ID/`

## 📋 Logs

```bash
cat aternos_bot.log
```

## ✅ Features

- ✅ Auto-start server
- ✅ **Auto-join server** (new!)
- ✅ Keep-alive every 1 minute
- ✅ Phone-friendly (Termux)
- ✅ Real-time logs
- ✅ Auto-reconnect

## ⚠️ Important

- Keep Termux open
- Keep screen on
- Use WiFi
- Plug in charger

## 🎯 Result

Server **NEVER goes offline!** 🎮✅

Bot keeps it alive 24/7 with player auto-join!

---

**ULTIMATE ATERNOS BOT!** 🚀📱✅
