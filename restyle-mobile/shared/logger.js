// shared/logger.js
// Simple cross-platform logger for Node.js and React Native

const levels = ['error', 'warn', 'info', 'debug'];

function log(level, ...args) {
  if (typeof console[level] === 'function') {
    console[level](...args);
  } else {
    console.log(`[${level.toUpperCase()}]`, ...args);
  }
}

module.exports = {
  error: (...args) => log('error', ...args),
  warn: (...args) => log('warn', ...args),
  info: (...args) => log('info', ...args),
  debug: (...args) => log('debug', ...args),
};
