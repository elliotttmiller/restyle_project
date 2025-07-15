const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Ensure the project root is correctly set
config.projectRoot = __dirname;

// Add resolver configuration
config.resolver = {
  ...config.resolver,
  alias: {
    // Ensure App.js is resolved correctly
    'App': './App.js',
  },
  // Ensure the main entry point is resolved correctly
  mainFields: ['main', 'module'],
};

module.exports = config; 