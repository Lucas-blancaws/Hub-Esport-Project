# 🎮 Hub Esport Booking & Management System

Plateforme SaaS de réservation et gestion pour centres gaming esport.

**Projet Portfolio Holberton School C27 - DemoDay 2026**

---

## 📋 Vue d'Ensemble

Application web full-stack permettant la réservation en ligne de stations gaming avec paiement intégré, dashboard administrateur et système de validation par QR Code.

### 🎯 Fonctionnalités Principales

- ✅ **Réservation en ligne** : Calendrier interactif avec disponibilités temps réel
- ✅ **Paiement Stripe** : Checkout Sessions sécurisées (mode TEST)
- ✅ **Dashboard Admin** : Analytics, graphiques d'occupation, gestion du parc PC
- ✅ **Système POS** : Réservations manuelles sur place
- ✅ **QR Code** : Validation d'entrée mobile (scan via Ngrok)
- ✅ **Emails automatiques** : Confirmations + reset password
- ✅ **Responsive** : Interface mobile-first (Bootstrap 5)

---

## 🛠️ Stack Technique

### Backend
- **Python 3.12** - Langage principal
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de données
- **Flask-Login** - Gestion des sessions
- **Alembic** - Migrations BDD

### Frontend
- **HTML5 / CSS3** - Structure et style
- **JavaScript ES6+** - Logique client
- **Bootstrap 5** - Framework CSS responsive
- **FullCalendar.js** - Calendrier de réservation
- **Chart.js** - Graphiques dashboard admin

### Services & APIs
- **Stripe API** - Paiement (Checkout Sessions - Mode TEST)
- **SMTP Gmail** - Envoi d'emails transactionnels
- **Ngrok** - Tests mobile cross-device

---

## 📁 Structure du Projet

```
hub-esport-booking/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py          # Login, Register, Reset Password
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py          # Réservations, Admin, API
│   ├── services/
│   │   ├── email_service.py   # Envoi emails (SMTP)
│   │   ├── payment_service.py # Stripe Checkout Sessions
│   │   ├── reservation_service.py
│   │   └── station_service.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── img/
│   │       └── hero-bg.jpg
│   ├── templates/
│   │   ├── auth/              # Login, Register, Reset
│   │   ├── main/              # Booking, Dashboard, Success
│   │   └── base.html
│   ├── __init__.py            # Factory pattern
│   └── models.py              # User, Station, Reservation
├── migrations/                # Alembic DB migrations
├── venv/                      # Virtual environment
├── .env                       # Variables d'environnement
├── .gitignore
├── config.py                  # Configuration Flask
├── README.md
├── requirements.txt
└── run.py                     # Point d'entrée
```

---

## 🚀 Installation & Setup

### Prérequis
- Python 3.12+
- PostgreSQL
- Compte Stripe (mode TEST)
- Compte Cloudinary
- Compte Gmail (SMTP)

### 1. Cloner le repository
```bash
git clone https://github.com/Lucas-blancaws/Hub-Esport-Project.git
cd Hub-Esport-Project
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OU
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` :
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://localhost/hub_esport_db

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Initialiser la base de données
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Lancer l'application
```bash
flask run
```

Application disponible sur : `http://localhost:5000`

---

## 🧪 Tests

### Tests API avec Postman
3 endpoints validés :
- `GET /api/reservations` - Liste des réservations
- `GET /api/availability` - Disponibilités par station/date
- `POST /reserve` - Création réservation (authentifié)

### Tests Stripe
- Mode TEST : Carte `4242 4242 4242 4242`
- Expiration : N'importe quelle date future
- CVC : N'importe quel 3 chiffres

### Tests Mobile (Ngrok)
```bash
ngrok http 5000
```
Accès via URL Ngrok pour scan QR Code mobile.

---

## 📊 Architecture

### Pattern MVC avec Services
```
Routes (Controllers)
    ↓
Services (Business Logic)
    ↓
Models (Data Layer)
```

### Algorithme Anti-Double Booking
```python
# Détection mathématique de conflits temporels
conflicts = Reservation.query.filter(
    Reservation.station_id == station_id,
    Reservation.start_time < end_time,
    Reservation.end_time > start_time
).count()
```
**Complexité : O(1)** grâce aux index SQL.

---

## 🔐 Sécurité

- ✅ Mots de passe hashés (Werkzeug)
- ✅ Sessions Flask sécurisées
- ✅ Protection CSRF (Flask-WTF)
- ✅ SQLAlchemy ORM (prévention SQL injection)
- ✅ Stripe PCI-DSS compliant

---

## 📈 Roadmap Production

**Limitations MVP actuelles :**
- Stripe en mode TEST (paiements fictifs)
- Flux synchrone `/payment/success` (pas de gestion asynchrone)
- Flask development server (pas production-ready)

**Production future :**
- [ ] Déploiement Gunicorn + Nginx
- [ ] Stripe mode LIVE + système de confirmation robuste
- [ ] CI/CD avec GitHub Actions
- [ ] Tests automatisés (Pytest + Selenium)
- [ ] Monitoring & logging (Sentry)

---

## 👨‍💻 Auteur

**Lucas Blanc-Portier**  
Étudiant Holberton School - Cohort C27  
Projet Portfolio (DemoDay) - Mars 2026

**Hub Esport Bordeaux** - Co-fondateur & Initiateur  
Associés : Mohamed & Adrien | Mentor : Tewfik

---

## 📜 Licence

Ce projet est développé dans le cadre du programme Holberton School.

---

## 🙏 Remerciements

- Holberton School pour l'encadrement
- Stripe pour la documentation API
- Bootstrap & FullCalendar pour les librairies open-source