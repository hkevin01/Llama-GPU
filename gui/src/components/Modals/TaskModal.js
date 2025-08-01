import React, { useState, useEffect } from 'react';
import { X, Save, Calendar, User, Tag, AlertCircle } from 'lucide-react';
import { useProject } from '../../context/ProjectContext';
import './TaskModal.css';

function TaskModal() {
  const { state, dispatch, getTaskById } = useProject();
  const { taskModal } = state.ui;
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});

  const task = taskModal.taskId ? getTaskById(taskModal.taskId) : null;

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title || '',
        description: task.description || '',
        status: task.status || 'not-started',
        priority: task.priority || 'medium',
        category: task.category || '',
        phase: task.phase || '',
        assignee: task.assignee || '',
        plannedStart: task.plannedStart || '',
        plannedEnd: task.plannedEnd || '',
        progress: task.progress || 0,
        notes: task.notes || ''
      });
    } else if (taskModal.mode === 'create') {
      setFormData({
        title: '',
        description: '',
        status: 'not-started',
        priority: 'medium',
        category: 'Core Development',
        phase: 'Phase 1',
        assignee: 'Development Team',
        plannedStart: '',
        plannedEnd: '',
        progress: 0,
        notes: ''
      });
    }
  }, [task, taskModal.mode]);

  const handleClose = () => {
    dispatch({ type: 'CLOSE_TASK_MODAL' });
    setFormData({});
    setErrors({});
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title?.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.description?.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (formData.plannedStart && formData.plannedEnd) {
      if (new Date(formData.plannedStart) > new Date(formData.plannedEnd)) {
        newErrors.plannedEnd = 'End date must be after start date';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    if (taskModal.mode === 'create') {
      dispatch({
        type: 'ADD_TASK',
        payload: {
          ...formData,
          dependencies: [],
          blockers: []
        }
      });
      
      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          type: 'success',
          title: 'Task Created',
          message: `New task "${formData.title}" has been created successfully`
        }
      });
    } else if (taskModal.mode === 'edit') {
      dispatch({
        type: 'UPDATE_TASK',
        payload: {
          id: taskModal.taskId,
          updates: formData
        }
      });
      
      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          type: 'success',
          title: 'Task Updated',
          message: `Task "${formData.title}" has been updated successfully`
        }
      });
    }

    handleClose();
  };

  const handleStatusChange = (newStatus) => {
    let newProgress = formData.progress;
    
    switch (newStatus) {
      case 'complete':
        newProgress = 100;
        break;
      case 'not-started':
        newProgress = 0;
        break;
      case 'blocked':
        // Keep current progress
        break;
      default:
        // For 'progress' status, keep current progress
        break;
    }
    
    handleInputChange('status', newStatus);
    handleInputChange('progress', newProgress);
  };

  if (!taskModal.isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content task-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            {taskModal.mode === 'create' && 'Create New Task'}
            {taskModal.mode === 'edit' && 'Edit Task'}
            {taskModal.mode === 'view' && 'Task Details'}
          </h2>
          <button className="close-button" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <form onSubmit={handleSubmit} className="task-form">
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  <Tag size={16} />
                  Task Title
                </label>
                <input
                  type="text"
                  className={`form-input ${errors.title ? 'error' : ''}`}
                  value={formData.title || ''}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Enter task title..."
                  disabled={taskModal.mode === 'view'}
                />
                {errors.title && (
                  <span className="error-message">
                    <AlertCircle size={14} />
                    {errors.title}
                  </span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className={`form-textarea ${errors.description ? 'error' : ''}`}
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe the task..."
                rows={3}
                disabled={taskModal.mode === 'view'}
              />
              {errors.description && (
                <span className="error-message">
                  <AlertCircle size={14} />
                  {errors.description}
                </span>
              )}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Status</label>
                <select
                  className="form-select"
                  value={formData.status || ''}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={taskModal.mode === 'view'}
                >
                  <option value="not-started">Not Started</option>
                  <option value="progress">In Progress</option>
                  <option value="complete">Complete</option>
                  <option value="blocked">Blocked</option>
                  <option value="review">Under Review</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Priority</label>
                <select
                  className="form-select"
                  value={formData.priority || ''}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Category</label>
                <select
                  className="form-select"
                  value={formData.category || ''}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                >
                  <option value="Core Development">Core Development</option>
                  <option value="Frontend">Frontend</option>
                  <option value="Backend">Backend</option>
                  <option value="Quality Assurance">Quality Assurance</option>
                  <option value="Documentation">Documentation</option>
                  <option value="DevOps">DevOps</option>
                  <option value="Security">Security</option>
                  <option value="Performance">Performance</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Phase</label>
                <select
                  className="form-select"
                  value={formData.phase || ''}
                  onChange={(e) => handleInputChange('phase', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                >
                  <option value="Phase 1">Phase 1</option>
                  <option value="Phase 2">Phase 2</option>
                  <option value="Phase 3">Phase 3</option>
                  <option value="Phase 4">Phase 4</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  <User size={16} />
                  Assignee
                </label>
                <select
                  className="form-select"
                  value={formData.assignee || ''}
                  onChange={(e) => handleInputChange('assignee', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                >
                  <option value="Development Team">Development Team</option>
                  <option value="Frontend Team">Frontend Team</option>
                  <option value="Backend Team">Backend Team</option>
                  <option value="QA Team">QA Team</option>
                  <option value="DevOps Team">DevOps Team</option>
                  <option value="Security Team">Security Team</option>
                  <option value="Documentation Team">Documentation Team</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Progress (%)</label>
                <div className="progress-input-container">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.progress || 0}
                    onChange={(e) => handleInputChange('progress', parseInt(e.target.value))}
                    className="progress-slider"
                    disabled={taskModal.mode === 'view'}
                  />
                  <span className="progress-value">{formData.progress || 0}%</span>
                </div>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  <Calendar size={16} />
                  Planned Start
                </label>
                <input
                  type="date"
                  className="form-input"
                  value={formData.plannedStart || ''}
                  onChange={(e) => handleInputChange('plannedStart', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <Calendar size={16} />
                  Planned End
                </label>
                <input
                  type="date"
                  className={`form-input ${errors.plannedEnd ? 'error' : ''}`}
                  value={formData.plannedEnd || ''}
                  onChange={(e) => handleInputChange('plannedEnd', e.target.value)}
                  disabled={taskModal.mode === 'view'}
                />
                {errors.plannedEnd && (
                  <span className="error-message">
                    <AlertCircle size={14} />
                    {errors.plannedEnd}
                  </span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea
                className="form-textarea"
                value={formData.notes || ''}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Additional notes or comments..."
                rows={3}
                disabled={taskModal.mode === 'view'}
              />
            </div>

            {taskModal.mode !== 'view' && (
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={handleClose}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <Save size={16} />
                  {taskModal.mode === 'create' ? 'Create Task' : 'Save Changes'}
                </button>
              </div>
            )}

            {taskModal.mode === 'view' && (
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={handleClose}>
                  Close
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={() => dispatch({
                    type: 'OPEN_TASK_MODAL',
                    payload: { taskId: taskModal.taskId, mode: 'edit' }
                  })}
                >
                  Edit Task
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

export default TaskModal;
