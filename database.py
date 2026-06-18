from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey, BigInteger, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, unique=True, nullable=False, index=True)
    sport_id = Column(Integer, nullable=False, index=True)
    sport_name = Column(String(100))
    league_id = Column(Integer, index=True)
    league_name = Column(String(255))
    league_name_en = Column(String(255))
    league_name_ru = Column(String(255))
    country = Column(String(100))
    country_en = Column(String(100))
    country_code = Column(Integer)
    
    # Teams
    home_team_id = Column(Integer)
    home_team_name = Column(String(255), nullable=False)
    home_team_name_en = Column(String(255))
    home_team_name_ru = Column(String(255))
    home_team_country = Column(Integer)
    home_team_city = Column(String(100))
    home_team_image = Column(String(500))
    
    away_team_id = Column(Integer)
    away_team_name = Column(String(255), nullable=False)
    away_team_name_en = Column(String(255))
    away_team_name_ru = Column(String(255))
    away_team_country = Column(Integer)
    away_team_city = Column(String(100))
    away_team_image = Column(String(500))
    
    # Timing
    start_time = Column(DateTime)
    last_update = Column(DateTime)
    finish_time = Column(DateTime)
    status = Column(String(50), index=True)  # FINISHED, CANCELLED, POSTPONED, etc.
    status_code = Column(Integer, index=True)  # GS value
    
    # Score
    home_score = Column(Integer)
    away_score = Column(Integer)
    score_json = Column(JSON)
    
    # Metadata
    is_hot = Column(Boolean, default=False)
    is_highlighted = Column(Boolean, default=False)
    event_count = Column(Integer)
    special_group = Column(Integer)
    
    # Raw data
    raw_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    odds = relationship("Odds", back_populates="match", cascade="all, delete-orphan")
    additional_odds = relationship("AdditionalOdds", back_populates="match", cascade="all, delete-orphan")

