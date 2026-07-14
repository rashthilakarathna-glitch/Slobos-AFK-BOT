import requests
import time
import schedule
import logging
from datetime import datetime
from typing import Optional
import json
import os
import sys

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
    """Bot to keep Aternos server alive by periodic activity"""
    
    BASE_URL = "https://aternos.org"
    
    def __init__(self, username: str, password: str, server_id: str):
        """
        Initialize the Aternos bot
        
        Args:
            username: Aternos username
            password: Aternos password
            server_id: Server ID (found in Aternos dashboard URL)
        """
        self.username = username
        self.password = password
        self.server_id = server_id
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        self.is_logged_in = False
        self.csrf_token = None
        
    def get_csrf_token(self) -> bool:
        """Get CSRF token from login page"""
        try:
            logger.info("Fetching CSRF token...")
            response = self.session.get(f"{self.BASE_URL}/", timeout=10)
            
            if 'token' in response.text:
                logger.info("✓ CSRF token obtained")
                return True
            else:
                logger.warning("Could not find CSRF token in page")
                return False
                
        except Exception as e:
            logger.error(f"Error getting CSRF token: {str(e)}")
            return False
    
    def login(self) -> bool:
        """Login to Aternos account"""
        try:
            logger.info("Attempting to login to Aternos...")
            
            # First get CSRF token
            if not self.get_csrf_token():
                logger.error("Failed to get CSRF token")
                return False
            
            # Login endpoint
            login_url = f"{self.BASE_URL}/api/user/login"
            
            data = {
                'user': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, json=data, timeout=10)
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if resp_json.get('success') or response.status_code == 200:
                        logger.info("✓ Successfully logged in to Aternos")
                        self.is_logged_in = True
                        return True
                except:
                    self.is_logged_in = True
                    logger.info("✓ Successfully logged in to Aternos")
                    return True
            else:
                logger.error(f"✗ Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Login error: {str(e)}")
            return False
    
    def get_server_status(self) -> Optional[dict]:
        """Get current server status"""
        try:
            if not self.is_logged_in:
                logger.warning("Not logged in, attempting to login...")
                if not self.login():
                    return None
            
            status_url = f"{self.BASE_URL}/api/server/{self.server_id}/status"
            response = self.session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                logger.info(f"Server status: {status_data}")
                return status_data
            else:
                logger.warning(f"Could not fetch server status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting server status: {str(e)}")
            return None
    
    def keep_alive(self) -> bool:
        """Send keep-alive signal to keep server active"""
        try:
            if not self.is_logged_in:
                if not self.login():
                    logger.error("Cannot send keep-alive: not logged in")
                    return False
            
            logger.info("📡 Sending keep-alive signal...")
            
            endpoints = [
                f"{self.BASE_URL}/api/server/{self.server_id}/confirm",
                f"{self.BASE_URL}/api/server/{self.server_id}/tick",
                f"{self.BASE_URL}/api/server/{self.server_id}/status"
            ]
            
            for endpoint in endpoints:
                try:
                    if "confirm" in endpoint or "tick" in endpoint:
                        response = self.session.post(endpoint, timeout=10)
                    else:
                        response = self.session.get(endpoint, timeout=10)
                    
                    if response.status_code in [200, 204]:
                        logger.info(f"✓ Keep-alive signal sent successfully")
                        return True
                        
                except Exception as e:
                    logger.debug(f"Endpoint failed: {str(e)}")
                    continue
            
            logger.warning("Could not send keep-alive to any endpoint")
            return False
                
        except Exception as e:
            logger.error(f"Error sending keep-alive: {str(e)}")
            return False
    
    def start_server(self) -> bool:
        """Start the server if it's offline"""
        try:
            if not self.is_logged_in:
                if not self.login():
                    return False
            
            logger.info("🚀 Attempting to start server...")
            
            start_url = f"{self.BASE_URL}/api/server/{self.server_id}/start"
            response = self.session.post(start_url, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("✓ Server start command sent")
                return True
            else:
                logger.warning(f"Start command response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the server"""
        try:
            if not self.is_logged_in:
                if not self.login():
                    return False
            
            logger.info("⏹️  Attempting to stop server...")
            
            stop_url = f"{self.BASE_URL}/api/server/{self.server_id}/stop"
            response = self.session.post(stop_url, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("✓ Server stop command sent")
                return True
            else:
                logger.warning(f"Stop command response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping server: {str(e)}")
            return False
    
    def scheduled_keep_alive(self):
        """Scheduled keep-alive task"""
        logger.info(f"⏰ Keep-alive at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.keep_alive()
    
    def start_scheduler(self, interval: int = 5):
        """Start the scheduler to keep server alive"""
        logger.info(f"🤖 Starting Aternos Bot - Keep-alive every {interval} minutes")
        logger.info(f"📍 Server ID: {self.server_id}")
        logger.info(f"⏱️  Bot is running. Do NOT close this window!")
        
        schedule.every(interval).minutes.do(self.scheduled_keep_alive)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")


def display_menu():
    """Display interactive menu for phone users"""
    print("\n" + "="*50)
    print("🤖 ATERNOS SERVER KEEPER BOT")
    print("="*50)
    print("\n1️⃣  Start Bot (Keep-Alive)")
    print("2️⃣  Check Server Status")
    print("3️⃣  Start Server")
    print("4️⃣  Stop Server")
    print("5️⃣  Change Settings")
    print("6️⃣  View Logs")
    print("7️⃣  Exit")
    print("\n" + "="*50)


def load_config():
    """Load configuration from config.py or ask user"""
    try:
        from config import ATERNOS_USERNAME, ATERNOS_PASSWORD, SERVER_ID, KEEP_ALIVE_INTERVAL
        return ATERNOS_USERNAME, ATERNOS_PASSWORD, SERVER_ID, KEEP_ALIVE_INTERVAL
    except:
        return None, None, None, None


def save_config(username, password, server_id, interval):
    """Save configuration to config.py"""
    config_content = f'''#!/usr/bin/env python3
ATERNOS_USERNAME = "{username}"
ATERNOS_PASSWORD = "{password}"
SERVER_ID = "{server_id}"
KEEP_ALIVE_INTERVAL = {interval}
'''
    with open('config.py', 'w') as f:
        f.write(config_content)
    logger.info("✓ Configuration saved to config.py")


def setup_config():
    """Interactive setup for configuration"""
    print("\n" + "="*50)
    print("⚙️  CONFIGURATION SETUP")
    print("="*50)
    
    username = input("\n📝 Enter your Aternos username: ").strip()
    password = input("🔑 Enter your Aternos password: ").strip()
    server_id = input("🖥️  Enter your Server ID (from URL): ").strip()
    
    try:
        interval = int(input("⏱️  Keep-alive interval in minutes (default 5): ") or "5")
    except:
        interval = 5
    
    save_config(username, password, server_id, interval)
    print("\n✓ Configuration saved!")
    return username, password, server_id, interval


def main():
    """Main function with interactive menu"""
    
    print("\n" + "="*50)
    print("🤖 ATERNOS SERVER KEEPER BOT - PHONE EDITION")
    print("="*50)
    
    # Load config
    username, password, server_id, interval = load_config()
    
    if not username or username == "your_aternos_username":
        print("\n⚠️  No configuration found!")
        print("Let's set up your bot...\n")
        username, password, server_id, interval = setup_config()
    
    if not username or not password or not server_id:
        print("\n❌ Configuration incomplete. Please try again.")
        return
    
    bot = AternosBot(username, password, server_id)
    
    while True:
        display_menu()
        choice = input("\n👉 Enter your choice (1-7): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Bot...")
            print("⚠️  Keep this window open to keep the server alive!")
            print("📱 If this closes, the bot stops.\n")
            if bot.login():
                bot.start_scheduler(interval=interval)
            else:
                print("❌ Failed to login. Check your credentials!")
                
        elif choice == "2":
            print("\n🔍 Checking server status...")
            if bot.login():
                status = bot.get_server_status()
                if status:
                    print(f"✓ Server Status: {json.dumps(status, indent=2)}")
                else:
                    print("❌ Could not fetch server status")
            else:
                print("❌ Failed to login")
                
        elif choice == "3":
            print("\n🚀 Starting server...")
            if bot.login():
                if bot.start_server():
                    print("✓ Server start command sent!")
                else:
                    print("❌ Failed to start server")
            else:
                print("❌ Failed to login")
                
        elif choice == "4":
            print("\n⏹️  Stopping server...")
            if bot.login():
                if bot.stop_server():
                    print("✓ Server stop command sent!")
                else:
                    print("❌ Failed to stop server")
            else:
                print("❌ Failed to login")
                
        elif choice == "5":
            print("\n⚙️  Changing settings...")
            username, password, server_id, interval = setup_config()
            bot = AternosBot(username, password, server_id)
            print("\n✓ Settings updated!")
            
        elif choice == "6":
            print("\n📋 Recent Logs:")
            print("="*50)
            try:
                with open('aternos_bot.log', 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.strip())
            except:
                print("No logs found yet.")
            print("="*50)
                
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
