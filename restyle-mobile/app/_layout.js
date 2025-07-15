import { Stack } from 'expo-router';

// This is the root layout. It has NO logic.
// It unconditionally renders a Stack navigator, which satisfies Expo Router's requirement.
// This navigator will then render either the (app) or (auth) layout as a screen.
export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(app)" />
      <Stack.Screen name="(auth)" />
    </Stack>
  );
}