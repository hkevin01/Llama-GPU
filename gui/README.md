# Project Progress Tracker - GUI Application

A modern, interactive React-based project management dashboard with real-time progress tracking, task management, and data visualization.

## Features

- 📊 **Interactive Dashboard** - Real-time charts and metrics
- ✅ **Task Management** - Create, edit, and track tasks with modal forms
- 🔔 **Notification System** - Real-time updates and notifications
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Clean interface with smooth animations
- 📈 **Progress Tracking** - Visual progress indicators and status tracking
- 🔍 **Search & Filter** - Advanced filtering for tasks and projects
- ⚙️ **Settings Panel** - Customizable user preferences

## Quick Start

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn package manager

### Installation & Running

1. Navigate to the gui directory:
```bash
cd gui
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:3000`

## Application Structure

### Main Pages
- **Dashboard** - Overview with charts, metrics, and activity feeds
- **Progress Tracker** - Detailed task management with filtering
- **Project Plans** - Project timeline and milestone tracking
- **Plan Comparison** - Compare planned vs actual progress
- **Settings** - User preferences and configuration

### Key Components
- **Sidebar Navigation** - Collapsible menu with project status
- **Task Modal** - Interactive forms for task creation/editing
- **Notification Center** - Sliding panel with real-time updates
- **Charts** - Interactive data visualization using Chart.js

### State Management
- React Context API for global state
- Automatic data refresh every 30 seconds
- Persistent notifications and task management

## Sample Data

The application includes 10 sample tasks across different project phases:
- AI/ML Model Development
- Web Dashboard Creation
- API Development
- Testing & QA
- Documentation
- Deployment Planning

## Technology Stack

- **React 18.2.0** - Frontend framework
- **React Router DOM** - Client-side routing
- **Chart.js** - Data visualization
- **Lucide React** - Modern icon system
- **Date-fns** - Date manipulation
- **Custom CSS** - Responsive styling with animations

## Interactive Features

- ✨ Click task cards to edit details
- 🔍 Search tasks by name or description
- 📊 Hover over charts for detailed data
- 🔔 View real-time notifications
- 📱 Responsive sidebar that adapts to screen size
- ⚙️ Customize settings and preferences

## Development

To modify the application:

1. Components are in `src/components/`
2. Global state is managed in `src/context/ProjectContext.js`
3. Styling uses CSS modules and responsive design patterns
4. Charts are configured in the Dashboard component

The application is designed for immediate interaction and testing with a professional, modern interface suitable for real project management scenarios.
