import PropTypes from 'prop-types';
import { createContext, useContext, useEffect, useMemo, useReducer } from 'react';

const AppContext = createContext();

// Initial state
const initialState = {
  // UI state
  ui: {
    activePage: 'dashboard',
    darkMode: false,
    sidebarOpen: true,
  },

  // System info
  systemInfo: {
    gpus: [
      { name: 'NVIDIA RTX 4090', memoryTotal: 24576, memoryUsed: 2048 },
      { name: 'NVIDIA RTX 4080', memoryTotal: 16384, memoryUsed: 1024 },
    ],
    cpuUsage: 25,
    memoryUsage: 45,
    apiServerStatus: 'disconnected',
    backendType: 'CUDA',
    awsDetected: false,
  },

  // Model management
  models: {
    available: [
      'microsoft/DialoGPT-medium',
      'gpt2',
      'facebook/opt-350m',
      'EleutherAI/gpt-neo-125M',
      'huggingface/CodeBERTa-small-v1'
    ],
    loaded: null,
    loading: false,
    loadError: null,
  },

  // Multi-GPU configuration
  multiGPU: {
    enabled: false,
    strategy: 'tensor',
    gpuIds: [0, 1],
    tensorParallelSize: 2,
    pipelineParallelSize: 2,
    dataParallelSize: 1,
    loadBalancing: 'round_robin',
    stats: {
      gpuLoads: {},
      gpuMemory: {},
      throughput: 0,
    },
  },

  // Quantization settings
  quantization: {
    enabled: false,
    type: 'int8',
    dynamic: true,
    perChannel: true,
    symmetric: true,
    reduceRange: true,
    memoryEfficient: true,
    preserveAccuracy: true,
    stats: {
      memorySaved: 0,
      accuracyLoss: 0,
      modelsQuantized: 0,
    },
  },

  // Inference state
  inference: {
    isGenerating: false,
    prompt: '',
    response: '',
    parameters: {
      maxTokens: 100,
      temperature: 0.7,
      topP: 0.9,
      topK: 50,
      repetitionPenalty: 1.0,
    },
    batchQueue: [],
    streamingOutput: '',
    activeRequests: [],
    stats: {
      totalRequests: 127,
      successfulRequests: 124,
      avgTokensPerSecond: 23.5,
      avgResponseTime: 450,
      batchesProcessed: 15,
      avgBatchSize: 3.2,
      batchThroughput: 8.7,
      avgBatchProcessingTime: 850,
    },
  },

  // Performance metrics
  performance: {
    tokensPerSecond: 0,
    responseTime: 0,
    queueLength: 0,
    batchSize: 1,
    averageLatency: 0,
    throughput: 0,
    errorRate: 0,
    uptime: 0,
  },

  // API server configuration
  apiServer: {
    running: false,
    port: 8000,
    host: 'localhost',
    apiKey: 'test-key',
    rateLimitEnabled: true,
    rateLimit: 60,
    corsEnabled: true,
    authEnabled: true,
    loggingEnabled: true,
    stats: {
      totalRequests: 0,
      activeConnections: 0,
      errorCount: 0,
      averageResponseTime: 0,
    },
  },

  // Application settings
  settings: {
    theme: 'light',
    autoRefresh: true,
    refreshInterval: 5,
    notifications: true,
    soundEnabled: false,
    compactView: false,
    showAdvanced: false,
    autoSave: true,
    logLevel: 'info',
  },

  // Notifications
  notifications: {
    items: [
      {
        id: 1,
        title: 'System Started',
        message: 'Llama-GPU interface is ready',
        type: 'success',
        timestamp: '10:30:15',
        read: false,
      },
      {
        id: 2,
        title: 'GPU Detected',
        message: '2 CUDA-compatible GPUs found',
        type: 'info',
        timestamp: '10:30:16',
        read: false,
      },
    ],
    unread: 2,
  },

  // WebSocket connection
  wsConnected: false,
  wsReconnecting: false,
};

