# 🌐 Webhook Cron Job - Guide de Déploiement

Guide complet pour déployer le service de sauvegarde de matchs avec un webhook HTTP utilisable sur cron-job.org ou similaire.

## 📋 Concept

Le système fonctionne ainsi:
1. **Application Web Flask** - Hébergée sur un serveur (gratuit ou payant)
2. **Endpoint HTTP** - URL publique qui déclenche le scraping
3. **Service Cron Job** - Appelle l'URL chaque minute
4. **Sauvegarde automatique** - Les matchs terminés sont sauvegardés en base de données

```
┌─────────────────┐
│  cron-job.org   │
│  (chaque minute)│
└────────┬────────┘
         │ HTTP GET
         ▼
┌─────────────────┐
│  Flask App      │
│  /trigger      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  888starz API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Base de Données│
│  (SQLite/PG)    │
└─────────────────┘
```

## 🚀 Options de Déploiement

### Option 1: Render.com (Gratuit) - RECOMMANDÉ

Render offre un hébergement gratuit avec SSL automatique.

#### Étapes:

1. **Créer un compte sur [render.com](https://render.com)**

2. **Créer un nouveau Web Service**
   - Connectez votre repository GitHub
   - Ou utilisez le déploiement direct avec les fichiers

3. **Configuration du Build**
   ```
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Variables d'environnement**
   Ajoutez dans le dashboard Render:
   ```
   DB_TYPE=sqlite
   SQLITE_PATH=/var/data/match_history.db
   LOG_LEVEL=INFO
   LOG_FILE=/var/logs/match_saver.log
   ```

5. **Déployer**
   - Cliquez sur "Deploy"
   - Attendez le déploiement (2-3 minutes)
   - Render vous donnera une URL comme: `https://match-saver.onrender.com`

6. **Votre endpoint webhook sera:**
   ```
   https://match-saver.onrender.com/trigger
   ```

### Option 2: Railway.app (Gratuit)

Railage est une alternative populaire avec un déploiement facile.

#### Étapes:

1. **Créer un compte sur [railway.app](https://railway.app)**

2. **Nouveau projet**
   - Importez depuis GitHub ou déposez les fichiers

3. **Configuration**
   - Railway détectera automatiquement Python
   - Ajoutez les variables d'environnement

4. **Déployer**
   - Railway vous donnera une URL publique

### Option 3: PythonAnywhere (Gratuit)

PythonAnywhere est spécialisé pour Python.

#### Étapes:

1. **Créer un compte sur [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Créer un nouveau Web App**
   - Choisissez Python 3.10+
   - Framework: Flask

3. **Uploader les fichiers**
   - Utilisez l'interface web ou git

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurer le WSGI**
   - Pointez vers `app.py`

6. **Votre URL sera:**
   ```
   https://votre-username.pythonanywhere.com/trigger
   ```

### Option 4: Serveur VPS (Payant)

Pour plus de contrôle, utilisez un VPS.

#### Étapes:

1. **Louer un VPS** (DigitalOcean, Linode, Hetzner)

2. **Installer les dépendances**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

3. **Cloner/déposer les fichiers**

4. **Installer les dépendances Python**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Configurer Nginx comme reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name votre-domaine.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. **Démarrer avec Gunicorn**
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

7. **Configurer SSL avec Let's Encrypt**
   ```bash
   sudo certbot --nginx
   ```

## ⚙️ Configuration du Cron Job

### Sur cron-job.org (Gratuit)

1. **Créer un compte sur [cron-job.org](https://cron-job.org)**

2. **Créer un nouveau cron job**
   - Title: Match Saver
   - URL: `https://votre-url.com/trigger`
   - Schedule: Every minute
   - Method: GET

3. **Activer le cron job**

4. **Vérifier les logs** dans le dashboard de cron-job.org

### Sur EasyCron (Gratuit)

1. **Créer un compte sur [easycron.com](https://www.easycron.com)**

2. **Créer un cron job**
   - URL: `https://votre-url.com/trigger`
   - Execution: Every 1 minute
   - Method: GET

3. **Sauvegarder et activer**

### Sur Cronitor (Payant mais plus avancé)

1. **Créer un compte sur [cronitor.io](https://cronitor.io)**

2. **Créer un monitor**
   - URL: `https://votre-url.com/trigger`
   - Schedule: * * * * *

3. **Copier l'URL du monitor**

## 🧪 Tester le Système

### 1. Tester localement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer les tables
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_tables()"

# Lancer l'application
python app.py
```

L'application sera accessible sur: `http://localhost:5000`

### 2. Tester les endpoints

```bash
# Test home
curl http://localhost:5000/

# Test trigger (sans sauvegarder)
curl http://localhost:5000/test

# Test trigger (avec sauvegarde)
curl http://localhost:5000/trigger

# Test stats
curl http://localhost:5000/stats

# Test health
curl http://localhost:5000/health
```

### 3. Tester en production

Une fois déployé:

```bash
# Test le webhook
curl https://votre-url.com/trigger

# Vérifier la réponse
# Devrait retourner:
# {
#   "success": true,
#   "message": "Match scraping completed",
#   "stats": {...}
# }
```

## 📊 Monitoring

### Vérifier les logs

Sur votre serveur:

```bash
# Si vous utilisez Render/Railway
# Vérifiez les logs dans le dashboard

# Si vous utilisez PythonAnywhere
# Vérifiez les logs dans l'interface web

# Si vous utilisez un VPS
tail -f match_saver.log
```

### Vérifier la base de données

```python
from database import DatabaseManager

db = DatabaseManager()
stats = db.get_match_stats()
print(stats)
```

### Endpoint de monitoring

```bash
# Statistiques
curl https://votre-url.com/stats

# Health check
curl https://votre-url.com/health
```

## 🔒 Sécurité

### 1. Ajouter une clé secrète (optionnel)

Si vous voulez sécuriser l'endpoint:

```python
# Dans app.py
@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    # Vérifier la clé secrète
    secret_key = request.args.get('key')
    if secret_key != Config.SECRET_KEY:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    # ... reste du code
```

Configuration dans `.env`:
```
SECRET_KEY=votre_clé_secrète_ici
```

URL du cron job:
```
https://votre-url.com/trigger?key=votre_clé_secrète_ici
```

### 2. Limiter par IP (optionnel)

```python
# Dans app.py
ALLOWED_IPS = ['1.2.3.4', '5.6.7.8']  # IPs de cron-job.org

@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    if request.remote_addr not in ALLOWED_IPS:
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    
    # ... reste du code
```

## 📝 Exemple Complet

### Déploiement sur Render + cron-job.org

1. **Déployer sur Render**
   - URL obtenue: `https://match-saver.onrender.com`

2. **Configurer cron-job.org**
   - URL: `https://match-saver.onrender.com/trigger`
   - Schedule: Every minute
   - Activer

3. **Tester**
   ```bash
   curl https://match-saver.onrender.com/trigger
   ```

4. **Vérifier après quelques minutes**
   ```bash
   curl https://match-saver.onrender.com/stats
   ```

5. **Résultat attendu**
   ```json
   {
     "success": true,
     "stats": {
       "total": 45,
       "finished": 42,
       "cancelled": 2,
       "other": 1
     }
   }
   ```

## 🚨 Dépannage

### Problème: L'endpoint ne répond pas

**Solutions:**
- Vérifiez que l'application est en cours d'exécution
- Vérifiez les logs du serveur
- Vérifiez que le port est ouvert
- Testez avec curl localement

### Problème: Aucun match n'est sauvegardé

**Solutions:**
- Vérifiez que l'API 888starz répond
- Vérifiez les logs pour les erreurs
- Testez l'endpoint `/test` pour voir si des matchs sont disponibles
- Vérifiez que la base de données est accessible

### Problème: Cron job échoue

**Solutions:**
- Vérifiez l'URL dans cron-job.org
- Vérifiez que l'URL est accessible publiquement
- Vérifiez les logs de cron-job.org
- Essayez manuellement avec curl

### Problème: Base de données SQLite verrouillée

**Solutions:**
- Utilisez PostgreSQL pour la production
- Assurez-vous qu'une seule instance s'exécute
- Vérifiez les permissions du fichier

## 📚 Ressources

- [Render.com](https://render.com) - Hébergement gratuit
- [Railway.app](https://railway.app) - Hébergement gratuit
- [PythonAnywhere](https://www.pythonanywhere.com) - Hébergement Python gratuit
- [cron-job.org](https://cron-job.org) - Service cron gratuit
- [EasyCron](https://www.easycron.com) - Service cron gratuit

---

## ✅ Checklist de Déploiement

- [ ] Choisir un hébergeur (Render recommandé)
- [ ] Créer un compte sur l'hébergeur
- [ ] Uploader les fichiers
- [ ] Configurer les variables d'environnement
- [ ] Déployer l'application
- [ ] Tester l'endpoint `/trigger`
- [ ] Créer un compte sur cron-job.org
- [ ] Configurer le cron job avec l'URL
- [ ] Activer le cron job
- [ ] Attendre quelques minutes
- [ ] Vérifier les statistiques avec `/stats`
- [ ] Surveiller les logs

---

**Note:** Ce système est conçu pour fonctionner 24/7 avec un hébergement gratuit. Les services comme Render ont des limitations (sleep après inactivité), mais le cron job réveillera l'application à chaque appel.

*SOLITAIRE HACK*
