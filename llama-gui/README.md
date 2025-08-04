# Llama-GPU Interface

A modern, responsive GUI application for managing GPU-accelerated LLaMA model inference. Built with React, Material-UI, and Electron for a desktop-class experience.

## Features

- **Model Management**: Load, unload, and configure LLaMA models with various backends
- **Inference Center**: Interactive text generation with real-time streaming and batch processing
- **Multi-GPU Configuration**: Manage multiple GPUs with advanced parallelism strategies
- **Quantization Settings**: Configure model compression with performance analysis
- **Performance Monitoring**: Real-time metrics, GPU utilization, and system statistics
- **API Server Control**: Manage the inference API server with endpoint documentation
- **Settings & Preferences**: Theme control, configuration export/import, and user preferences
- **Dark/Light Theme**: Seamless theme switching with Material-UI integration

## Quick Start

### Prerequisites

- Node.js 16 or later
- npm or yarn package manager
- CUDA-compatible GPU (for backend integration)

### Installation

1. **Navigate to the GUI directory:**
   ```bash
   cd llama-gui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The application will open at `http://localhost:3000`

### Running as Desktop App (Electron)

1. **Start the Electron application:**
   ```bash
   npm run electron-dev
   ```

   This will start both the React development server and the Electron wrapper.

2. **Build for production:**
   ```bash
   npm run build
   npm run electron-pack
   ```

## Project Structure

```
llama-gui/
├── public/                 # Static assets and Electron main process
├── src/
│   ├── components/         # React components
│   │   ├── Common/        # Reusable components (LoadingSpinner, NotificationSystem)
│   │   ├── Layout/        # Layout components (Header, Sidebar)
│   │   └── Pages/         # Main application pages
│   ├── context/           # React Context for state management
│   ├── App.js             # Main application component
│   ├── index.js           # Application entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
└── README.md              # This file
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run electron` - Run Electron app (after build)
- `npm run electron-dev` - Run in development mode with hot reload
- `npm run electron-pack` - Build and package for distribution

## CUDA Optimization

The application includes CUDA acceleration support using `cudf` and `numba`:

- **Data Processing**: GPU-accelerated data processing using RAPIDS cuDF
- **Memory Management**: Efficient GPU memory handling for large datasets
- **Metrics Computation**: Real-time performance metrics calculation on GPU
- **Text Processing**: CUDA-accelerated text processing for responses

To enable CUDA optimization:

1. Make sure you have CUDA toolkit installed
2. Install CUDA dependencies:
   ```bash
   pip install cudf-cu11 numba
   ```
3. The system will automatically detect and use CUDA when available

## Configuration

The application includes a comprehensive state management system that handles:

- **System Information**: GPU detection, memory usage, temperature monitoring
- **Model State**: Currently loaded models, available models, backend status
- **Multi-GPU Setup**: GPU selection, parallelism configuration, load balancing
- **Quantization**: Compression settings, memory analysis, performance impact
- **Inference Tracking**: Active requests, generation parameters, streaming output
- **Performance Metrics**: Real-time charts, system statistics, export capabilities

## Backend Integration

The GUI is designed to integrate with the existing Python backend API. Key integration points:

- **Model Loading**: Communicates with backend model management endpoints
- **Inference Requests**: Handles text generation via REST API and WebSocket streaming
- **System Monitoring**: Retrieves real-time GPU and performance metrics
- **Configuration Sync**: Synchronizes settings between frontend and backend

### API Endpoints Expected

- `GET /api/models` - List available models
- `POST /api/models/load` - Load a specific model
- `POST /api/models/unload` - Unload current model
- `POST /api/inference` - Submit inference request
- `GET /api/system/status` - Get system information
- `GET /api/performance/metrics` - Get performance statistics
- `WebSocket /ws` - Real-time updates and streaming

## Theme Customization

The application supports both light and dark themes with Material-UI integration:

- **Light Theme**: Clean, professional interface with blue accents
- **Dark Theme**: Reduced eye strain with carefully chosen contrast ratios
- **Dynamic Switching**: Seamless theme transitions with persistent preferences
- **Component Theming**: All components automatically adapt to theme changes

## Development Notes

### State Management

The application uses React Context with useReducer for comprehensive state management:

```javascript
import { useAppContext } from './context/AppContext';

function MyComponent() {
  const { state, dispatch } = useAppContext();

  // Access any part of the application state
  const { ui, system, models, multiGpu, quantization } = state;

  // Dispatch actions to update state
  dispatch({ type: 'TOGGLE_THEME' });
}
```

### Adding New Features

1. **New Pages**: Add components to `src/components/Pages/`
2. **State Updates**: Add action types and reducer cases to `AppContext.js`
3. **Navigation**: Update routes in `App.js` and sidebar navigation
4. **API Integration**: Add service functions for backend communication

### Performance Considerations

- **Real-time Updates**: Uses efficient state updates and React.memo for optimization
- **Chart Rendering**: Recharts with optimized data structures for smooth animations
- **Memory Management**: Proper cleanup of intervals, timeouts, and event listeners

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in package.json or stop conflicting processes
2. **Dependency Errors**: Run `npm install` or delete `node_modules` and reinstall
3. **Electron Issues**: Ensure compatible versions of Node.js and Electron
4. **Theme Not Loading**: Check Material-UI theme provider configuration

### Development Tips

- Use React Developer Tools for debugging component state
- Check browser console for JavaScript errors
- Monitor network tab for API request issues
- Use Material-UI theme inspector for styling debugging

## Contributing

1. Follow React best practices and Material-UI design principles
2. Maintain consistent code formatting (consider using Prettier)
3. Add proper error handling and loading states
4. Test theme switching and responsive behavior
5. Document new features and API integrations

## License

This project is part of the Llama-GPU inference system. See the main project documentation for licensing information.
