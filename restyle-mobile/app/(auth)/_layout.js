import React from 'react';
import { Redirect, Stack } from 'expo-router';
import { useAuthStore } from '../../shared/authStore';

// This layout handles the authentication screens.
export default function AuthLayout() {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    // If a user who is already logged in tries to visit a screen in this group,
    // redirect them away to the main dashboard.
    return <Redirect href="/dashboard" />;
  }

  // If the user is not authenticated, show the screens in this group (e.g., login).
  return <Stack screenOptions={{ headerShown: false }} />;
} 