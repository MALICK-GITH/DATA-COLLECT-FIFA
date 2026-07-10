import requests
import logging
import time
from datetime import datetime
from typing import List, Dict, Any
from config import Config
from database import DatabaseManager

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

def normalize_text(value: str = "") -> str:
    return (
        str(value or "")
        .lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ù", "u")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("ô", "o")
        .replace("ç", "c")
        .strip()
    )

class MatchScraper:
    def __init__(self):
        self.db = DatabaseManager()
        self.api_url = Config.get_api_url()

    def fetch_matches(self, sports=None, count=None, lng=None, mode=None) -> Dict[str, Any]:
        """Fetch matches from the API"""
        params = Config.get_api_params()
        overrides = {
            'sports': sports,
            'count': count,
            'lng': lng,
            'mode': mode
        }
        for key, value in overrides.items():
            if value is not None:
                params[key] = value

        max_attempts = max(Config.API_RETRY_COUNT, 1)
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Fetching matches with params: {params} (attempt {attempt}/{max_attempts})")
                response = requests.get(
                    self.api_url,
                    params=params,
                    headers=Config.get_api_headers(),
                    timeout=Config.API_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()

                if isinstance(data, dict) and data.get('Success'):
                    logger.info(f"Successfully fetched {len(data.get('Value', []))} matches")
                    return data

                logger.error(f"API returned error: {data.get('Error') if isinstance(data, dict) else 'Invalid JSON structure'}")
            except requests.exceptions.RequestException as error:
                logger.error(f"Error fetching matches: {error}")
            except ValueError as error:
                logger.error(f"Invalid JSON response: {error}")

            if attempt < max_attempts:
                sleep_seconds = Config.API_RETRY_BACKOFF_SECONDS * attempt
                logger.info(f"Retrying API call in {sleep_seconds} second(s)")
                time.sleep(sleep_seconds)

        return None
    
    def parse_status(self, gs: int, status_text: str, score_context: Dict[str, Any] | None = None) -> str:
        """Parse status code to human-readable status"""
        score_context = score_context or {}
        normalized_status = normalize_text(status_text)
        normalized_sls = normalize_text(score_context.get('SLS', ''))
        normalized_cps = normalize_text(score_context.get('CPS', ''))
        normalized_info = normalize_text(score_context.get('I', ''))
        
        if (
            gs == 3 or
            'termine' in normalized_status or
            'termine' in normalized_sls or
            'termine' in normalized_cps or
            'termine' in normalized_info
        ):
            return 'FINISHED'
        
        status_map = {
            0: 'NOT_STARTED',
            1: 'LIVE',
            2: 'HALFTIME',
            4: 'CANCELLED',
            5: 'POSTPONED',
            6: 'INTERRUPTED',
            128: 'PREMATCH'
        }
        return status_map.get(gs, 'UNKNOWN')
    
    def parse_match(self, raw_match: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw match data to database format"""
        score_context = raw_match.get('SC', {})
        gs = score_context.get('GS', 0)
        
        # Parse score
        final_score = score_context.get('FS', {})
        home_score = final_score.get('S1') if final_score else None
        away_score = final_score.get('S2') if final_score else None
        
        # Parse status
        status = self.parse_status(gs, score_context.get('I', ''), score_context)
        
        # Parse timing
        start_time = None
        if raw_match.get('S'):
            start_time = datetime.fromtimestamp(raw_match['S'])
        
        last_update = None
        if raw_match.get('U'):
            last_update = datetime.fromtimestamp(raw_match['U'])
        
        # If match is finished, set finish time
        finish_time = None
        if status == 'FINISHED' and last_update:
            finish_time = last_update
        
        # Parse main odds
        odds = []
        for odd in raw_match.get('E', []):
            odds.append({
                'bet_type': odd.get('T'),
                'odds_value': odd.get('C'),
                'odds_formatted': odd.get('CV'),
                'group_id': odd.get('G'),
                'parameter': odd.get('P'),
                'is_boosted': odd.get('B', False),
                'count_enabled': odd.get('CE')
            })
        
        # Parse additional odds
        additional_odds = []
        for group in raw_match.get('AE', []):
            for market in group.get('ME', []):
                additional_odds.append({
                    'group_id': group.get('G'),
                    'bet_type': market.get('T'),
                    'odds_value': market.get('C'),
                    'odds_formatted': market.get('CV'),
                    'parameter': market.get('P'),
                    'count_enabled': market.get('CE')
                })
        
        return {
            'event_id': raw_match.get('I'),
            'sport_id': raw_match.get('SI'),
            'sport_name': raw_match.get('SN'),
            'league_id': raw_match.get('LI'),
            'league_name': raw_match.get('L'),
            'league_name_en': raw_match.get('LE'),
            'league_name_ru': raw_match.get('LR'),
            'country': raw_match.get('CN'),
            'country_en': raw_match.get('CE'),
            'country_code': raw_match.get('COI'),
            
            'home_team_id': raw_match.get('O1I'),
            'home_team_name': raw_match.get('O1'),
            'home_team_name_en': raw_match.get('O1E'),
            'home_team_name_ru': raw_match.get('O1R'),
            'home_team_country': raw_match.get('O1C'),
            'home_team_city': raw_match.get('O1CT'),
            'home_team_image': raw_match.get('O1IMG', [None])[0] if raw_match.get('O1IMG') else None,
            
            'away_team_id': raw_match.get('O2I'),
            'away_team_name': raw_match.get('O2'),
            'away_team_name_en': raw_match.get('O2E'),
            'away_team_name_ru': raw_match.get('O2R'),
            'away_team_country': raw_match.get('O2C'),
            'away_team_city': raw_match.get('O2CT'),
            'away_team_image': raw_match.get('O2IMG', [None])[0] if raw_match.get('O2IMG') else None,
            
            'start_time': start_time,
            'last_update': last_update,
            'finish_time': finish_time,
            'status': status,
            'status_code': gs,
            
            'home_score': home_score,
            'away_score': away_score,
            'score_json': score_context,
            
            'is_hot': raw_match.get('HS') == 1,
            'is_highlighted': raw_match.get('HMH') == 1,
            'event_count': raw_match.get('EC'),
            'special_group': raw_match.get('SGC'),
            
            'raw_data': raw_match,
            'odds': odds,
            'additional_odds': additional_odds
        }
    
    def save_finished_matches(self, matches: List[Dict[str, Any]]) -> Dict[str, int]:
        """Save only finished matches to database"""
        summary = {
            'finished_seen': 0,
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        for match in matches:
            parsed = self.parse_match(match)
            if parsed['status'] == 'FINISHED':
                summary['finished_seen'] += 1
                try:
                    result = self.db.save_finished_match_dataset(parsed)
                    action = result.get('action', 'skipped')
                    if action in summary:
                        summary[action] += 1
                    logger.info(
                        f"Saved finished match [{action}]: "
                        f"{parsed['home_team_name']} vs {parsed['away_team_name']} "
                        f"({parsed['home_score']}-{parsed['away_score']})"
                    )
                except Exception as e:
                    summary['errors'] += 1
                    logger.error(f"Error saving match: {e}")
        return summary
    
    def save_all_matches(self, matches: List[Dict[str, Any]]) -> int:
        """Save all matches to database"""
        saved_count = 0
        for match in matches:
            parsed = self.parse_match(match)
            try:
                self.db.save_match(parsed)
                saved_count += 1
                logger.info(f"Saved match: {parsed['home_team_name']} vs {parsed['away_team_name']} - Status: {parsed['status']}")
            except Exception as e:
                logger.error(f"Error saving match: {e}")
        return saved_count
    
    def run(self, save_finished_only=True):
        """Main run method"""
        logger.info("Starting match scraper")
        
        # Fetch matches
        data = self.fetch_matches()
        if not data:
            logger.error("Failed to fetch matches")
            return
        
        matches = data.get('Value', [])
        logger.info(f"Processing {len(matches)} matches")
        
        # Save matches
        if save_finished_only:
            save_summary = self.save_finished_matches(matches)
            logger.info(f"Finished matches summary: {save_summary}")
        else:
            saved_count = self.save_all_matches(matches)
            logger.info(f"Saved {saved_count} matches")
        
        # Print stats
        stats = self.db.get_match_stats()
        logger.info(f"Database stats: {stats}")
        
        logger.info("Match scraper completed")
        return {
            'fetched_matches': len(matches),
            'save_summary': save_summary if save_finished_only else {
                'saved_all_matches': saved_count
            },
            'stats': stats
        }

def main():
    """Main entry point"""
    scraper = MatchScraper()
    scraper.run(save_finished_only=True)

if __name__ == "__main__":
    main()
