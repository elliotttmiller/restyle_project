const { spawn } = require('child_process');
const path = require('path');

// Ensure we're in the correct directory
process.chdir(__dirname);

// Set environment variables
process.env.EXPO_PROJECT_ROOT = __dirname;

console.log('Starting Expo from:', __dirname);
console.log('Project root:', process.env.EXPO_PROJECT_ROOT);

// Start Expo
const expo = spawn('npx', ['expo', 'start', '--clear'], {
  stdio: 'inherit',
  shell: true,
  cwd: __dirname
});

expo.on('error', (error) => {
  console.error('Failed to start Expo:', error);
  process.exit(1);
});

expo.on('exit', (code) => {
  console.log(`Expo exited with code ${code}`);
  process.exit(code);
}); 