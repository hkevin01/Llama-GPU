import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AppContext = createContext();

// Initial state
const initialState = {
  // System info
  systemInfo: {
    gpus: [],
    cpuUsage: 0,
    memoryUsage: 0,
    apiServerStatus: 'disconnected',
    backendType: 'CPU',
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
  notifications: [],
  
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
  
  // Models
  SET_AVAILABLE_MODELS: 'SET_AVAILABLE_MODELS',
  SET_MODEL_LOADING: 'SET_MODEL_LOADING',
  SET_LOADED_MODEL: 'SET_LOADED_MODEL',
  SET_MODEL_ERROR: 'SET_MODEL_ERROR',
  
  // Multi-GPU
  UPDATE_MULTI_GPU_CONFIG: 'UPDATE_MULTI_GPU_CONFIG',
  UPDATE_MULTI_GPU_STATS: 'UPDATE_MULTI_GPU_STATS',
  
  // Quantization
  UPDATE_QUANTIZATION_CONFIG: 'UPDATE_QUANTIZATION_CONFIG',
  UPDATE_QUANTIZATION_STATS: 'UPDATE_QUANTIZATION_STATS',
  
  // Inference
  SET_INFERENCE_STATE: 'SET_INFERENCE_STATE',
  UPDATE_INFERENCE_PARAMS: 'UPDATE_INFERENCE_PARAMS',
  ADD_TO_BATCH_QUEUE: 'ADD_TO_BATCH_QUEUE',
  REMOVE_FROM_BATCH_QUEUE: 'REMOVE_FROM_BATCH_QUEUE',
  UPDATE_STREAMING_OUTPUT: 'UPDATE_STREAMING_OUTPUT',
  
  // Performance
  UPDATE_PERFORMANCE_METRICS: 'UPDATE_PERFORMANCE_METRICS',
  
  // API Server
  UPDATE_API_SERVER_CONFIG: 'UPDATE_API_SERVER_CONFIG',
  UPDATE_API_SERVER_STATS: 'UPDATE_API_SERVER_STATS',
  
  // Settings
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  
  // Notifications
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  CLEAR_NOTIFICATIONS: 'CLEAR_NOTIFICATIONS',
  
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
      
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [
          ...state.notifications,
          {
            id: Date.now(),
            timestamp: new Date(),
            ...action.payload,
          },
        ],
      };
      
    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(
          (notification) => notification.id !== action.payload
        ),
      };
      
    case actionTypes.CLEAR_NOTIFICATIONS:
      return {
        ...state,
        notifications: [],
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

  const value = {
    state,
    dispatch,
    actionTypes,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export { actionTypes };
