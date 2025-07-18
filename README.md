# League Win Rate Friend Tracker

A comprehensive application that allows users to track League of Legends win rate percentages when playing with specific combinations of friends.

## Features

- **Friend Management**: Add, remove, and track friends by Riot ID or PUUID
- **Dynamic Analysis Tiles**: Create multiple dashboard tiles to track different friend combinations
- **Flexible Filtering**: Filter matches by exact player presence or inclusive presence
- **Cross-Player Analysis**: Analyze how other players perform together
- **Visual Analytics**: Charts, graphs, and UI tiles showing win rates
- **Real-time Updates**: Refresh match data from Riot API
- **Persistent Storage**: Save and restore analysis tiles

## Tech Stack

- **Backend**: Python Django with Django REST Framework
- **Frontend**: TypeScript React with Material-UI
- **Database**: PostgreSQL
- **Charts**: Recharts
- **Containerization**: Docker & Docker Compose
- **API**: Riot Games API integration

## Quick Start

1. **Clone the repository**
2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Riot API key
   ```
3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```
4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Riot Games API Key (https://developer.riotgames.com/)

### Environment Variables
Create a `.env` file with:
```
RIOT_API_KEY=your_riot_api_key_here
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://user:password@db:5432/league_tracker
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user

### Friends
- `GET /api/friends/` - Get user's friends
- `POST /api/friends/` - Add new friend
- `DELETE /api/friends/{id}/` - Remove friend

### Matches
- `GET /api/matches/{puuid}/` - Get stored matches
- `POST /api/matches/refresh/{puuid}/` - Refresh matches from Riot API

### Tiles
- `GET /api/tiles/` - Get user's analysis tiles
- `POST /api/tiles/` - Create new analysis tile
- `PUT /api/tiles/{id}/` - Update tile
- `DELETE /api/tiles/{id}/` - Delete tile

## Project Structure

```
LeagueWinRateFriendTracker/
├── backend/                 # Django backend
│   ├── league_tracker/     # Main Django project
│   ├── api/               # REST API app
│   ├── core/              # Core models and utilities
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Docker orchestration
├── .env.example          # Environment template
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 