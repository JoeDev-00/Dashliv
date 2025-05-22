# Système de Gestion de Livraison

Un système complet de gestion de livraison développé avec Django, permettant de suivre les colis en temps réel, de gérer les commandes et d'évaluer les services.

## Fonctionnalités

- **Gestion des utilisateurs** : Clients, livreurs et administrateurs
- **Création et suivi des commandes** : Interface intuitive pour créer et suivre les commandes
- **Cartographie interactive** : Intégration avec Google Maps API pour le suivi en temps réel
- **Notifications** : Alertes par email, SMS et dans l'application
- **Tableaux de bord** : Interfaces dédiées pour les clients et les livreurs
- **Système d'évaluation** : Notation et commentaires sur les livraisons

## Installation

1. Cloner le dépôt
   \`\`\`bash
   git clone https://github.com/votre-nom/livraison-system.git
   cd livraison-system
   \`\`\`

2. Créer un environnement virtuel
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   \`\`\`

3. Installer les dépendances
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Configurer les variables d'environnement
   - Créer un fichier `.env` à la racine du projet
   - Ajouter les variables suivantes:
     \`\`\`
     SECRET_KEY=votre_cle_secrete
     DEBUG=True
     GOOGLE_MAPS_API_KEY=votre_cle_api_google_maps
     EMAIL_HOST_USER=votre_email@gmail.com
     EMAIL_HOST_PASSWORD=votre_mot_de_passe
     TWILIO_ACCOUNT_SID=votre_account_sid
     TWILIO_AUTH_TOKEN=votre_auth_token
     TWILIO_PHONE_NUMBER=votre_numero_twilio
     \`\`\`

5. Effectuer les migrations
   \`\`\`bash
   python manage.py makemigrations
   python manage.py migrate
   \`\`\`

6. Créer un superutilisateur
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

7. Lancer le serveur
   \`\`\`bash
   python manage.py runserver
   \`\`\`

## Structure du projet

- **users** : Gestion des utilisateurs et des profils
- **orders** : Création et gestion des commandes
- **tracking** : Suivi des livraisons en temps réel
- **dashboard** : Tableaux de bord pour clients et livreurs
- **ratings** : Système d'évaluation du service
- **notifications** : Système de notifications

## Technologies utilisées

- **Backend** : Django
- **Frontend** : HTML, CSS, JavaScript, Bootstrap
- **Base de données** : SQLite (développement), PostgreSQL (production)
- **Cartographie** : Google Maps API
- **Notifications** : Emails (SMTP), SMS (Twilio)

## Déploiement

Pour déployer l'application en production:

1. Configurer les paramètres de production dans `settings.py`
2. Utiliser une base de données PostgreSQL
3. Configurer un serveur web comme Nginx ou Apache
4. Utiliser Gunicorn comme serveur WSGI
5. Configurer les certificats SSL pour HTTPS

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
