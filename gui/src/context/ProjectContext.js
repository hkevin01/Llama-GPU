import { createContext, useContext, useEffect, useReducer } from 'react';

const ProjectContext = createContext();

// Sample project data with comprehensive tasks and progress
const initialState = {
  tasks: [
    {
      id: 'TCH-001',
      title: 'Core Inference Engine Implementation',
      description: 'Develop the main inference engine with multi-backend support',
      status: 'complete',
      priority: 'critical',
      category: 'Core Development',
      phase: 'Phase 1',
      assignee: 'Development Team',
      plannedStart: '2025-07-01',
      plannedEnd: '2025-07-15',
      actualStart: '2025-07-01',
      actualEnd: '2025-07-14',
      progress: 100,
      dependencies: [],
      blockers: [],
      notes: 'Completed ahead of schedule with optimized CUDA integration'
    },
    {
      id: 'TCH-002',
      title: 'Multi-GPU Support Architecture',
      description: 'Implement tensor and pipeline parallelism for multi-GPU setups',
      status: 'complete',
      priority: 'high',
      category: 'Performance',
      phase: 'Phase 1',
      assignee: 'GPU Team',
      plannedStart: '2025-07-08',
      plannedEnd: '2025-07-22',
      actualStart: '2025-07-10',
      actualEnd: '2025-07-20',
      progress: 100,
      dependencies: ['TCH-001'],
      blockers: [],
      notes: 'Successfully implemented with load balancing'
    },
    {
      id: 'TCH-003',
      title: 'Plugin Architecture Framework',
      description: 'Create extensible plugin system for custom functionality',
      status: 'complete',
      priority: 'high',
      category: 'Architecture',
      phase: 'Phase 1',
      assignee: 'Architecture Team',
      plannedStart: '2025-07-15',
      plannedEnd: '2025-07-29',
      actualStart: '2025-07-16',
      actualEnd: '2025-07-28',
      progress: 100,
      dependencies: ['TCH-001'],
      blockers: [],
      notes: 'Plugin marketplace foundation ready'
    },
    {
      id: 'GUI-001',
      title: 'Web Dashboard Interface',
      description: 'Build responsive web dashboard with Bootstrap and Flask',
      status: 'complete',
      priority: 'high',
      category: 'Frontend',
      phase: 'Phase 2',
      assignee: 'Frontend Team',
      plannedStart: '2025-07-22',
      plannedEnd: '2025-08-05',
      actualStart: '2025-07-25',
      actualEnd: '2025-08-01',
      progress: 100,
      dependencies: ['TCH-001', 'TCH-003'],
      blockers: [],
      notes: 'Professional UI with real-time monitoring capabilities'
    },
    {
      id: 'API-001',
      title: 'REST API Development',
      description: 'Create comprehensive REST API with OpenAPI documentation',
      status: 'progress',
      priority: 'high',
      category: 'Backend',
      phase: 'Phase 2',
      assignee: 'API Team',
      plannedStart: '2025-07-29',
      plannedEnd: '2025-08-12',
      actualStart: '2025-07-30',
      actualEnd: null,
      progress: 85,
      dependencies: ['TCH-001'],
      blockers: [],
      notes: 'Rate limiting and authentication in progress'
    },
    {
      id: 'TEST-001',
      title: 'Comprehensive Testing Suite',
      description: 'Develop unit, integration, and performance tests',
      status: 'progress',
      priority: 'high',
      category: 'Quality Assurance',
      phase: 'Phase 2',
      assignee: 'QA Team',
      plannedStart: '2025-08-01',
      plannedEnd: '2025-08-15',
      actualStart: '2025-08-02',
      actualEnd: null,
      progress: 70,
      dependencies: ['TCH-001', 'API-001'],
      blockers: [],
      notes: 'Unit tests complete, integration tests in progress'
    },
    {
      id: 'DOC-001',
      title: 'Technical Documentation',
      description: 'Create comprehensive technical documentation',
      status: 'progress',
      priority: 'medium',
      category: 'Documentation',
      phase: 'Phase 2',
      assignee: 'Documentation Team',
      plannedStart: '2025-08-05',
      plannedEnd: '2025-08-20',
      actualStart: '2025-08-01',
      actualEnd: null,
      progress: 60,
      dependencies: ['API-001'],
      blockers: [],
      notes: 'API docs complete, user guides in progress'
    },
    {
      id: 'SEC-001',
      title: 'Security Implementation',
      description: 'Implement authentication, authorization, and security measures',
      status: 'not-started',
      priority: 'high',
      category: 'Security',
      phase: 'Phase 3',
      assignee: 'Security Team',
      plannedStart: '2025-08-10',
      plannedEnd: '2025-08-25',
      actualStart: null,
      actualEnd: null,
      progress: 0,
      dependencies: ['API-001'],
      blockers: ['Waiting for security review approval'],
      notes: 'Pending security architecture review'
    },
    {
      id: 'PERF-001',
      title: 'Performance Optimization',
      description: 'Optimize inference speed and memory usage',
      status: 'not-started',
      priority: 'medium',
      category: 'Performance',
      phase: 'Phase 3',
      assignee: 'Performance Team',
      plannedStart: '2025-08-15',
      plannedEnd: '2025-08-30',
      actualStart: null,
      actualEnd: null,
      progress: 0,
      dependencies: ['TEST-001'],
      blockers: [],
      notes: 'Benchmarking framework needed'
    },
    {
      id: 'DEPLOY-001',
      title: 'Production Deployment',
      description: 'Set up production infrastructure and CI/CD pipelines',
      status: 'not-started',
      priority: 'high',
      category: 'DevOps',
      phase: 'Phase 3',
      assignee: 'DevOps Team',
      plannedStart: '2025-08-20',
      plannedEnd: '2025-09-05',
      actualStart: null,
      actualEnd: null,
      progress: 0,
      dependencies: ['SEC-001', 'TEST-001'],
      blockers: [],
      notes: 'AWS infrastructure planning in progress'
    }
  ],
  plans: [
    {
      id: 'plan-1',
      name: 'Core Development Plan',
      file: 'plan.md',
      created: '2025-07-01',
      lastModified: '2025-07-15',
      status: 'active',
      phases: ['Phase 1', 'Phase 2'],
      totalTasks: 25,
      completedTasks: 18
    },
    {
      id: 'plan-2',
      name: 'GUI Implementation Plan',
      file: 'plan_part1.md',
      created: '2025-07-20',
      lastModified: '2025-08-01',
      status: 'completed',
      phases: ['Phase 2'],
      totalTasks: 8,
      completedTasks: 8
    },
    {
      id: 'plan-3',
      name: 'Security & Deployment Plan',
      file: 'plan_part2.md',
      created: '2025-08-01',
      lastModified: '2025-08-01',
      status: 'in-progress',
      phases: ['Phase 3'],
      totalTasks: 12,
      completedTasks: 2
    }
  ],
  notifications: [
    {
      id: 1,
      type: 'success',
      title: 'Task Completed',
      message: 'Web Dashboard Interface has been successfully completed',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      read: false
    },
    {
      id: 2,
      type: 'warning',
      title: 'Blocker Identified',
      message: 'Security Implementation is blocked pending review approval',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
      read: false
    },
    {
      id: 3,
      type: 'info',
      title: 'Milestone Reached',
      message: 'Phase 2 development is 75% complete',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
      read: true
    }
  ],
  settings: {
    theme: 'light',
    autoRefresh: true,
    refreshInterval: 30000,
    showCompletedTasks: true,
    defaultView: 'dashboard'
  },
  ui: {
    taskModal: {
      isOpen: false,
      taskId: null,
      mode: 'view' // 'view', 'edit', 'create'
    },
    notifications: {
      isOpen: false
    },
    filters: {
      status: 'all',
      priority: 'all',
      category: 'all',
      phase: 'all',
      assignee: 'all'
    }
  }
};

