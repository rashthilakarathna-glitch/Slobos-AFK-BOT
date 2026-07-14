#!/usr/bin/env python3
"""
Aternos Minecraft 1.20 Server Keeper Bot - AUTO START & KEEP-ALIVE
Server: 1234-Qf37.aternos.me:45024
Automatically starts server and keeps it online!
"""

import requests
import time
import schedule
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aternos_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AternosBot:
    """Aternos Minecraft 1.20 Auto-Start & Keep-Alive Bot"""
    
    BASE_URL = "https://aternos.org"
    MINECRAFT_VERSION = "1.20"
    SERVER_ADDRESS = "1234-Qf37.aternos.me:45024"
    
    def __init__(self, username: str, password: str, server_id: str):
        self.username = username
        self.password = password
        self.server_id = server_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        self.is_logged_in = False
        self.keep_alive_count = 0
        self.server_started = False
        
    def login(self) -> bool:
        """Auto-login to Aternos"""
        try:
            logger.info(f"🔐 Auto-logging in to Aternos...")
            print("🔐 Logging in...")
            login_url = f"{self.BASE_URL}/api/user/login"
            data = {'user': self.username, 'password': self.password}
            response = self.session.post(login_url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Auto-login successful!")
                print("✅ Login successful!")
                self.is_logged_in = True
                return True
            else:
                logger.error(f"❌ Auto-login failed: {response.status_code}")
                print(f"❌ Login failed: {response.status_code}")
                self.is_logged_in = False
                return False
        except Exception as e:
            logger.error(f"❌ Login error: {str(e)}")
            print(f"❌ Login error: {str(e)}")
            self.is_logged_in = False
            return False
    
    def get_server_status(self) -> dict:
        """Get server status"""
        try:
            if not self.is_logged_in and not self.login():
                return None
            
            status_url = f"{self.BASE_URL}/api/server/{self.server_id}/status"
            response = self.session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                logger.info(f"📊 Server status: {status}")
                return status
            return None
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return None
    
    def start_server(self) -> bool:
        """Start the server"""
        try:
            if not self.is_logged_in and not self.login():
                return False
            
            logger.info("🚀 Starting server...")
            print("🚀 Starting server...")
            
            start_url = f"{self.BASE_URL}/api/server/{self.server_id}/start"
            response = self.session.post(start_url, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("✅ Server start command sent!")
                print("✅ Server start command sent!")
                self.server_started = True
                return True
            else:
                logger.warning(f"⚠️ Start response: {response.status_code}")
                print(f"⚠️ Start response: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
    
    def keep_alive(self) -> bool:
        """Send keep-alive signal to keep server online"""
        try:
            if not self.is_logged_in and not self.login():
                return False
            
            self.keep_alive_count += 1
            logger.info(f"📡 Keep-alive signal #{self.keep_alive_count}...")
            
            endpoints = [
                f"{self.BASE_URL}/api/server/{self.server_id}/confirm",
                f"{self.BASE_URL}/api/server/{self.server_id}/tick",
                f"{self.BASE_URL}/api/server/{self.server_id}/status"
            ]
            
            for endpoint in endpoints:
                try:
                    method = 'post' if 'confirm' in endpoint or 'tick' in endpoint else 'get'
                    response = self.session.post(endpoint, timeout=10) if method == 'post' else self.session.get(endpoint, timeout=10)
                    
                    if response.status_code in [200, 204]:
                        logger.info(f"✅ Keep-alive #{self.keep_alive_count} sent!")
                        return True
                except:
                    continue
            
            logger.warning("⚠️ Could not send keep-alive")
            return False
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False
    
    def auto_run(self, interval: int = 5):
        """Auto-run: Start server and keep it alive"""
        
        print("\n" + "="*70)
        print("🎮 MINECRAFT 1.20 - ATERNOS AUTO-START & KEEPER BOT")
        print("="*70)
        print(f"\n🎯 Server: {self.SERVER_ADDRESS}")
        print(f"📍 Server ID: {self.server_id}")
        print(f"⏱️  Keep-alive every {interval} minute(s)")
        print(f"🚀 Auto-starting server now...")
        print(f"📱 Keep this window open!")
        print(f"❌ Press Ctrl+C to stop\n")
        print("="*70 + "\n")
        
        logger.info(f"🤖 ATERNOS MC {self.MINECRAFT_VERSION} BOT - AUTO START MODE")
        logger.info(f"🎮 Server: {self.SERVER_ADDRESS}")
        logger.info(f"📍 Server ID: {self.server_id}")
        logger.info(f"⏱️  Keep-alive every {interval} minute(s)")
        
        # LOGIN FIRST
        print("⏳ Logging in...")
        if not self.login():
            logger.error("❌ Failed to login! Exiting...")
            print("❌ Login failed! Check credentials in config.py")
            return
        
        # CHECK STATUS
        print("\n📊 Checking server status...")
        status = self.get_server_status()
        if status:
            logger.info(f"Current status: {status}")
            print(f"📊 Status received: {status}")
        
        # START SERVER
        print("\n🚀 Starting server now...")
        self.start_server()
        
        # Wait for server to start
        print("⏳ Waiting for server to boot (30 seconds)...")
        time.sleep(30)
        
        print("\n✅ Server should be starting!")
        print("🔄 Now sending keep-alive signals every", interval, "minute(s)\n")
        
        # Schedule keep-alive
        schedule.every(interval).minutes.do(self.keep_alive)
        
        # Send first keep-alive
        logger.info("🚀 Sending first keep-alive signal...")
        print("📡 Sending first keep-alive...")
        self.keep_alive()
        
        logger.info("🎯 BOT NOW RUNNING - SERVER SHOULD BE ONLINE!")
        print("\n" + "="*70)
        print("✅ BOT RUNNING - SERVER SHOULD BE ONLINE!")
        print(f"🎮 Join your server: {self.SERVER_ADDRESS}")
        print("="*70 + "\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"\n🛑 Bot stopped by user! Total keep-alives: {self.keep_alive_count}")
            print(f"\n🛑 Bot stopped! Total keep-alives sent: {self.keep_alive_count}")


def load_config():
    """Load configuration from config.py"""
    try:
        if os.path.exists('config.py'):
            from config import ATERNOS_USERNAME, ATERNOS_PASSWORD, SERVER_ID, KEEP_ALIVE_INTERVAL
            return ATERNOS_USERNAME, ATERNOS_PASSWORD, SERVER_ID, KEEP_ALIVE_INTERVAL
    except:
        pass
    return None, None, None, None


def save_config(username, password, server_id, interval):
    """Save configuration to config.py"""
    config = f'''# Auto-generated configuration
# Server: 1234-Qf37.aternos.me:45024
ATERNOS_USERNAME = "{username}"
ATERNOS_PASSWORD = "{password}"
SERVER_ID = "{server_id}"
KEEP_ALIVE_INTERVAL = {interval}
'''
    with open('config.py', 'w') as f:
        f.write(config)
    logger.info("✅ Configuration saved to config.py")
    print("✅ Config saved!")


def initial_setup():
    """One-time setup"""
    print("\n" + "="*70)
    print("⚙️  ATERNOS BOT - INITIAL SETUP")
    print("="*70)
    print(f"\n🎮 Server: 1234-Qf37.aternos.me:45024")
    print("\n📍 How to find your Server ID:")
    print("   1. Go to aternos.org")
    print("   2. Select your Minecraft 1.20 server")
    print("   3. Look at URL: aternos.org/server/YOUR_ID/")
    print("   4. Copy YOUR_ID\n")
    
    username = input("📝 Enter Aternos Username: ").strip()
    if not username:
        print("❌ Username required!")
        return None, None, None, None
    
    password = input("🔑 Enter Aternos Password: ").strip()
    if not password:
        print("❌ Password required!")
        return None, None, None, None
    
    server_id = input("🖥️  Enter Server ID: ").strip()
    if not server_id:
        print("❌ Server ID required!")
        return None, None, None, None
    
    try:
        interval = int(input("⏱️  Keep-alive interval in minutes (default 5): ") or "5")
        if interval < 1:
            interval = 5
    except:
        interval = 5
    
    save_config(username, password, server_id, interval)
    print("\n✅ Setup complete! Bot will start your server...\n")
    return username, password, server_id, interval


def main():
    """Main auto-start function"""
    
    print("\n" + "="*70)
    print("🎮 MINECRAFT 1.20 - ATERNOS AUTO-START & KEEPER BOT")
    print("📱 GITHUB EDITION - AUTO START MODE")
    print(f"🎮 Server: 1234-Qf37.aternos.me:45024")
    print("="*70)
    
    # Load existing config
    username, password, server_id, interval = load_config()
    
    # If no config, do initial setup
    if not username or username == "your_username":
        print("\n⚠️  No configuration found!")
        print("Let's set up your bot (first time only)\n")
        username, password, server_id, interval = initial_setup()
    
    # Validate config
    if not username or not password or not server_id:
        print("\n❌ Configuration incomplete! Exiting...")
        return
    
    # Create bot and auto-start
    bot = AternosBot(username, password, server_id)
    bot.auto_run(interval=interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped!")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
