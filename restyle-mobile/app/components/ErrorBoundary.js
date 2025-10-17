import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, retryCount: 0 };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Only log in development, use proper error tracking in production
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
    // In production, send to error tracking service (e.g., Sentry)
    // Example: Sentry.captureException(error, { extra: errorInfo });
  }

  handleReset = () => {
    // Prevent infinite retry loops - max 3 attempts
    const newRetryCount = this.state.retryCount + 1;
    if (newRetryCount >= 3) {
      // After 3 retries, keep error state
      return;
    }
    this.setState({ hasError: false, retryCount: newRetryCount });
  };

  render() {
    if (this.state.hasError) {
      const attemptsLeft = 3 - this.state.retryCount;
      return (
        <View style={styles.container}>
          <Text style={styles.title}>Oops! Something went wrong</Text>
          {attemptsLeft > 0 ? (
            <TouchableOpacity style={styles.button} onPress={this.handleReset}>
              <Text style={styles.buttonText}>
                Try Again {this.state.retryCount > 0 ? `(${attemptsLeft} left)` : ''}
              </Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.subtitle}>
              Please restart the app or contact support.
            </Text>
          )}
        </View>
      );
    }
    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#666', marginTop: 10, textAlign: 'center' },
  button: { backgroundColor: '#1A73E8', padding: 14, borderRadius: 8, marginTop: 10 },
  buttonText: { color: 'white', fontSize: 16, fontWeight: '600', textAlign: 'center' },
});

export default ErrorBoundary;