function projectReducer(state, action) {
  switch (action.type) {
    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id
            ? { ...task, ...action.payload.updates }
            : task
        )
      };

    case 'ADD_TASK':
      return {
        ...state,
        tasks: [...state.tasks, { ...action.payload, id: `TASK-${Date.now()}` }]
      };

    case 'DELETE_TASK':
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload.id)
      };

    case 'OPEN_TASK_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          taskModal: {
            isOpen: true,
            taskId: action.payload.taskId,
            mode: action.payload.mode || 'view'
          }
        }
      };

    case 'CLOSE_TASK_MODAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          taskModal: {
            isOpen: false,
            taskId: null,
            mode: 'view'
          }
        }
      };

    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [
          {
            id: Date.now(),
            timestamp: new Date(),
            read: false,
            ...action.payload
          },
          ...state.notifications
        ]
      };

    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(notification =>
          notification.id === action.payload.id
            ? { ...notification, read: true }
            : notification
        )
      };

    case 'TOGGLE_NOTIFICATIONS':
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: {
            isOpen: !state.ui.notifications.isOpen
          }
        }
      };

    case 'UPDATE_FILTERS':
      return {
        ...state,
        ui: {
          ...state.ui,
          filters: {
            ...state.ui.filters,
            ...action.payload
          }
        }
      };

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload
        }
      };

    default:
      return state;
  }
}

export function ProjectProvider({ children }) {
  const [state, dispatch] = useReducer(projectReducer, initialState);

  // Auto-refresh functionality
  useEffect(() => {
    if (state.settings.autoRefresh) {
      const interval = setInterval(() => {
        // Simulate data updates
        const randomTask = state.tasks[Math.floor(Math.random() * state.tasks.length)];
        if (randomTask && randomTask.status === 'progress' && randomTask.progress < 100) {
          const newProgress = Math.min(100, randomTask.progress + Math.random() * 5);
          dispatch({
            type: 'UPDATE_TASK',
            payload: {
              id: randomTask.id,
              updates: { progress: Math.round(newProgress) }
            }
          });
        }
      }, state.settings.refreshInterval);

      return () => clearInterval(interval);
    }
  }, [state.settings.autoRefresh, state.settings.refreshInterval, state.tasks]);

  const contextValue = {
    state,
    dispatch,

    // Helper functions
    getTaskById: (id) => state.tasks.find(task => task.id === id),
    getFilteredTasks: () => {
      const { filters } = state.ui;
      return state.tasks.filter(task => {
        if (filters.status !== 'all' && task.status !== filters.status) return false;
        if (filters.priority !== 'all' && task.priority !== filters.priority) return false;
        if (filters.category !== 'all' && task.category !== filters.category) return false;
        if (filters.phase !== 'all' && task.phase !== filters.phase) return false;
        if (filters.assignee !== 'all' && task.assignee !== filters.assignee) return false;
        return true;
      });
    },
    getProjectStats: () => {
      const tasks = state.tasks;
      const total = tasks.length;
      const completed = tasks.filter(t => t.status === 'complete').length;
      const inProgress = tasks.filter(t => t.status === 'progress').length;
      const blocked = tasks.filter(t => t.status === 'blocked').length;
      const notStarted = tasks.filter(t => t.status === 'not-started').length;

      return {
        total,
        completed,
        inProgress,
        blocked,
        notStarted,
        completionRate: total > 0 ? Math.round((completed / total) * 100) : 0
      };
    },
    getUnreadNotifications: () => state.notifications.filter(n => !n.read)
  };

  return (
    <ProjectContext.Provider value={contextValue}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
}

export { ProjectContext };
