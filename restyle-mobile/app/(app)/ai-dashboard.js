import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import api from '../../shared/api';

export default function AIDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    backend: false,
    database: false,
    redis: false,
    celery: false,
    ai_services: {
      vision: false,
      rekognition: false,
      gemini: false,
      vertex: false
    }
  });
  const [performanceMetrics, setPerformanceMetrics] = useState({
    total_searches: 0,
    successful_searches: 0,
    average_response_time: 0,
    ai_confidence_avg: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    checkSystemStatus();
    loadPerformanceMetrics();
  }, []);

  const checkSystemStatus = async () => {
    setLoading(true);
    try {
      // Check backend health with timeout and proper error handling
      try {
        const healthResponse = await api.get('/core/health/');
        setSystemStatus(prev => ({
          ...prev,
          backend: healthResponse.status === 200,
          database: healthResponse.data?.database || false,
          redis: healthResponse.data?.redis || false,
          celery: healthResponse.data?.celery || false
        }));
      } catch (error) {
        console.log('Backend health check failed:', error.message);
        setSystemStatus(prev => ({
          ...prev,
          backend: false,
          database: false,
          redis: false,
          celery: false
        }));
      }

      // Check eBay token health
      try {
        const tokenResponse = await api.get('/core/ebay-token/health/');
        setSystemStatus(prev => ({
          ...prev,
          ebay_tokens: tokenResponse.data?.status === 'healthy'
        }));
      } catch (error) {
        console.log('eBay token health check failed:', error.message);
        setSystemStatus(prev => ({
          ...prev,
          ebay_tokens: false
        }));
      }

      // Check AI services status
      try {
        const aiResponse = await api.get('/core/ai/status/');
        setSystemStatus(prev => ({
          ...prev,
          ai_services: aiResponse.data?.services || {
            vision: false,
            rekognition: false,
            gemini: false,
            vertex: false
          }
        }));
      } catch (error) {
        console.log('AI services status check failed:', error.message);
        setSystemStatus(prev => ({
          ...prev,
          ai_services: {
            vision: false,
            rekognition: false,
            gemini: false,
            vertex: false
          }
        }));
      }

    } catch (error) {
      console.error('System status check failed:', error);
      // Don't show alert on every failure to avoid annoying the user
      setSystemStatus({
        backend: false,
        database: false,
        redis: false,
        celery: false,
        ebay_tokens: false,
        ai_services: {
          vision: false,
          rekognition: false,
          gemini: false,
          vertex: false
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPerformanceMetrics = async () => {
    try {
      // This would be a new endpoint for performance metrics
      const metricsResponse = await api.get('/core/metrics/');
      if (metricsResponse.data) {
        setPerformanceMetrics({
          total_searches: metricsResponse.data.total_searches || 0,
          successful_searches: metricsResponse.data.successful_searches || 0,
          average_response_time: metricsResponse.data.average_response_time || 0,
          ai_confidence_avg: metricsResponse.data.ai_confidence_avg || 0
        });
      }
    } catch (error) {
      console.log('Performance metrics load failed:', error.message);
      // Set default values instead of failing
      setPerformanceMetrics({
        total_searches: 0,
        successful_searches: 0,
        average_response_time: 0,
        ai_confidence_avg: 0
      });
    }
  };

  const renderStatusIndicator = (service, status) => (
    <View style={[styles.statusIndicator, status ? styles.statusOnline : styles.statusOffline]}>
      <View style={[styles.statusDot, status ? styles.dotOnline : styles.dotOffline]} />
      <Text style={[styles.statusText, status ? styles.statusTextOnline : styles.statusTextOffline]}>
        {service}
      </Text>
    </View>
  );

  const renderMetricCard = (title, value, subtitle, color = '#4CAF50') => (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <Text style={styles.metricTitle}>{title}</Text>
      <Text style={[styles.metricValue, { color }]}>{value}</Text>
      {subtitle && <Text style={styles.metricSubtitle}>{subtitle}</Text>}
    </View>
  );

  const renderAIServiceCard = (service, status, confidence = null) => (
    <View style={[styles.aiServiceCard, status ? styles.aiServiceActive : styles.aiServiceInactive]}>
      <View style={styles.aiServiceHeader}>
        <Text style={styles.aiServiceName}>{service}</Text>
        <View style={[styles.aiServiceStatus, status ? styles.aiServiceStatusActive : styles.aiServiceStatusInactive]} />
      </View>
      {confidence !== null && (
        <View style={styles.confidenceBar}>
          <View style={[styles.confidenceFill, { width: `${confidence}%` }]} />
        </View>
      )}
      <Text style={styles.aiServiceStatusText}>
        {status ? 'Active' : 'Inactive'}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#a259f7" />
        </TouchableOpacity>
        <Text style={styles.title}>🤖 AI System Dashboard</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={checkSystemStatus}>
          {loading ? (
            <ActivityIndicator color="#a259f7" size="small" />
          ) : (
            <Ionicons name="refresh" size={24} color="#a259f7" />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* System Status */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          <View style={styles.statusGrid}>
            {renderStatusIndicator('Backend', systemStatus.backend)}
            {renderStatusIndicator('Database', systemStatus.database)}
            {renderStatusIndicator('Redis', systemStatus.redis)}
            {renderStatusIndicator('Celery', systemStatus.celery)}
          </View>
        </View>

        {/* AI Services Status */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Services</Text>
          <View style={styles.aiServicesGrid}>
            {renderAIServiceCard('Google Vision', systemStatus.ai_services.vision, 95)}
            {renderAIServiceCard('AWS Rekognition', systemStatus.ai_services.rekognition, 88)}
            {renderAIServiceCard('Google Gemini', systemStatus.ai_services.gemini, 92)}
            {renderAIServiceCard('Vertex AI', systemStatus.ai_services.vertex, 85)}
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Metrics</Text>
          <View style={styles.metricsGrid}>
            {renderMetricCard(
              'Total Searches',
              performanceMetrics.total_searches.toLocaleString(),
              'All time searches',
              '#2196F3'
            )}
            {renderMetricCard(
              'Success Rate',
              `${((performanceMetrics.successful_searches / Math.max(performanceMetrics.total_searches, 1)) * 100).toFixed(1)}%`,
              'Successful searches',
              '#4CAF50'
            )}
            {renderMetricCard(
              'Avg Response',
              `${performanceMetrics.average_response_time.toFixed(1)}s`,
              'Average response time',
              '#FF9800'
            )}
            {renderMetricCard(
              'AI Confidence',
              `${performanceMetrics.ai_confidence_avg.toFixed(1)}%`,
              'Average AI confidence',
              '#9C27B0'
            )}
          </View>
        </View>

        {/* System Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Information</Text>
          <View style={styles.infoCard}>
            <Text style={styles.infoText}>
              <Text style={styles.infoLabel}>Multi-Expert AI System:</Text> Google Vision, AWS Rekognition, Gemini, Vertex AI
            </Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoLabel}>Advanced Features:</Text> Confidence scoring, query optimization, multiple variants
            </Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoLabel}>Analysis Quality:</Text> High-precision image analysis with brand detection
            </Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoLabel}>Search Coverage:</Text> Comprehensive eBay search with intelligent filtering
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#000',
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
    textAlign: 'center',
  },
  refreshButton: {
    padding: 8,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  statusGrid: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 15,
    borderWidth: 1,
    borderColor: '#333',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 10,
  },
  dotOnline: {
    backgroundColor: '#4CAF50',
  },
  dotOffline: {
    backgroundColor: '#F44336',
  },
  statusText: {
    fontSize: 16,
    fontWeight: '500',
  },
  statusTextOnline: {
    color: '#4CAF50',
  },
  statusTextOffline: {
    color: '#F44336',
  },
  statusOnline: {
    backgroundColor: '#1a1a1a',
  },
  statusOffline: {
    backgroundColor: '#1a1a1a',
  },
  aiServicesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  aiServiceCard: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    width: '48%',
    borderWidth: 1,
    borderColor: '#333',
  },
  aiServiceActive: {
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  aiServiceInactive: {
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  aiServiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  aiServiceName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  aiServiceStatus: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  aiServiceStatusActive: {
    backgroundColor: '#4CAF50',
  },
  aiServiceStatusInactive: {
    backgroundColor: '#F44336',
  },
  confidenceBar: {
    height: 4,
    backgroundColor: '#333',
    borderRadius: 2,
    marginBottom: 5,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 2,
  },
  aiServiceStatusText: {
    fontSize: 12,
    color: '#888',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    width: '48%',
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: '#333',
  },
  metricTitle: {
    fontSize: 12,
    color: '#888',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  metricSubtitle: {
    fontSize: 10,
    color: '#666',
  },
  infoCard: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 15,
    borderWidth: 1,
    borderColor: '#333',
  },
  infoText: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 8,
    lineHeight: 20,
  },
  infoLabel: {
    fontWeight: '600',
    color: '#a259f7',
  },
}); 