class Odds(Base):
    __tablename__ = 'odds'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False, index=True)
    
    bet_type = Column(Integer, index=True)  # T value
    odds_value = Column(Float, nullable=False)
    odds_formatted = Column(String(50))
    group_id = Column(Integer, index=True)  # G value
    parameter = Column(Float, nullable=True)  # P value
    is_boosted = Column(Boolean, default=False)
    count_enabled = Column(Integer)
    
    match = relationship("Match", back_populates="odds")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AdditionalOdds(Base):
    __tablename__ = 'additional_odds'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False, index=True)
    
    group_id = Column(Integer, index=True)
    bet_type = Column(Integer, index=True)
    odds_value = Column(Float, nullable=False)
    odds_formatted = Column(String(50))
    parameter = Column(Float, nullable=True)
    count_enabled = Column(Integer)
    
    match = relationship("Match", back_populates="additional_odds")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class FinishedMatchDataset(Base):
    __tablename__ = 'finished_matches_dataset'
    
    id = Column(BigInteger, primary_key=True)
    match_id = Column(String, unique=True, nullable=False, index=True)
    team_home = Column(String, nullable=False)
    team_away = Column(String, nullable=False)
    league = Column(String, nullable=False)
    score_home = Column(Integer, nullable=False)
    score_away = Column(Integer, nullable=False)
    finished_at = Column(DateTime(timezone=True))
    source = Column(String)
    raw_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.get_database_url())
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully")
    
    def drop_tables(self):
        Base.metadata.drop_all(self.engine)
        print("Database tables dropped")
    
    def get_session(self):
        return self.Session()
    
    def match_exists(self, event_id):
        session = self.get_session()
        try:
            match = session.query(Match).filter_by(event_id=event_id).first()
            return match is not None
        finally:
            session.close()
    
    def save_match(self, match_data):
        session = self.get_session()
        try:
            payload = dict(match_data)
            
            # Check if match already exists
            existing_match = session.query(Match).filter_by(event_id=payload['event_id']).first()
            
            if existing_match:
                # Update existing match
                for key, value in payload.items():
                    if key != 'odds' and key != 'additional_odds' and key != 'raw_data':
                        setattr(existing_match, key, value)
                existing_match.raw_data = payload.get('raw_data')
                existing_match.updated_at = datetime.utcnow()
                
                # Delete old odds and add new ones
                session.query(Odds).filter_by(match_id=existing_match.id).delete()
                session.query(AdditionalOdds).filter_by(match_id=existing_match.id).delete()
                
                for odd_data in payload.get('odds', []):
                    odd = Odds(match_id=existing_match.id, **odd_data)
                    session.add(odd)
                
                for odd_data in payload.get('additional_odds', []):
                    odd = AdditionalOdds(match_id=existing_match.id, **odd_data)
                    session.add(odd)
                
                self._upsert_finished_match_dataset(session, payload)
                
                session.commit()
                return existing_match.id
            else:
                # Create new match
                odds_data = payload.pop('odds', [])
                additional_odds_data = payload.pop('additional_odds', [])
                raw_data = payload.pop('raw_data', None)
                
                match = Match(**payload, raw_data=raw_data)
                session.add(match)
                session.flush()  # Get the ID
                
                for odd_data in odds_data:
                    odd = Odds(match_id=match.id, **odd_data)
                    session.add(odd)
                
                for odd_data in additional_odds_data:
                    odd = AdditionalOdds(match_id=match.id, **odd_data)
                    session.add(odd)
                
                self._upsert_finished_match_dataset(session, {
                    **payload,
                    'raw_data': raw_data,
                    'odds': odds_data,
                    'additional_odds': additional_odds_data
                })
                
                session.commit()
                return match.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _upsert_finished_match_dataset(self, session, match_data):
        if match_data.get('status') != 'FINISHED':
            return {'action': 'skipped', 'id': None}
        
        dataset_payload = {
            'match_id': str(match_data['event_id']),
            'team_home': match_data.get('home_team_name') or 'Unknown',
            'team_away': match_data.get('away_team_name') or 'Unknown',
            'league': match_data.get('league_name') or match_data.get('league_name_en') or 'Unknown',
            'score_home': match_data.get('home_score') if match_data.get('home_score') is not None else 0,
            'score_away': match_data.get('away_score') if match_data.get('away_score') is not None else 0,
            'finished_at': match_data.get('finish_time') or match_data.get('last_update') or match_data.get('start_time'),
            'source': 'livefeedsht-vmp',
            'raw_json': match_data.get('raw_data')
        }
        
        existing_row = session.query(FinishedMatchDataset).filter_by(match_id=dataset_payload['match_id']).first()
        
        if existing_row:
            existing_row.team_home = dataset_payload['team_home']
            existing_row.team_away = dataset_payload['team_away']
            existing_row.league = dataset_payload['league']
            existing_row.score_home = dataset_payload['score_home']
            existing_row.score_away = dataset_payload['score_away']
            existing_row.finished_at = dataset_payload['finished_at']
            existing_row.source = dataset_payload['source']
            existing_row.raw_json = dataset_payload['raw_json']
            existing_row.updated_at = datetime.utcnow()
            return {'action': 'updated', 'id': existing_row.id}
        
        dataset_row = FinishedMatchDataset(**dataset_payload)
        session.add(dataset_row)
        session.flush()
        return {'action': 'inserted', 'id': dataset_row.id}
    
    def save_finished_match_dataset(self, match_data):
        session = self.get_session()
        try:
            result = self._upsert_finished_match_dataset(session, match_data)
            session.commit()
            return result
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()
    
    def delete_match_from_dataset(self, match_id):
        session = self.get_session()
        try:
            deleted_count = session.query(FinishedMatchDataset).filter_by(match_id=str(match_id)).delete()
            session.commit()
            return deleted_count
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()
    
    def check_connection(self):
        session = self.get_session()
        try:
            session.execute(text("SELECT 1"))
            return True
        finally:
            session.close()
    
    def get_finished_matches(self, limit=None):
        session = self.get_session()
        try:
            query = session.query(Match).filter(Match.status == 'FINISHED')
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()
    
    def get_finished_match_dataset_rows(self, limit=None):
        session = self.get_session()
        try:
            query = session.query(FinishedMatchDataset).order_by(FinishedMatchDataset.finished_at.desc(), FinishedMatchDataset.id.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()
    
    def get_match_stats(self):
        session = self.get_session()
        try:
            dataset_finished_matches = session.query(FinishedMatchDataset).count()
            
            try:
                total_matches = session.query(Match).count()
                finished_matches = session.query(Match).filter(Match.status == 'FINISHED').count()
                cancelled_matches = session.query(Match).filter(Match.status == 'CANCELLED').count()
            except Exception:
                total_matches = 0
                finished_matches = dataset_finished_matches
                cancelled_matches = 0
            
            return {
                'total': total_matches,
                'finished': finished_matches,
                'cancelled': cancelled_matches,
                'other': max(total_matches - finished_matches - cancelled_matches, 0),
                'finished_matches_dataset': dataset_finished_matches
            }
        finally:
            session.close()
