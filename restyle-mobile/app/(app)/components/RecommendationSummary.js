import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function RecommendationSummary({ recommendation }) {
    if (!recommendation) return null;
    
    return (
        <View style={styles.container}>
            <Text style={styles.priceLabel}>Suggested Price</Text>
            <Text style={styles.price}>${recommendation.suggested_price?.toFixed(2)}</Text>
            <View style={styles.rangeContainer}>
                <Text style={styles.rangeLabel}>Price Range:</Text>
                <Text style={styles.rangeValue}>
                    ${recommendation.suggested_price_range?.[0]?.toFixed(2)} - ${recommendation.suggested_price_range?.[1]?.toFixed(2)}
                </Text>
            </View>
            <Text style={styles.summaryText}>{recommendation.summary}</Text>
            <View style={[styles.confidenceBadge, styles[recommendation.confidence?.toLowerCase()]]}>
                <Text style={styles.confidenceText}>{recommendation.confidence} Confidence</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { 
        padding: 20, 
        backgroundColor: '#fff', 
        borderRadius: 10, 
        marginVertical: 10, 
        alignItems: 'center', 
        shadowColor: '#000', 
        shadowOffset: { width: 0, height: 2 }, 
        shadowOpacity: 0.1, 
        shadowRadius: 4, 
        elevation: 3 
    },
    priceLabel: { fontSize: 16, color: '#666' },
    price: { fontSize: 48, fontWeight: 'bold', color: '#1A73E8', marginVertical: 5 },
    rangeContainer: { flexDirection: 'row', alignItems: 'center' },
    rangeLabel: { fontSize: 16, color: '#333' },
    rangeValue: { fontSize: 16, fontWeight: '600', marginLeft: 5 },
    summaryText: { fontSize: 14, color: '#444', textAlign: 'center', marginTop: 15, lineHeight: 20 },
    confidenceBadge: { marginTop: 15, paddingVertical: 5, paddingHorizontal: 15, borderRadius: 15 },
    confidenceText: { color: '#fff', fontWeight: 'bold' },
    high: { backgroundColor: '#28a745' },
    medium: { backgroundColor: '#ffc107' },
    low: { backgroundColor: '#dc3545' },
});