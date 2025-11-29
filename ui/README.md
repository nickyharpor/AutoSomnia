# AutoSomnia UI

React.js dashboard for AutoSomnia AI Trading Platform.

## 🏗️ Project Structure

```
ui/
├── src/
│   ├── components/          # Reusable components
│   │   ├── common/         # Common UI components (Button, Card, Table)
│   │   └── layout/         # Layout components (Header, Sidebar, Layout)
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx   # Main dashboard
│   │   ├── Users.jsx       # User management
│   │   ├── Trades.jsx      # Trade history
│   │   ├── Analytics.jsx   # Analytics & charts
│   │   └── Settings.jsx    # Settings page
│   ├── services/           # API services
│   │   ├── api.js          # Axios instance & interceptors
│   │   ├── userService.js  # User API calls
│   │   ├── tradeService.js # Trade API calls
│   │   └── accountService.js # Account API calls
│   ├── hooks/              # Custom React hooks
│   │   └── useApi.js       # API hook for data fetching
│   ├── utils/              # Utility functions
│   │   └── formatters.js   # Formatting helpers
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── .env.example            # Environment variables template
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```
VITE_API_URL=http://localhost:8000
VITE_TELEGRAM_BOT_NAME=autosomnia_bot
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## 📁 Key Features

### Authentication

- **Telegram Login**: Secure authentication via Telegram Login Widget
- **Protected Routes**: Automatic redirect for unauthenticated users
- **Session Management**: Token-based authentication with localStorage
- **User Context**: Global authentication state management

### Components

- **Layout Components**: Sidebar navigation, Header with notifications
- **Common Components**: Reusable Button, Card, Table components
- **Auth Components**: Telegram login button, protected routes
- **Responsive Design**: Mobile-friendly layout
- **Dark Mode**: Full dark mode support with toggle and persistence

### Pages

- **Dashboard**: Overview with stats and recent activity
- **Users**: User management with auto-exchange toggle
- **Trades**: Trade history with filtering
- **Analytics**: Charts and performance metrics
- **Settings**: Configuration management

### Services

- **API Layer**: Centralized API calls with Axios
- **Interceptors**: Request/response handling
- **Error Handling**: Automatic error management

### Hooks

- **useApi**: Custom hook for API calls with loading/error states

## 🎨 Styling

- CSS Modules for component-specific styles
- CSS Variables for theming
- Responsive design with mobile-first approach

## 🔧 Configuration

### Vite Config

- React plugin enabled
- Proxy configured for API calls (`/api` → `http://localhost:8000`)
- Port: 3000

### ESLint

- React recommended rules
- React Hooks rules
- React Refresh plugin

### Prettier

- Single quotes
- No semicolons
- 2 space indentation
- 100 character line width

## 📡 API Integration

The UI connects to the FastAPI backend at `http://localhost:8000`.

### Available Services

- **userService**: User CRUD operations
- **tradeService**: Trade history and statistics
- **accountService**: Account management

### Example Usage

```javascript
import { userService } from './services/userService'

// Get all users
const users = await userService.getUsers()

// Enable auto-exchange
await userService.enableAutoExchange(userId)
```

## 🎯 Best Practices

### Component Structure

```javascript
import { useState } from 'react'
import './Component.css'

const Component = ({ prop1, prop2 }) => {
  const [state, setState] = useState(null)

  return (
    <div className="component">
      {/* Component content */}
    </div>
  )
}

export default Component
```

### API Calls with useApi Hook

```javascript
import useApi from '../hooks/useApi'
import { userService } from '../services/userService'

const Component = () => {
  const { data, loading, error, refetch } = useApi(
    userService.getUsers,
    null,
    true // immediate execution
  )

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return <div>{/* Render data */}</div>
}
```

## 🔐 Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `VITE_TELEGRAM_BOT_NAME`: Your Telegram bot username (e.g., `autosomnia_bot`)

## 🔒 Authentication

The app uses Telegram Login Widget for secure authentication with HMAC-SHA-256 verification.

**📚 Complete Documentation:** See [TELEGRAM_AUTH_INDEX.md](../private/TELEGRAM_AUTH_INDEX.md) for all guides

**Quick Links:**
- 🚀 [QUICK_START.md](../private/QUICK_START.md) - Get started in 5 minutes
- 💻 [BACKEND_AUTH_SETUP.md](../private/BACKEND_AUTH_SETUP.md) - Backend implementation
- 📋 [AUTH_QUICK_REFERENCE.md](../private/AUTH_QUICK_REFERENCE.md) - Quick reference card
- 🔄 [AUTH_FLOW_DIAGRAM.md](../private/AUTH_FLOW_DIAGRAM.md) - Visual flow diagrams

**Quick Setup:**
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Set bot username in `.env` file: `VITE_TELEGRAM_BOT_NAME=your_bot`
3. Implement backend verification endpoint (see BACKEND_AUTH_SETUP.md)
4. Users can login with their Telegram account

**Status:** ✅ Frontend complete | ⏳ Backend pending

## 📦 Dependencies

### Core

- **react**: ^18.2.0
- **react-dom**: ^18.2.0
- **react-router-dom**: ^6.20.0

### UI & Utilities

- **axios**: ^1.6.2 - HTTP client
- **recharts**: ^2.10.3 - Charts library
- **lucide-react**: ^0.294.0 - Icon library

### Dev Dependencies

- **vite**: ^5.0.8 - Build tool
- **@vitejs/plugin-react**: ^4.2.1 - React plugin
- **eslint**: ^8.55.0 - Linting
- **prettier**: ^3.1.1 - Code formatting

## 🚧 Future Enhancements

- [ ] Real-time updates with WebSocket
- [ ] Advanced filtering and search
- [ ] Export data functionality
- [x] Dark mode support ✅
- [x] Telegram authentication ✅
- [ ] Advanced charts with Recharts
- [ ] Notifications system
- [ ] Mobile app (React Native)
- [ ] Role-based access control

## 📝 Notes

- This is a skeleton structure with minimal implementation
- Components are ready for integration with backend APIs
- Styling follows a clean, modern design system
- All components are functional components with hooks
- Responsive design included

## 🤝 Contributing

1. Follow the existing code structure
2. Use functional components with hooks
3. Keep components small and focused
4. Write clean, readable code
5. Use CSS modules for styling

## 📄 License

Part of the AutoSomnia project.
