# D&D Monster Manager

A comprehensive web application for Dungeon Masters to manage their D&D campaigns, including encounters, monsters, NPCs, and loot.

## Features

- **Campaign Management**: Create and manage multiple campaigns
- **Encounter Building**: Design and run combat encounters
- **Monster Database**: Track and customize monsters
- **NPC Management**: Create and manage NPCs with detailed information
- **Loot System**: Track items and treasures for encounters
- **Modern UI**: Dark theme inspired by D&D Beyond

## Technologies Used

- **Backend**: Python/Flask
- **Database**: SQLite/SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dd-monster-manager.git
   cd dd-monster-manager
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

6. Open your browser and navigate to `http://localhost:5000`

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
├── requirements.txt   # Project dependencies
└── README.md         # This file
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