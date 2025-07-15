import { Redirect } from 'expo-router';

// The index route immediately tries to send the user to the main app dashboard.
// The gatekeeper at (app)/_layout.js will then check if this is allowed.
// If not, it will redirect them to /login.
export default function Index() {
  return <Redirect href="/dashboard" />;
} 