// Action types
const actionTypes = {
  // System
  SET_SYSTEM_INFO: 'SET_SYSTEM_INFO',
  UPDATE_GPU_STATS: 'UPDATE_GPU_STATS',
  SET_API_SERVER_STATUS: 'SET_API_SERVER_STATUS',
  REFRESH_SYSTEM_STATS: 'REFRESH_SYSTEM_STATS',
  REFRESH_GPU_STATS: 'REFRESH_GPU_STATS',
  REFRESH_AVAILABLE_MODELS: 'REFRESH_AVAILABLE_MODELS',
  REFRESH_PERFORMANCE_METRICS: 'REFRESH_PERFORMANCE_METRICS',

  // UI
  SET_ACTIVE_PAGE: 'SET_ACTIVE_PAGE',
  TOGGLE_THEME: 'TOGGLE_THEME',

  // Models
  SET_AVAILABLE_MODELS: 'SET_AVAILABLE_MODELS',
  SET_MODEL_LOADING: 'SET_MODEL_LOADING',
  SET_LOADED_MODEL: 'SET_LOADED_MODEL',
  SET_MODEL_ERROR: 'SET_MODEL_ERROR',
  UNLOAD_MODEL: 'UNLOAD_MODEL',

  // Multi-GPU
  UPDATE_MULTI_GPU_CONFIG: 'UPDATE_MULTI_GPU_CONFIG',
  UPDATE_MULTI_GPU_STATS: 'UPDATE_MULTI_GPU_STATS',
  TOGGLE_MULTI_GPU: 'TOGGLE_MULTI_GPU',
  SET_MULTI_GPU_STRATEGY: 'SET_MULTI_GPU_STRATEGY',
  SET_LOAD_BALANCING: 'SET_LOAD_BALANCING',
  SET_GPU_IDS: 'SET_GPU_IDS',
  SET_PARALLELISM_SIZE: 'SET_PARALLELISM_SIZE',

  // Quantization
  UPDATE_QUANTIZATION_CONFIG: 'UPDATE_QUANTIZATION_CONFIG',
  UPDATE_QUANTIZATION_STATS: 'UPDATE_QUANTIZATION_STATS',
  TOGGLE_QUANTIZATION: 'TOGGLE_QUANTIZATION',
  SET_QUANTIZATION_TYPE: 'SET_QUANTIZATION_TYPE',
  SET_QUANTIZATION_DYNAMIC: 'SET_QUANTIZATION_DYNAMIC',
  SET_QUANTIZATION_MEMORY_EFFICIENT: 'SET_QUANTIZATION_MEMORY_EFFICIENT',
  SET_QUANTIZATION_PRESERVE_ACCURACY: 'SET_QUANTIZATION_PRESERVE_ACCURACY',

  // Inference
  SET_INFERENCE_STATE: 'SET_INFERENCE_STATE',
  UPDATE_INFERENCE_PARAMS: 'UPDATE_INFERENCE_PARAMS',
  ADD_TO_BATCH_QUEUE: 'ADD_TO_BATCH_QUEUE',
  REMOVE_FROM_BATCH_QUEUE: 'REMOVE_FROM_BATCH_QUEUE',
  UPDATE_STREAMING_OUTPUT: 'UPDATE_STREAMING_OUTPUT',
  ADD_ACTIVE_REQUEST: 'ADD_ACTIVE_REQUEST',
  REMOVE_ACTIVE_REQUEST: 'REMOVE_ACTIVE_REQUEST',
  UPDATE_INFERENCE_STATS: 'UPDATE_INFERENCE_STATS',

  // Notifications
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  MARK_NOTIFICATION_READ: 'MARK_NOTIFICATION_READ',
  MARK_ALL_NOTIFICATIONS_READ: 'MARK_ALL_NOTIFICATIONS_READ',
  CLEAR_NOTIFICATIONS: 'CLEAR_NOTIFICATIONS',

  // Performance
  UPDATE_PERFORMANCE_METRICS: 'UPDATE_PERFORMANCE_METRICS',

  // API Server
  UPDATE_API_SERVER_CONFIG: 'UPDATE_API_SERVER_CONFIG',
  UPDATE_API_SERVER_STATS: 'UPDATE_API_SERVER_STATS',

  // Settings
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',

  // WebSocket
  SET_WS_CONNECTED: 'SET_WS_CONNECTED',
  SET_WS_RECONNECTING: 'SET_WS_RECONNECTING',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_SYSTEM_INFO:
      return {
        ...state,
        systemInfo: { ...state.systemInfo, ...action.payload },
      };

    case actionTypes.UPDATE_GPU_STATS:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          stats: { ...state.multiGPU.stats, ...action.payload },
        },
      };

    case actionTypes.SET_API_SERVER_STATUS:
      return {
        ...state,
        systemInfo: {
          ...state.systemInfo,
          apiServerStatus: action.payload,
        },
      };

    case actionTypes.SET_ACTIVE_PAGE:
      return {
        ...state,
        ui: {
          ...state.ui,
          activePage: action.payload,
        },
      };

    case actionTypes.TOGGLE_THEME:
      return {
        ...state,
        ui: {
          ...state.ui,
          darkMode: !state.ui.darkMode,
        },
      };

    case actionTypes.REFRESH_SYSTEM_STATS:
    case actionTypes.REFRESH_GPU_STATS:
    case actionTypes.REFRESH_AVAILABLE_MODELS:
    case actionTypes.REFRESH_PERFORMANCE_METRICS:
      // These are handled by effects, just return state
      return state;

    case actionTypes.SET_AVAILABLE_MODELS:
      return {
        ...state,
        models: {
          ...state.models,
          available: action.payload,
        },
      };

    case actionTypes.SET_MODEL_LOADING:
      return {
        ...state,
        models: {
          ...state.models,
          loading: action.payload,
          loadError: null,
        },
      };

    case actionTypes.SET_LOADED_MODEL:
      return {
        ...state,
        models: {
          ...state.models,
          loaded: action.payload,
          loading: false,
          loadError: null,
        },
      };

    case actionTypes.SET_MODEL_ERROR:
      return {
        ...state,
        models: {
          ...state.models,
          loading: false,
          loadError: action.payload,
        },
      };

    case actionTypes.UNLOAD_MODEL:
      return {
        ...state,
        models: {
          ...state.models,
          loaded: null,
          loading: false,
          loadError: null,
        },
      };

    case actionTypes.UPDATE_MULTI_GPU_CONFIG:
      return {
        ...state,
        multiGPU: { ...state.multiGPU, ...action.payload },
      };

    case actionTypes.UPDATE_MULTI_GPU_STATS:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          stats: { ...state.multiGPU.stats, ...action.payload },
        },
      };

    case actionTypes.TOGGLE_MULTI_GPU:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          enabled: action.payload,
        },
      };

    case actionTypes.SET_MULTI_GPU_STRATEGY:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          strategy: action.payload,
        },
      };

    case actionTypes.SET_LOAD_BALANCING:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          loadBalancing: action.payload,
        },
      };

    case actionTypes.SET_GPU_IDS:
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          gpuIds: action.payload,
        },
      };

    case actionTypes.SET_PARALLELISM_SIZE: {
      const { type, value } = action.payload;
      return {
        ...state,
        multiGPU: {
          ...state.multiGPU,
          [`${type}ParallelSize`]: value,
        },
      };
    }

    case actionTypes.UPDATE_QUANTIZATION_CONFIG:
      return {
        ...state,
        quantization: { ...state.quantization, ...action.payload },
      };

    case actionTypes.UPDATE_QUANTIZATION_STATS:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          stats: { ...state.quantization.stats, ...action.payload },
        },
      };

    case actionTypes.TOGGLE_QUANTIZATION:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          enabled: action.payload,
        },
      };

    case actionTypes.SET_QUANTIZATION_TYPE:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          type: action.payload,
        },
      };

    case actionTypes.SET_QUANTIZATION_DYNAMIC:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          dynamic: action.payload,
        },
      };

    case actionTypes.SET_QUANTIZATION_MEMORY_EFFICIENT:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          memoryEfficient: action.payload,
        },
      };

    case actionTypes.SET_QUANTIZATION_PRESERVE_ACCURACY:
      return {
        ...state,
        quantization: {
          ...state.quantization,
          preserveAccuracy: action.payload,
        },
      };

    case actionTypes.SET_INFERENCE_STATE:
      return {
        ...state,
        inference: { ...state.inference, ...action.payload },
      };

    case actionTypes.UPDATE_INFERENCE_PARAMS:
      return {
        ...state,
        inference: {
          ...state.inference,
          parameters: { ...state.inference.parameters, ...action.payload },
        },
      };

    case actionTypes.ADD_TO_BATCH_QUEUE:
      return {
        ...state,
        inference: {
          ...state.inference,
          batchQueue: [...state.inference.batchQueue, action.payload],
        },
      };

    case actionTypes.REMOVE_FROM_BATCH_QUEUE:
      return {
        ...state,
        inference: {
          ...state.inference,
          batchQueue: state.inference.batchQueue.filter(
            (item, index) => index !== action.payload
          ),
        },
      };

    case actionTypes.UPDATE_STREAMING_OUTPUT:
      return {
        ...state,
        inference: {
          ...state.inference,
          streamingOutput: state.inference.streamingOutput + action.payload,
        },
      };

    case actionTypes.ADD_ACTIVE_REQUEST:
      return {
        ...state,
        inference: {
          ...state.inference,
          activeRequests: [...state.inference.activeRequests, action.payload],
        },
      };

    case actionTypes.REMOVE_ACTIVE_REQUEST:
      return {
        ...state,
        inference: {
          ...state.inference,
          activeRequests: state.inference.activeRequests.filter(
            request => request.id !== action.payload
          ),
        },
      };

    case actionTypes.UPDATE_INFERENCE_STATS:
      return {
        ...state,
        inference: {
          ...state.inference,
          stats: { ...state.inference.stats, ...action.payload },
        },
      };

    case actionTypes.UPDATE_PERFORMANCE_METRICS:
      return {
        ...state,
        performance: { ...state.performance, ...action.payload },
      };

    case actionTypes.UPDATE_API_SERVER_CONFIG:
      return {
        ...state,
        apiServer: { ...state.apiServer, ...action.payload },
      };

    case actionTypes.UPDATE_API_SERVER_STATS:
      return {
        ...state,
        apiServer: {
          ...state.apiServer,
          stats: { ...state.apiServer.stats, ...action.payload },
        },
      };

    case actionTypes.UPDATE_SETTINGS:
      return {
        ...state,
        settings: { ...state.settings, ...action.payload },
      };

    case actionTypes.SET_WS_CONNECTED:
      return {
        ...state,
        wsConnected: action.payload,
        wsReconnecting: false,
      };

    case actionTypes.SET_WS_RECONNECTING:
      return {
        ...state,
        wsReconnecting: action.payload,
      };

    // Notification actions
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: {
          ...state.notifications,
          items: [...state.notifications.items, action.payload],
          unread: state.notifications.unread + 1,
        },
      };

    case actionTypes.MARK_NOTIFICATION_READ:
      return {
        ...state,
        notifications: {
          ...state.notifications,
          items: state.notifications.items.map(item =>
            item.id === action.payload ? { ...item, read: true } : item
          ),
          unread: Math.max(0, state.notifications.unread - 1),
        },
      };

    case actionTypes.MARK_ALL_NOTIFICATIONS_READ:
      return {
        ...state,
        notifications: {
          ...state.notifications,
          items: state.notifications.items.map(item => ({ ...item, read: true })),
          unread: 0,
        },
      };

    case actionTypes.CLEAR_NOTIFICATIONS:
      return {
        ...state,
        notifications: {
          items: [],
          unread: 0,
        },
      };

    default:
      return state;
  }
}

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Simulate system info updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (state.settings.autoRefresh) {
        // Update performance metrics with simulated data
        dispatch({
          type: actionTypes.UPDATE_PERFORMANCE_METRICS,
          payload: {
            tokensPerSecond: Math.random() * 100 + 50,
            responseTime: Math.random() * 1000 + 100,
            queueLength: Math.floor(Math.random() * 10),
            averageLatency: Math.random() * 500 + 50,
            throughput: Math.random() * 50 + 25,
          },
        });

        // Update GPU stats
        dispatch({
          type: actionTypes.UPDATE_GPU_STATS,
          payload: {
            gpuLoads: {
              0: Math.random() * 0.8 + 0.1,
              1: Math.random() * 0.8 + 0.1,
            },
            gpuMemory: {
              0: Math.random() * 0.7 + 0.2,
              1: Math.random() * 0.7 + 0.2,
            },
            throughput: Math.random() * 100 + 50,
          },
        });
      }
    }, state.settings.refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [state.settings.autoRefresh, state.settings.refreshInterval]);

  const value = useMemo(() => ({
    state,
    dispatch,
    actionTypes,
  }), [state]);

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

AppProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// Hook to use the context
export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export { actionTypes };
