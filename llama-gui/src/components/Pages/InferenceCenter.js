import {
    Clear,
    PlayArrow,
    Psychology,
    Send,
    Settings,
    Stop
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Divider,
    FormControlLabel,
    Grid,
    IconButton,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    Paper,
    Slider,
    Switch,
    TextField,
    Typography
} from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function InferenceCenter() {
  const { state, dispatch } = useAppContext();
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [batchPrompts, setBatchPrompts] = useState(['']);
  const [batchMode, setBatchMode] = useState(false);

  // Generation parameters
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(100);
  const [topP, setTopP] = useState(0.9);
  const [topK, setTopK] = useState(40);
  const [repetitionPenalty, setRepetitionPenalty] = useState(1.1);

  const outputRef = useRef(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const handleGenerate = async () => {
    if (!prompt.trim() || !state.models.loaded) return;

    setIsGenerating(true);
    setOutput('');

    // Simulate streaming inference
    const words = [
      'The', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog.',
      'This', 'is', 'a', 'demonstration', 'of', 'streaming', 'text', 'generation',
      'with', 'the', 'Llama-GPU', 'inference', 'system.', 'The', 'model',
      'processes', 'tokens', 'in', 'real-time', 'and', 'displays', 'results',
      'as', 'they', 'are', 'generated.', 'Performance', 'metrics', 'are',
      'tracked', 'continuously.', 'This', 'allows', 'for', 'efficient',
      'monitoring', 'of', 'inference', 'speed', 'and', 'quality.'
    ];

    dispatch({
      type: 'ADD_ACTIVE_REQUEST',
      payload: {
        id: Date.now(),
        prompt: prompt.substring(0, 50) + '...',
        status: 'generating',
        startTime: Date.now(),
      }
    });

    let currentOutput = '';
    for (let i = 0; i < words.length && isGenerating; i++) {
      await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
      currentOutput += (i > 0 ? ' ' : '') + words[i];
      setOutput(currentOutput);

      // Update performance stats
      dispatch({
        type: 'UPDATE_INFERENCE_STATS',
        payload: {
          tokensGenerated: i + 1,
          timeElapsed: Date.now() - performance.now(),
        }
      });
    }

    setIsGenerating(false);
    dispatch({ type: 'REMOVE_ACTIVE_REQUEST', payload: Date.now() });
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Generation Complete',
        message: `Generated ${words.length} tokens`,
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const handleStop = () => {
    setIsGenerating(false);
  };

  const handleClear = () => {
    setPrompt('');
    setOutput('');
  };

  const addBatchPrompt = () => {
    setBatchPrompts([...batchPrompts, '']);
  };

  const updateBatchPrompt = (index, value) => {
    const updated = [...batchPrompts];
    updated[index] = value;
    setBatchPrompts(updated);
  };

  const removeBatchPrompt = (index) => {
    setBatchPrompts(batchPrompts.filter((_, i) => i !== index));
  };

  const handleBatchGenerate = async () => {
    const validPrompts = batchPrompts.filter(p => p.trim());
    if (validPrompts.length === 0) return;

    setIsGenerating(true);

    // Simulate batch processing
    for (let i = 0; i < validPrompts.length; i++) {
      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          title: 'Batch Processing',
          message: `Processing prompt ${i + 1} of ${validPrompts.length}`,
          type: 'info',
          timestamp: new Date().toLocaleTimeString(),
        }
      });

      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    setIsGenerating(false);
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Batch Complete',
        message: `Processed ${validPrompts.length} prompts`,
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Inference Center
      </Typography>

      {!state.models.loaded && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No model loaded. Please load a model in the Model Manager first.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Main Inference Panel */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">
                  {batchMode ? 'Batch Inference' : 'Single Inference'}
                </Typography>
                <Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={batchMode}
                        onChange={(e) => setBatchMode(e.target.checked)}
                      />
                    }
                    label="Batch Mode"
                  />
                  <IconButton onClick={() => setShowAdvanced(!showAdvanced)}>
                    <Settings />
                  </IconButton>
                </Box>
              </Box>

              {!batchMode ? (
                <>
                  {/* Single Inference */}
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Enter your prompt here..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    sx={{ mb: 2 }}
                  />

                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<Send />}
                      onClick={handleGenerate}
                      disabled={!prompt.trim() || !state.models.loaded || isGenerating}
                    >
                      Generate
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Stop />}
                      onClick={handleStop}
                      disabled={!isGenerating}
                    >
                      Stop
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Clear />}
                      onClick={handleClear}
                    >
                      Clear
                    </Button>
                  </Box>

                  {/* Output */}
                  <Paper
                    ref={outputRef}
                    sx={{
                      p: 2,
                      minHeight: 200,
                      maxHeight: 400,
                      overflow: 'auto',
                      backgroundColor: 'grey.50',
                      border: '1px solid',
                      borderColor: 'grey.300',
                    }}
                  >
                    {output ? (
                      <Typography variant="body1" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                        {output}
                        {isGenerating && (
                          <Box component="span" sx={{
                            display: 'inline-block',
                            width: '2px',
                            height: '1.2em',
                            backgroundColor: 'primary.main',
                            animation: 'blink 1s infinite',
                            ml: 0.5,
                            '@keyframes blink': {
                              '0%, 50%': { opacity: 1 },
                              '51%, 100%': { opacity: 0 },
                            },
                          }} />
                        )}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        Generated text will appear here...
                      </Typography>
                    )}
                  </Paper>
                </>
              ) : (
                <>
                  {/* Batch Inference */}
                  <Typography variant="subtitle2" gutterBottom>
                    Batch Prompts
                  </Typography>
                  {batchPrompts.map((prompt, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <TextField
                        fullWidth
                        placeholder={`Prompt ${index + 1}...`}
                        value={prompt}
                        onChange={(e) => updateBatchPrompt(index, e.target.value)}
                      />
                      <IconButton
                        onClick={() => removeBatchPrompt(index)}
                        disabled={batchPrompts.length === 1}
                      >
                        <Clear />
                      </IconButton>
                    </Box>
                  ))}

                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Button variant="outlined" onClick={addBatchPrompt}>
                      Add Prompt
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<PlayArrow />}
                      onClick={handleBatchGenerate}
                      disabled={!batchPrompts.some(p => p.trim()) || !state.models.loaded || isGenerating}
                    >
                      Start Batch
                    </Button>
                  </Box>
                </>
              )}

              {isGenerating && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Parameters Panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generation Parameters
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>Temperature: {temperature}</Typography>
                <Slider
                  value={temperature}
                  onChange={(_, value) => setTemperature(value)}
                  min={0.1}
                  max={2.0}
                  step={0.1}
                  marks={[
                    { value: 0.1, label: '0.1' },
                    { value: 1.0, label: '1.0' },
                    { value: 2.0, label: '2.0' },
                  ]}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>Max Tokens: {maxTokens}</Typography>
                <Slider
                  value={maxTokens}
                  onChange={(_, value) => setMaxTokens(value)}
                  min={10}
                  max={512}
                  step={10}
                  marks={[
                    { value: 10, label: '10' },
                    { value: 256, label: '256' },
                    { value: 512, label: '512' },
                  ]}
                />
              </Box>

              {showAdvanced && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Advanced Parameters
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Top P: {topP}</Typography>
                    <Slider
                      value={topP}
                      onChange={(_, value) => setTopP(value)}
                      min={0.1}
                      max={1.0}
                      step={0.05}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Top K: {topK}</Typography>
                    <Slider
                      value={topK}
                      onChange={(_, value) => setTopK(value)}
                      min={1}
                      max={100}
                      step={1}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Repetition Penalty: {repetitionPenalty}</Typography>
                    <Slider
                      value={repetitionPenalty}
                      onChange={(_, value) => setRepetitionPenalty(value)}
                      min={1.0}
                      max={2.0}
                      step={0.05}
                    />
                  </Box>
                </>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Current Stats */}
              <Typography variant="subtitle2" gutterBottom>
                Performance Stats
              </Typography>

              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Speed: {state.inference.stats.avgTokensPerSecond.toFixed(1)} tokens/s
                </Typography>
              </Box>

              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Active Requests: {state.inference.activeRequests.length}
                </Typography>
              </Box>

              {state.models.loaded && (
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={`${state.models.loaded.name} (${state.models.loaded.backend})`}
                    color="primary"
                    size="small"
                    icon={<Psychology />}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Active Requests */}
        {state.inference.activeRequests.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Requests
                </Typography>
                <List>
                  {state.inference.activeRequests.map((request) => (
                    <ListItem key={request.id}>
                      <ListItemText
                        primary={request.prompt}
                        secondary={`Status: ${request.status} | Started: ${new Date(request.startTime).toLocaleTimeString()}`}
                      />
                      <IconButton onClick={() => dispatch({ type: 'REMOVE_ACTIVE_REQUEST', payload: request.id })}>
                        <Stop />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default InferenceCenter;
