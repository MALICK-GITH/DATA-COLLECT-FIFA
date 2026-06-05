import schedule
import time
import logging
from scraper import MatchScraper
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CronService:
    def __init__(self):
        self.scraper = MatchScraper()
        self.running = False
        
    def job(self):
        """Scheduled job"""
        logger.info("=" * 50)
        logger.info("Running scheduled job")
        try:
            self.scraper.run(save_finished_only=True)
        except Exception as e:
            logger.error(f"Error in scheduled job: {e}")
        logger.info("=" * 50)
    
    def start(self):
        """Start the cron service"""
        logger.info("Starting cron service")
        self.running = True
        
        schedule_minutes = max(Config.SCHEDULE_EVERY_MINUTES, 1)
        logger.info(f"Configured schedule: every {schedule_minutes} minute(s) (CRON_SCHEDULE={Config.CRON_SCHEDULE})")
        schedule.every(schedule_minutes).minutes.do(self.job)
        
        # Run immediately on start
        self.job()
        
        # Keep the service running
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop(self):
        """Stop the cron service"""
        logger.info("Stopping cron service")
        self.running = False

def main():
    """Main entry point for the service"""
    service = CronService()
    
    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        service.stop()

if __name__ == "__main__":
    main()
