# Web Editor

The `edhelper` web editor provides a modern web interface for building and managing Commander decks. It includes a FastAPI backend and a React frontend.

> **Note**: The editor is currently under development. The backend API is designed to be used exclusively by the frontend application and should not be accessed directly.

## Installation

The editor is included in the full installation:

```bash
pip install edhelper[all]
```

## Starting the Editor

```bash
edhelper start-editor
```

This will:
1. Start the FastAPI backend server on `http://0.0.0.0:3839`
2. Open your default browser to the editor interface

> **Note**: The frontend is still under development. The backend will be available, but the full web interface may not be functional yet.

## Architecture

The editor consists of:

- **Backend** (`editor/backend/`): FastAPI REST API that handles all deck and card operations
- **Frontend** (`editor/frontend/`): React application (under development) that provides the web interface

The backend API is **not intended for direct use**. It is designed to be consumed exclusively by the frontend application. All interactions should go through the web interface once it's complete.

## Planned Features

Once the frontend is complete, the editor will provide:

- **Deck List View**: Browse all your decks
- **Deck Builder**: Add/remove cards, set commander
- **Card Search**: Search and browse cards with autocomplete
- **Meta Suggestions**: Get EDHREC recommendations for commanders
- **Export Options**: Export decks in various formats (TXT, CSV, JSON)
- **Real-time Updates**: Changes are immediately reflected
- **Modern UI**: Clean and intuitive interface

## Development

### Backend

The backend uses FastAPI and is located in `editor/backend/`. It provides RESTful endpoints for:

- Deck management (CRUD operations)
- Card operations (search, find, top commanders)
- Commander meta data from EDHREC
- Export functionality

### Frontend

The frontend is a React application located in `editor/frontend/`. It's currently under development.

```bash
cd editor/frontend
npm install
npm run dev
```

## Current Status

- ✅ Backend API: Complete and functional
- 🚧 Frontend: Under development
- ⏳ Full Integration: Pending frontend completion

## Troubleshooting

### Port Already in Use

If port 3839 is already in use, you can modify the port in `main.py`:

```python
BACKEND_CMD = [
    "uvicorn",
    "editor.backend.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8080",  # Change port here
]
```

### Browser Doesn't Open

If the browser doesn't open automatically, navigate to:
```
http://localhost:3839
```

> **Note**: Until the frontend is complete, you may see a basic page or API documentation.

## Using the Editor

Once the frontend is complete, you'll be able to:

1. Start the editor with `edhelper start-editor`
2. Access the web interface in your browser
3. Manage decks through the graphical interface
4. Search and add cards visually
5. Get meta suggestions for commanders
6. Export decks in various formats

For now, use the CLI or shell for deck management.

