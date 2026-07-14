import requests
import time
import schedule
import logging
from datetime import datetime
from typing import Optional

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.is_logged_in = False
        
    def login(self) -> bool:
        """Login to Aternos account"""
        try:
            logger.info("Attempting to login to Aternos...")
            
            login_url = "https://aternos.org/api/user/login"
            data = {
                'user': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Successfully logged in to Aternos")
                self.is_logged_in = True
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
            
            status_url = f"https://aternos.org/api/server/{self.server_id}/info"
            response = self.session.get(status_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
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
            
            # Method 1: Send activity to server info endpoint
            keep_alive_url = f"https://aternos.org/api/server/{self.server_id}/confirm"
            response = self.session.post(keep_alive_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Keep-alive signal sent successfully")
                return True
            elif response.status_code == 401:
                logger.warning("Session expired, re-logging in...")
                self.is_logged_in = False
                return self.keep_alive()  # Retry after login
            else:
                logger.warning(f"Keep-alive response: {response.status_code}")
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
            
            start_url = f"https://aternos.org/api/server/{self.server_id}/start"
            response = self.session.post(start_url, timeout=10)
            
            if response.status_code == 200:
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
            
            stop_url = f"https://aternos.org/api/server/{self.server_id}/stop"
            response = self.session.post(stop_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Server stop command sent")
                return True
            else:
                logger.warning(f"Stop command response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping server: {str(e)}")
            return False
    
    def scheduled_keep_alive(self):
        """Scheduled keep-alive task (runs every 5 minutes)"""
        logger.info(f"⏰ Running scheduled keep-alive at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.keep_alive()
    
    def start_scheduler(self, interval: int = 5):
        """
        Start the scheduler to keep server alive
        
        Args:
            interval: Minutes between keep-alive signals (default: 5)
        """
        logger.info(f"🤖 Starting Aternos Bot - Keep-alive every {interval} minutes")
        logger.info(f"📍 Server ID: {self.server_id}")
        
        # Schedule the task
        schedule.every(interval).minutes.do(self.scheduled_keep_alive)
        
        # Keep scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")


def main():
    """Main function to run the bot"""
    
    # Configuration - UPDATE THESE WITH YOUR DETAILS
    ATERNOS_USERNAME = "your_aternos_username"  # Replace with your Aternos username
    ATERNOS_PASSWORD = "your_aternos_password"  # Replace with your Aternos password
    SERVER_ID = "your_server_id"               # Replace with your server ID
    KEEP_ALIVE_INTERVAL = 5                    # Minutes between keep-alive signals
    
    # Validate configuration
    if ATERNOS_USERNAME == "your_aternos_username":
        logger.error("❌ Please configure ATERNOS_USERNAME, ATERNOS_PASSWORD, and SERVER_ID in the script")
        return
    
    # Create and start bot
    bot = AternosBot(ATERNOS_USERNAME, ATERNOS_PASSWORD, SERVER_ID)
    
    # Initial login
    if bot.login():
        # Start scheduler
        bot.start_scheduler(interval=KEEP_ALIVE_INTERVAL)
    else:
        logger.error("Failed to initialize bot - login unsuccessful")


if __name__ == "__main__":
    main()
