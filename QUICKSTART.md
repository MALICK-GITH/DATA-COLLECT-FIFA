# ⚡ Démarrage Rapide - 5 Minutes

Guide rapide pour déployer le système de sauvegarde de matchs avec cron-job.org.

## 🎯 Option la plus simple: Render + cron-job.org (GRATUIT)

### Étape 1: Déployer sur Render (3 minutes)

1. Allez sur [render.com](https://render.com) et créez un compte
2. Cliquez sur "New +" → "Web Service"
3. Connectez votre compte GitHub ou uploadez les fichiers
4. Configurez:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Ajoutez les variables d'environnement:
   - `DB_TYPE=sqlite`
   - `SQLITE_PATH=/var/data/match_history.db`
   - `LOG_LEVEL=INFO`
6. Cliquez sur "Deploy Web Service"
7. Attendez 2-3 minutes, Render vous donnera une URL comme: `https://match-saver.onrender.com`

### Étape 2: Configurer cron-job.org (2 minutes)

1. Allez sur [cron-job.org](https://cron-job.org) et créez un compte
2. Cliquez sur "Cronjobs" → "Create cronjob"
3. Remplissez:
   - **Title**: Match Saver
   - **URL**: `https://match-saver.onrender.com/trigger`
   - **Schedule**: Every minute
   - **Method**: GET
4. Cliquez sur "Create"
5. Activez le cron job (toggle switch)

### Étape 3: Tester (30 secondes)

```bash
# Testez l'endpoint
curl https://match-saver.onrender.com/trigger

# Devrait retourner:
# {"success": true, "message": "Match scraping completed", ...}
```

### Étape 4: Vérifier les statistiques (après quelques minutes)

```bash
curl https://match-saver.onrender.com/stats
```

## ✅ C'est tout!

Le système fonctionne maintenant:
- ✅ Chaque minute, cron-job.org appelle votre URL
- ✅ L'application interroge l'API 888starz.bet
- ✅ Les matchs terminés sont sauvegardés automatiquement
- ✅ Vous pouvez vérifier les statistiques à tout moment

## 📊 Endpoints disponibles

- `https://votre-url.com/` - Info du service
- `https://votre-url.com/trigger` - Déclenche le scraping
- `https://votre-url.com/stats` - Statistiques de la base
- `https://votre-url.com/health` - Health check
- `https://votre-url.com/test` - Test sans sauvegarde

## 🔧 Personnalisation

Pour changer les paramètres de l'API, éditez `config.py`:

```python
DEFAULT_SPORTS = 85  # ID du sport (85 = FIFA)
DEFAULT_COUNT = 100  # Nombre de matchs
DEFAULT_LNG = "fr"   # Langue
DEFAULT_MODE = 4     # Mode
```

## 📝 Fichiers importants

- `app.py` - Application Flask principale
- `scraper.py` - Scraper de l'API
- `database.py` - Gestion de la base de données
- `config.py` - Configuration
- `requirements.txt` - Dépendances

## 🚨 Problèmes?

### L'URL ne répond pas
- Vérifiez que Render a bien déployé (dashboard)
- Attendez quelques minutes pour le premier déploiement
- Vérifiez les logs dans Render

### Aucun match n'est sauvegardé
- Vérifiez que l'API 888starz a des matchs terminés
- Testez avec `/test` endpoint
- Vérifiez les logs dans Render

### Cron job échoue
- Vérifiez l'URL dans cron-job.org
- Testez l'URL manuellement avec curl
- Vérifiez les logs de cron-job.org

## 📚 Documentation complète

Pour plus de détails, voir:
- `README_WEBHOOK.md` - Guide de déploiement complet
- `README.md` - Documentation du projet

---

**Fait! Votre système est opérationnel en 5 minutes.**

*SOLITAIRE HACK*
