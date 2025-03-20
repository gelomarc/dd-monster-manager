# D&D Monster Manager

A comprehensive web application for Dungeon Masters to manage their D&D campaigns, including encounters, monsters, NPCs, and loot tracking.

## Features

- **Campaign Management**: Create and manage multiple campaigns
- **Encounter Building**: Design and run combat encounters
- **Monster Database**: Track and customize monsters
- **NPC Management**: Create and manage NPCs with detailed information
- **Loot System**: Track items and treasures for encounters
- **OCR Support**: Import character sheets and monster stats using OCR
- **PDF Export**: Generate campaign and encounter reports

## Technologies

- **Backend**: Python/Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **OCR**: Tesseract, PDF processing with pdfkit
- **Deployment**: Gunicorn, Nginx

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dd-monster-manager.git
   cd dd-monster-manager
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create .env file):
   ```
   SECRET_KEY=your-secret-key
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   DATABASE_URL=sqlite:///app.db
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run
   ```

## Production Deployment

### Prerequisites

- Ubuntu 22.04 LTS server
- Domain name pointing to your server
- Python 3.8+
- PostgreSQL
- Nginx
- SSL certificate (Let's Encrypt)

### Server Setup

1. Install required packages:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx postgresql postgresql-contrib
   ```

2. Create PostgreSQL database:
   ```sql
   CREATE DATABASE ddmonsters;
   CREATE USER ddmonster_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ddmonsters TO ddmonster_user;
   ```

3. Set up application:
   ```bash
   # Create application directory
   sudo mkdir /var/www/ddmonsters
   sudo chown $USER:$USER /var/www/ddmonsters

   # Clone repository and setup
   git clone https://github.com/yourusername/ddmonsters.git /var/www/ddmonsters
   cd /var/www/ddmonsters
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure Gunicorn service:
   ```bash
   sudo nano /etc/systemd/system/ddmonsters.service
   ```
   Add:
   ```ini
   [Unit]
   Description=DD Monsters Gunicorn Service
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/ddmonsters
   Environment="PATH=/var/www/ddmonsters/venv/bin"
   EnvironmentFile=/var/www/ddmonsters/.env
   ExecStart=/var/www/ddmonsters/venv/bin/gunicorn -c gunicorn_config.py wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

5. Configure Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/ddmonsters
   ```
   Use the provided nginx_config file content.

6. Enable site and SSL:
   ```bash
   sudo ln -s /etc/nginx/sites-available/ddmonsters /etc/nginx/sites-enabled/
   sudo certbot --nginx -d your-domain.com
   ```

7. Start services:
   ```bash
   sudo systemctl start ddmonsters
   sudo systemctl enable ddmonsters
   sudo systemctl restart nginx
   ```

## OCR Setup

The application includes OCR capabilities for importing character sheets and monster stats. Requirements:

- Tesseract OCR engine
- PDF processing tools (wkhtmltopdf)
- Optional: OpenCV and NumPy for enhanced OCR

Install additional OCR dependencies:
```bash
# On Ubuntu/Debian:
sudo apt install tesseract-ocr wkhtmltopdf
```

## Project Structure

```
dd-monster-manager/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # Route handlers
│   ├── static/         # Static files (CSS, JS)
│   ├── templates/      # HTML templates
│   └── __init__.py     # Application factory
├── migrations/         # Database migrations
├── tests/             # Test files
├── config.py          # Configuration
├── gunicorn_config.py # Gunicorn settings
├── wsgi.py           # WSGI entry point
└── requirements.txt   # Dependencies
```

## Testing

Run the test suite:
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- D&D Beyond for design inspiration
- The D&D community for feature suggestions
- Flask and its extensions for making this possible 