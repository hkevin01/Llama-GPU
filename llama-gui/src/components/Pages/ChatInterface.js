import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Grid,
  Paper,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  LinearProgress,
  Menu,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
} from '@mui/material';
import {
  BarChart,
  Chat,
  Clear,
  Download,
  PlayArrow,
  QueuePlayNext,
  Send,
  Settings,
  SmartToy,
  Stop,
  TextFields,
} from '@mui/icons-material';
import { useAppContext } from '../../context/AppContext';

const ChatInterface = () => {
  const { state, dispatch } = useAppContext();

  // Chat state
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Llama-GPU assistant. How can I help you today?',
      timestamp: new Date(),
      id: 1
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');

  // Interface modes and configuration
  const [mode, setMode] = useState(0); // 0: Chat, 1: Completion, 2: Batch
  const [selectedModel, setSelectedModel] = useState(state.models.loaded?.name || 'llama-base');
  const [backend, setBackend] = useState(state.systemInfo.backendType || 'ROCm');

  // Generation parameters
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(512);
  const [topP, setTopP] = useState(0.9);

  // Batch processing
  const [batchPrompts, setBatchPrompts] = useState(['']);
  const [batchResults, setBatchResults] = useState([]);
  const [batchProgress, setBatchProgress] = useState(0);

  // UI state
  const [showPerformance, setShowPerformance] = useState(true);
  const [settingsAnchor, setSettingsAnchor] = useState(null);

  // Performance metrics
  const [performanceMetrics, setPerformanceMetrics] = useState({
    tokensPerSecond: 0,
    responseTime: 0,
    totalTokens: 0,
    gpuUtilization: 0,
    memoryUsage: 0,
  });

  // Template prompts
  const templates = [
    { name: 'Creative Writing', prompt: 'Write a creative short story about...' },
    { name: 'Code Generation', prompt: 'Generate Python code that...' },
    { name: 'Explanation', prompt: 'Explain in simple terms...' },
    { name: 'Question Answering', prompt: 'Answer this question based on the context...' },
    { name: 'Translation', prompt: 'Translate the following text to...' },
    { name: 'Summarization', prompt: 'Summarize the following text...' },
    { name: 'Data Analysis', prompt: 'Analyze the following data and provide insights...' },
    { name: 'Technical Documentation', prompt: 'Create technical documentation for...' },
  ];

  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // Simulate performance metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (isGenerating) {
        setPerformanceMetrics(prev => ({
          ...prev,
          tokensPerSecond: Math.random() * 50 + 20,
          gpuUtilization: Math.random() * 40 + 60,
          memoryUsage: Math.random() * 20 + 40,
        }));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isGenerating]);

  // Handle sending messages
  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isGenerating) return;

    const userMessage = {
      role: 'user',
      content: currentMessage.trim(),
      timestamp: new Date(),
      id: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsGenerating(true);
    setStreamingContent('');

    // Simulate API call with streaming response
    try {
      const startTime = Date.now();
      await simulateStreamingResponse(userMessage.content, startTime);
    } catch (error) {
      console.error('Error generating response:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        id: Date.now(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsGenerating(false);
      setStreamingContent('');
    }
  };

  // Simulate streaming response
  const simulateStreamingResponse = async (prompt, startTime) => {
    const responses = [
      `I understand you're asking about "${prompt}". Let me provide you with a comprehensive response.`,
      `Based on your query about "${prompt}", here are some key points to consider:`,
      `Thank you for your question about "${prompt}". I'll help you with this topic.`,
    ];

    const selectedResponse = responses[Math.floor(Math.random() * responses.length)];
    const words = selectedResponse.split(' ');
    let currentContent = '';

    // Simulate token-by-token streaming
    for (let i = 0; i < words.length; i++) {
      if (abortControllerRef.current?.signal.aborted) {
        break;
      }

      currentContent += (i > 0 ? ' ' : '') + words[i];
      setStreamingContent(currentContent);

      // Random delay between 50-200ms per word
      await new Promise(resolve => setTimeout(resolve, Math.random() * 150 + 50));
    }

    const responseTime = Date.now() - startTime;
    const tokensGenerated = words.length;

    const assistantMessage = {
      role: 'assistant',
      content: currentContent,
      timestamp: new Date(),
      id: Date.now(),
      responseTime,
      tokensGenerated,
    };

    setMessages(prev => [...prev, assistantMessage]);

    // Update performance metrics
    setPerformanceMetrics(prev => ({
      ...prev,
      responseTime,
      totalTokens: prev.totalTokens + tokensGenerated,
      tokensPerSecond: Math.round((tokensGenerated / responseTime) * 1000),
    }));

    // Update global inference stats
    dispatch({
      type: 'UPDATE_INFERENCE_STATS',
      payload: {
        totalRequests: state.inference.stats.totalRequests + 1,
        avgTokensPerSecond: Math.round((tokensGenerated / responseTime) * 1000),
        avgResponseTime: responseTime,
      },
    });
  };

  // Handle stopping generation
  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsGenerating(false);
    setStreamingContent('');
  };

  // Handle batch processing
  const handleBatchProcess = async () => {
    const validPrompts = batchPrompts.filter(p => p.trim());
    if (validPrompts.length === 0) return;

    setIsGenerating(true);
    setBatchResults([]);
    setBatchProgress(0);

    try {
      const results = [];
      for (let i = 0; i < validPrompts.length; i++) {
        const prompt = validPrompts[i];
        setBatchProgress(((i + 1) / validPrompts.length) * 100);

        // Simulate processing each prompt
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

        results.push({
          prompt,
          response: `Generated response for: "${prompt}". This is a simulated response from the Llama-GPU backend.`,
          timestamp: new Date(),
          tokensGenerated: Math.floor(Math.random() * 200) + 50,
        });
      }

      setBatchResults(results);
    } catch (error) {
      console.error('Batch processing error:', error);
    } finally {
      setIsGenerating(false);
      setBatchProgress(0);
    }
  };

  // Apply template
  const applyTemplate = (template) => {
    setCurrentMessage(template.prompt);
  };

  // Clear chat
  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your Llama-GPU assistant. How can I help you today?',
        timestamp: new Date(),
        id: Date.now()
      }
    ]);
  };

  // Export chat
  const exportChat = () => {
    const chatData = {
      messages,
      configuration: {
        model: selectedModel,
        backend,
        temperature,
        maxTokens,
        topP,
      },
      performance: performanceMetrics,
      timestamp: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `llama-gpu-chat-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <SmartToy color="primary" />
            <Typography variant="h5" fontWeight="bold">
              Interactive Chat Interface
            </Typography>
            <Chip
              label={`${selectedModel} (${backend})`}
              color="primary"
              size="small"
            />
            {state.quantization.enabled && (
              <Chip
                label={`${state.quantization.type.toUpperCase()}`}
                color="secondary"
                size="small"
              />
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton onClick={exportChat} title="Export Chat">
              <Download />
            </IconButton>
            <IconButton onClick={clearChat} title="Clear Chat">
              <Clear />
            </IconButton>
            <IconButton
              onClick={(e) => setSettingsAnchor(e.currentTarget)}
              title="Settings"
            >
              <Settings />
            </IconButton>
          </Box>
        </Box>

        {/* Mode Selection */}
        <Box sx={{ mt: 2 }}>
          <Tabs value={mode} onChange={(e, newValue) => setMode(newValue)}>
            <Tab icon={<Chat />} label="Chat Mode" />
            <Tab icon={<TextFields />} label="Completion" />
            <Tab icon={<QueuePlayNext />} label="Batch Processing" />
          </Tabs>
        </Box>
      </Paper>

      <Box sx={{ display: 'flex', flex: 1, gap: 2, overflow: 'hidden' }}>
        {/* Main Content */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Messages Area */}
          {mode === 2 ? (
            // Batch Processing Mode
            <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <CardContent sx={{ flex: 1, overflow: 'auto' }}>
                <Typography variant="h6" gutterBottom>
                  Batch Processing
                </Typography>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Prompts ({batchPrompts.filter(p => p.trim()).length})
                  </Typography>
                  {batchPrompts.map((prompt, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                      <TextField
                        fullWidth
                        size="small"
                        value={prompt}
                        onChange={(e) => {
                          const newPrompts = [...batchPrompts];
                          newPrompts[index] = e.target.value;
                          setBatchPrompts(newPrompts);
                        }}
                        placeholder={`Prompt ${index + 1}`}
                      />
                      <IconButton
                        size="small"
                        onClick={() => {
                          const newPrompts = batchPrompts.filter((_, i) => i !== index);
                          setBatchPrompts(newPrompts);
                        }}
                        disabled={batchPrompts.length === 1}
                      >
                        <Clear />
                      </IconButton>
                    </Box>
                  ))}

                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => setBatchPrompts([...batchPrompts, ''])}
                    >
                      Add Prompt
                    </Button>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={handleBatchProcess}
                      disabled={isGenerating || !batchPrompts.some(p => p.trim())}
                      startIcon={isGenerating ? <Stop /> : <PlayArrow />}
                    >
                      {isGenerating ? 'Processing...' : 'Process Batch'}
                    </Button>
                  </Box>

                  {isGenerating && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Progress: {Math.round(batchProgress)}%
                      </Typography>
                      <LinearProgress variant="determinate" value={batchProgress} />
                    </Box>
                  )}
                </Box>

                {batchResults.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Results
                    </Typography>
                    {batchResults.map((result, index) => (
                      <Paper key={index} sx={{ p: 2, mb: 2 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Prompt: {result.prompt}
                        </Typography>
                        <Typography variant="body1">
                          {result.response}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {result.tokensGenerated} tokens • {result.timestamp.toLocaleTimeString()}
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          ) : (
            // Chat/Completion Mode
            <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <CardContent sx={{ flex: 1, overflow: 'auto', p: 1 }}>
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                      mb: 2,
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        backgroundColor: message.role === 'user'
                          ? 'primary.main'
                          : message.isError
                          ? 'error.light'
                          : 'background.paper',
                        color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          display: 'block',
                          mt: 1,
                          opacity: 0.7
                        }}
                      >
                        {message.timestamp.toLocaleTimeString()}
                        {message.responseTime && ` • ${message.responseTime}ms`}
                        {message.tokensGenerated && ` • ${message.tokensGenerated} tokens`}
                      </Typography>
                    </Paper>
                  </Box>
                ))}

                {streamingContent && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                    <Paper elevation={1} sx={{ p: 2, maxWidth: '70%' }}>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {streamingContent}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            backgroundColor: 'primary.main',
                            borderRadius: '50%',
                            animation: 'pulse 1s infinite',
                            mr: 1,
                          }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          Generating...
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                )}

                <div ref={messagesEndRef} />
              </CardContent>

              {/* Input Area */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    multiline
                    minRows={1}
                    maxRows={4}
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={
                      mode === 0
                        ? "Type your message... (Press Enter to send, Shift+Enter for new line)"
                        : "Enter your prompt for text completion..."
                    }
                    disabled={isGenerating}
                  />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {isGenerating ? (
                      <IconButton
                        color="error"
                        onClick={handleStopGeneration}
                        sx={{ height: 56 }}
                      >
                        <Stop />
                      </IconButton>
                    ) : (
                      <IconButton
                        color="primary"
                        onClick={handleSendMessage}
                        disabled={!currentMessage.trim()}
                        sx={{ height: 56 }}
                      >
                        <Send />
                      </IconButton>
                    )}
                  </Box>
                </Box>
              </Box>
            </Card>
          )}
        </Box>

        {/* Sidebar */}
        <Box sx={{ width: 320, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Model Configuration */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Model</InputLabel>
                    <Select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      label="Model"
                    >
                      {state.models.available.map((model) => (
                        <MenuItem key={model} value={model}>
                          {model}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Backend</InputLabel>
                    <Select
                      value={backend}
                      onChange={(e) => setBackend(e.target.value)}
                      label="Backend"
                    >
                      <MenuItem value="ROCm">ROCm (AMD)</MenuItem>
                      <MenuItem value="CUDA">CUDA (NVIDIA)</MenuItem>
                      <MenuItem value="CPU">CPU</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Generation Parameters */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Parameters
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Temperature: {temperature}</Typography>
                <Slider
                  value={temperature}
                  onChange={(e, newValue) => setTemperature(newValue)}
                  min={0.1}
                  max={2.0}
                  step={0.1}
                  size="small"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Max Tokens: {maxTokens}</Typography>
                <Slider
                  value={maxTokens}
                  onChange={(e, newValue) => setMaxTokens(newValue)}
                  min={50}
                  max={2048}
                  step={50}
                  size="small"
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>Top P: {topP}</Typography>
                <Slider
                  value={topP}
                  onChange={(e, newValue) => setTopP(newValue)}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>

          {/* Template Prompts */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Template Prompts
              </Typography>

              <List dense>
                {templates.map((template, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemButton
                      onClick={() => applyTemplate(template)}
                      sx={{ borderRadius: 1 }}
                    >
                      <ListItemText
                        primary={template.name}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          {showPerformance && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <BarChart sx={{ mr: 1 }} />
                  Performance
                </Typography>

                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Tokens/sec
                    </Typography>
                    <Typography variant="h6">
                      {performanceMetrics.tokensPerSecond.toFixed(0)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Response time
                    </Typography>
                    <Typography variant="h6">
                      {performanceMetrics.responseTime}ms
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      GPU Usage
                    </Typography>
                    <Typography variant="h6">
                      {performanceMetrics.gpuUtilization.toFixed(0)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Memory
                    </Typography>
                    <Typography variant="h6">
                      {performanceMetrics.memoryUsage.toFixed(0)}%
                    </Typography>
                  </Grid>
                </Grid>

                {isGenerating && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Generating...
                    </Typography>
                    <LinearProgress />
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>

      {/* Settings Menu */}
      <Menu
        anchorEl={settingsAnchor}
        open={Boolean(settingsAnchor)}
        onClose={() => setSettingsAnchor(null)}
      >
        <MenuItem onClick={() => setShowPerformance(!showPerformance)}>
          <FormControlLabel
            control={<Switch checked={showPerformance} />}
            label="Show Performance"
          />
        </MenuItem>
        <MenuItem onClick={() => setSettingsAnchor(null)}>
          <Typography>Model Settings</Typography>
        </MenuItem>
        <MenuItem onClick={() => setSettingsAnchor(null)}>
          <Typography>Export Settings</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ChatInterface;
