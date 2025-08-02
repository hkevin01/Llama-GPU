// Test script to validate imports
const { execSync } = require('child_process');

try {
  console.log('Testing ChatInterface component compilation...');
  execSync('npx babel src/components/Pages/ChatInterface.js --out-file /tmp/test.js --presets @babel/preset-react', {
    cwd: '/home/kevin/Projects/Llama-GPU/llama-gui',
    stdio: 'pipe'
  });
  console.log('✅ ChatInterface compiles successfully!');

  console.log('Testing App.js compilation...');
  execSync('npx babel src/App.js --out-file /tmp/test-app.js --presets @babel/preset-react', {
    cwd: '/home/kevin/Projects/Llama-GPU/llama-gui',
    stdio: 'pipe'
  });
  console.log('✅ App.js compiles successfully!');

  console.log('All components compile without errors!');
} catch (error) {
  console.error('❌ Compilation error:', error.message);
}
