from flask import Flask, request, jsonify, Response
import logging
import threading
import csv
import io
from datetime import datetime
from scraper import MatchScraper
from database import DatabaseManager
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

app = Flask(__name__)

# Initialize scraper and database
scraper = MatchScraper()
db = DatabaseManager()
db.create_tables()
trigger_lock = threading.Lock()

def is_authorized():
    if not Config.WEBHOOK_TOKEN:
        return True
    provided_token = request.headers.get('X-Webhook-Token') or request.args.get('token')
    return provided_token == Config.WEBHOOK_TOKEN

@app.route('/', methods=['GET'])
def home():
    """Home endpoint - basic info"""
    return jsonify({
        'service': 'Match Saver Webhook',
        'status': 'running',
        'version': '1.0.0',
        'api': {
            'url': Config.get_api_url(),
            'sports': Config.DEFAULT_SPORTS,
            'count': Config.DEFAULT_COUNT,
            'language': Config.DEFAULT_LNG,
            'mode': Config.DEFAULT_MODE
        },
        'endpoints': {
            '/': 'Home',
            '/trigger': 'Trigger match scraping',
            '/stats': 'Database statistics',
            '/health': 'Health check'
        }
    })

@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    """
    Main webhook endpoint for cron job services
    When called, it scrapes the API and saves finished matches
    """
    logger.info("=" * 60)
    logger.info("Webhook triggered")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Method: {request.method}")
    logger.info(f"IP: {request.remote_addr}")
    
    if not is_authorized():
        logger.warning("Unauthorized webhook request")
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401
    
    if not trigger_lock.acquire(blocking=False):
        logger.warning("Webhook rejected: another execution is already running")
        return jsonify({
            'success': False,
            'message': 'Another scraping job is already running'
        }), 409
    
    try:
        # Run the scraper
        result = scraper.run(save_finished_only=True)
        
        # Get database stats
        stats = db.get_match_stats()
        
        logger.info(f"Webhook completed successfully")
        logger.info(f"Trigger result: {result}")
        logger.info(f"Database stats: {stats}")
        logger.info("=" * 60)
        
        return jsonify({
            'success': True,
            'message': 'Match scraping completed',
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        logger.error("=" * 60)
        
        return jsonify({
            'success': False,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
    finally:
        trigger_lock.release()

@app.route('/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        stats = db.get_match_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/export', methods=['GET'])
def export_dataset():
    """Download finished matches dataset as CSV or JSON"""
    if not is_authorized():
        logger.warning("Unauthorized export request")
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401
    
    export_format = (request.args.get('format') or 'csv').lower()
    limit = request.args.get('limit', type=int)
    rows = db.get_finished_match_dataset_rows(limit=limit)
    
    serialized_rows = [
        {
            'id': row.id,
            'match_id': row.match_id,
            'team_home': row.team_home,
            'team_away': row.team_away,
            'league': row.league,
            'score_home': row.score_home,
            'score_away': row.score_away,
            'finished_at': row.finished_at.isoformat() if row.finished_at else None,
            'source': row.source,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None
        }
        for row in rows
    ]
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    if export_format == 'json':
        return jsonify({
            'success': True,
            'count': len(serialized_rows),
            'exported_at': datetime.utcnow().isoformat(),
            'rows': serialized_rows
        }), 200
    
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            'id',
            'match_id',
            'team_home',
            'team_away',
            'league',
            'score_home',
            'score_away',
            'finished_at',
            'source',
            'created_at',
            'updated_at'
        ]
    )
    writer.writeheader()
    writer.writerows(serialized_rows)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=finished_matches_dataset_{timestamp}.csv'
        }
    )

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        db.check_connection()
        database_status = 'connected'
        status_code = 200
    except Exception as error:
        logger.error(f"Health check database error: {error}")
        database_status = 'error'
        status_code = 500
    
    return jsonify({
        'status': 'healthy' if status_code == 200 else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'database': database_status
    }), status_code

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint - doesn't save to database"""
    logger.info("Test endpoint called")
    
    try:
        # Fetch matches without saving
        data = scraper.fetch_matches()
        
        if data:
            matches = data.get('Value', [])
            finished_matches = [m for m in matches if m.get('SC', {}).get('GS') == 3]
            
            return jsonify({
                'success': True,
                'total_matches': len(matches),
                'finished_matches': len(finished_matches),
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch matches'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    db.create_tables()
    
    # Run Flask app
    logger.info("Starting Flask application...")
    logger.info(f"Database URL: {Config.get_database_url()}")
    app.run(host='0.0.0.0', port=5000, debug=False)
