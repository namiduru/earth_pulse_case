# Frontend App

A modern file management app built with Svelte and TypeScript.

## 🚀 Quick Start

### Docker (Recommended)

```bash
# From project root, run:
docker-up.bat          # Windows
./docker-up.sh         # Unix/Linux/Mac
```

### Manual Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Open http://localhost:5173
```

## 📁 What's Inside

```
frontend/
├── src/
│   ├── components/     # UI components
│   ├── lib/           # API calls
│   ├── stores/        # State management
│   ├── routes/        # Pages
│   └── types/         # TypeScript types
├── package.json       # Dependencies
└── tailwind.config.js # Styling
```

## 🛠️ Development

```bash
npm run dev      # Start development
npm run build    # Build for production
npm run check    # Type checking
npm run lint     # Code linting
```

## 🎨 Features

- **Drag & Drop** file upload
- **File management** (upload, download, delete)
- **Responsive design** with Tailwind CSS
- **TypeScript** for better code quality
- **Real-time updates** with Svelte stores

## 🔧 Environment

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

**Note**: For Docker deployment, environment variables are automatically synced from `backend/.env` file.

## 🧪 Testing

```bash
npm test
```

That's it! Simple and clean. 🎉
