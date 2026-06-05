"""
Exemples de requêtes sur la base de données de matchs
"""
from database import DatabaseManager, Match, Odds, AdditionalOdds
from sqlalchemy import func, desc
from datetime import datetime, timedelta

def example_queries():
    db = DatabaseManager()
    session = db.get_session()
    
    print("=" * 60)
    print("EXEMPLES DE REQUÊTES")
    print("=" * 60)
    
    # 1. Statistiques générales
    print("\n1. Statistiques générales:")
    stats = db.get_match_stats()
    print(f"   Total matchs: {stats['total']}")
    print(f"   Terminés: {stats['finished']}")
    print(f"   Annulés: {stats['cancelled']}")
    print(f"   Autres: {stats['other']}")
    
    # 2. Derniers matchs terminés
    print("\n2. Derniers matchs terminés:")
    recent_matches = session.query(Match)\
        .filter(Match.status == 'FINISHED')\
        .order_by(desc(Match.finish_time))\
        .limit(5)\
        .all()
    
    for match in recent_matches:
        print(f"   {match.home_team_name} {match.home_score} - {match.away_score} {match.away_team_name}")
        print(f"   Ligue: {match.league_name}")
        print(f"   Date: {match.finish_time}")
        print()
    
    # 3. Matchs avec beaucoup de buts
    print("\n3. Matchs avec plus de 5 buts:")
    high_scoring = session.query(Match)\
        .filter(Match.status == 'FINISHED')\
        .filter((Match.home_score + Match.away_score) > 5)\
        .order_by(desc(Match.home_score + Match.away_score))\
        .limit(5)\
        .all()
    
    for match in high_scoring:
        total_goals = match.home_score + match.away_score
        print(f"   {match.home_team_name} {match.home_score} - {match.away_score} {match.away_team_name} ({total_goals} buts)")
    
    # 4. Matchs par ligue
    print("\n4. Nombre de matchs par ligue:")
    league_stats = session.query(
        Match.league_name,
        func.count(Match.id).label('count')
    ).filter(Match.status == 'FINISHED')\
     .group_by(Match.league_name)\
     .order_by(desc('count'))\
     .limit(10)\
     .all()
    
    for league, count in league_stats:
        print(f"   {league}: {count} matchs")
    
    # 5. Équipes les plus performantes (victoires)
    print("\n5. Équipes avec le plus de victoires à domicile:")
    home_wins = session.query(
        Match.home_team_name,
        func.count(Match.id).label('wins')
    ).filter(Match.status == 'FINISHED')\
     .filter(Match.home_score > Match.away_score)\
     .group_by(Match.home_team_name)\
     .order_by(desc('wins'))\
     .limit(5)\
     .all()
    
    for team, wins in home_wins:
        print(f"   {team}: {wins} victoires")
    
    # 6. Matchs des dernières 24h
    print("\n6. Matchs terminés dans les dernières 24h:")
    yesterday = datetime.now() - timedelta(days=1)
    recent_24h = session.query(Match)\
        .filter(Match.status == 'FINISHED')\
        .filter(Match.finish_time >= yesterday)\
        .order_by(desc(Match.finish_time))\
        .all()
    
    print(f"   {len(recent_24h)} matchs terminés dans les dernières 24h")
    
    # 7. Cotes moyennes par type de pari
    print("\n7. Cotes moyennes pour victoire domicile (T=1):")
    avg_odds = session.query(
        func.avg(Odds.odds_value).label('avg_odds')
    ).filter(Odds.bet_type == 1)\
     .first()
    
    print(f"   Cote moyenne victoire domicile: {avg_odds.avg_odds:.2f}")
    
    # 8. Matchs annulés
    print("\n8. Matchs annulés:")
    cancelled = session.query(Match)\
        .filter(Match.status == 'CANCELLED')\
        .order_by(desc(Match.created_at))\
        .limit(5)\
        .all()
    
    for match in cancelled:
        print(f"   {match.home_team_name} vs {match.away_team_name}")
        print(f"   Annulé le: {match.created_at}")
    
    # 9. Distribution des scores
    print("\n9. Scores les plus fréquents:")
    score_distribution = session.query(
        Match.home_score,
        Match.away_score,
        func.count(Match.id).label('count')
    ).filter(Match.status == 'FINISHED')\
     .group_by(Match.home_score, Match.away_score)\
     .order_by(desc('count'))\
     .limit(5)\
     .all()
    
    for home, away, count in score_distribution:
        print(f"   {home}-{away}: {count} fois")
    
    # 10. Matchs avec cotes boostées
    print("\n10. Matchs avec cotes boostées:")
    boosted_matches = session.query(Match)\
        .join(Odds, Match.id == Odds.match_id)\
        .filter(Odds.is_boosted == True)\
        .distinct()\
        .limit(5)\
        .all()
    
    for match in boosted_matches:
        print(f"   {match.home_team_name} vs {match.away_team_name}")
    
    session.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    example_queries()
