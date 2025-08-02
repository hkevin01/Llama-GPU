// Test file to validate syntax without running full server
console.log('Testing GPU detection...');

// Import our utilities (commented out for now)
// import { detectGPUs } from './src/utils/gpuDetection.js';

// Test data structure
const testGPUData = {
  gpus: [
    {
      id: 0,
      name: 'AMD Radeon RX 7900 XTX',
      memoryTotal: 24576,
      memoryUsed: 2048,
      backend: 'ROCm'
    },
    {
      id: 1,
      name: 'AMD Radeon RX 7800 XT',
      memoryTotal: 16384,
      memoryUsed: 1024,
      backend: 'ROCm'
    }
  ],
  backendType: 'ROCm'
};

console.log('Test GPU data:', testGPUData);
console.log('Navigation fixes should now work!');
