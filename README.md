# 🏆 Match Saver - Cron Job Service

Service automatique pour sauvegarder les matchs terminés du live feed dans une base de données.

## 📋 Fonctionnalités

- ✅ Récupération automatique des matchs depuis le nouvel endpoint live feed
- ✅ Filtrage des matchs terminés (status FINISHED)
- ✅ Sauvegarde dans une base de données (SQLite ou PostgreSQL)
- ✅ Conservation des cotes et scores finaux
- ✅ Exécution automatique via cron job
- ✅ Logging complet des opérations
- ✅ Statistiques de la base de données

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Étapes

1. **Cloner ou télécharger le projet**
```bash
cd cron_job_match_saver
```

2. **Exécuter le script d'installation**
```bash
bash setup.sh
```

Ou manuellement:

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env (copier l'exemple et configurer)
cp .env.example .env

# Créer les tables de la base de données
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_tables()"
```

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Type de base de données: sqlite ou postgresql
DB_TYPE=sqlite

# Configuration SQLite
SQLITE_PATH=match_history.db

# Configuration PostgreSQL (si DB_TYPE=postgresql)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=match_history
DB_USER=postgres
DB_PASSWORD=your_password

# Schedule cron (format standard cron)
CRON_SCHEDULE=*/5 * * * *

# Niveau de logging: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Fichier de log
LOG_FILE=match_saver.log
```

## 🎯 Utilisation

### Exécution unique

Pour exécuter le scraper une fois:

```bash
python scraper.py
```

### Service continu

Pour lancer le service qui s'exécute toutes les 5 minutes:

```bash
python cron_service.py
```

### Configuration du Cron Job

Voir `cron_setup.txt` pour les instructions détaillées selon votre système.

#### Linux/Mac - Crontab
```bash
crontab -e
```

Ajouter:
```
*/5 * * * * cd /path/to/cron_job_match_saver && python scraper.py >> match_saver.log 2>&1
```

#### Windows - Task Scheduler
Créer une tâche planifiée qui exécute `scraper.py` toutes les 5 minutes.

## 📊 Structure de la Base de Données

### Table `matches`
- Informations sur les matchs
- Équipes, scores, dates
- Statut du match

### Table `odds`
- Cotes principales
- Types de paris
- Groupes de paris

### Table `additional_odds`
- Cotes additionnelles
- Handicaps, over/under
- Marchés spéciaux

## 🔍 Monitoring

### Voir les logs
```bash
tail -f match_saver.log
```

### Statistiques de la base de données
```bash
python -c "from database import DatabaseManager; db = DatabaseManager(); print(db.get_match_stats())"
```

### Voir les matchs terminés
```python
from database import DatabaseManager

db = DatabaseManager()
matches = db.get_finished_matches(limit=10)
for match in matches:
    print(f"{match.home_team_name} {match.home_score} - {match.away_score} {match.away_team_name}")
```

## 🛠️ Personnalisation

### Modifier les paramètres de l'API

Éditer `config.py`:

```python
DEFAULT_SPORTS = 85  # ID du sport
DEFAULT_COUNT = 100  # Nombre de matchs à récupérer
DEFAULT_LNG = "fr"   # Langue
DEFAULT_MODE = 4     # Mode de l'API
```

### Changer la fréquence du cron

Dans `cron_service.py`:

```python
# Toutes les 5 minutes
schedule.every(5).minutes.do(self.job)

# Toutes les heures
schedule.every().hour.do(self.job)

# Tous les jours à minuit
schedule.every().day.at("00:00").do(self.job)
```

## 📈 Exemples de Requêtes

### Python

```python
from database import DatabaseManager, Match

db = DatabaseManager()
session = db.get_session()

# Tous les matchs terminés
matches = session.query(Match).filter(Match.status == 'FINISHED').all()

# Matchs avec un score spécifique
matches = session.query(Match).filter(
    Match.status == 'FINISHED',
    Match.home_score > 3
).all()

# Matchs d'une ligue spécifique
matches = session.query(Match).filter(
    Match.league_name.like('%Superligue%')
).all()

session.close()
```

### SQL

```sql
-- Matchs terminés avec score élevé
SELECT * FROM matches 
WHERE status = 'FINISHED' 
AND (home_score + away_score) > 5
ORDER BY finish_time DESC
LIMIT 10;

-- Statistiques par ligue
SELECT league_name, COUNT(*) as total_matches,
       AVG(home_score + away_score) as avg_goals
FROM matches
WHERE status = 'FINISHED'
GROUP BY league_name
ORDER BY total_matches DESC;
```

## 🔒 Sécurité

- Ne pas commit le fichier `.env`
- Utiliser des mots de passe forts pour PostgreSQL
- Limiter les accès à la base de données
- Surveiller les logs pour activités suspectes

## 🐛 Dépannage

### Erreur de connexion à l'API
- Vérifier la connexion internet
- Vérifier que l'URL de l'API est correcte
- Consulter les logs pour plus de détails

### Erreur de base de données
- Vérifier que les tables sont créées
- Vérifier les permissions de fichier (SQLite)
- Vérifier la configuration PostgreSQL

### Cron job ne s'exécute pas
- Vérifier le chemin absolu dans le crontab
- Vérifier les permissions d'exécution
- Consulter les logs système

## 📝 Licence

Ce projet est créé à des fins éducatives et de démonstration.

## 👤 Auteur

SOLITAIRE HACK

---

**Note:** Ce service utilise l'API 888starz.bet de manière non officielle. Respectez les conditions d'utilisation et les lois locales.
