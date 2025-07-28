import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { View, Text } from 'react-native';
import { Link } from 'expo-router';

export default function AuthIndex() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/(auth)/login');
  }, [router]);
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>Welcome to Restyle.ai</Text>
      <Link href="/login" style={{ fontSize: 18, color: '#a259f7', marginBottom: 10 }}>Login</Link>
      <Link href="/DebugApiScreen" style={{ fontSize: 16, color: '#888', marginTop: 20 }}>Debug API Screen</Link>
    </View>
  );
} 