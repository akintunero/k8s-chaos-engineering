# Chaos Engineering Web UI

Modern web dashboard for managing Kubernetes chaos engineering experiments.

## Features

- 🎯 **Dashboard** - Overview of experiments and metrics
- 🧪 **Experiment Management** - Run, stop, and monitor experiments
- ⏰ **Scheduling** - Create and manage scheduled experiments
- 📊 **Real-time Updates** - WebSocket-based live status updates
- 🎨 **Modern UI** - Beautiful, responsive interface built with React and Tailwind CSS

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + WebSockets
- **Charts**: Recharts

## Quick Start

### Development

1. **Start Backend**:
```bash
cd web/backend
pip install -r requirements.txt
python main.py
```

2. **Start Frontend**:
```bash
cd web/frontend
npm install
npm run dev
```

3. **Access UI**: http://localhost:3000

### Docker

```bash
cd web
docker-compose up
```

## API Endpoints

- `GET /api/experiments` - List available experiments
- `GET /api/experiments/running` - List running experiments
- `POST /api/experiments/run` - Run an experiment
- `POST /api/experiments/{name}/stop` - Stop an experiment
- `GET /api/experiments/{name}/status` - Get experiment status
- `GET /api/schedules` - List scheduled experiments
- `POST /api/schedules` - Create a schedule
- `DELETE /api/schedules/{name}` - Delete a schedule
- `WS /ws` - WebSocket for real-time updates

## Screenshots

The UI includes:
- Clean, modern design
- Responsive layout
- Real-time experiment status
- Easy experiment management
- Schedule management interface
