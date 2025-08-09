import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function StatisticalDetails({ stats }) {
    const conditionData = stats?.by_condition;
    if (!conditionData || Object.keys(conditionData).length === 0) return null;
    
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Market Analysis Breakdown</Text>
            {Object.entries(conditionData).map(([condition, data]) => (
                <View key={condition} style={styles.conditionBlock}>
                    <Text style={styles.conditionTitle}>{condition}</Text>
                    <Text style={styles.detailText}>Comps Analyzed: {data.num_comps}</Text>
                    <Text style={styles.detailText}>Avg. Sold Price (Weighted): ${data.weighted_mean_price.toFixed(2)}</Text>
                    <Text style={styles.detailText}>
                        Sold Price Range: ${data.price_range[0].toFixed(2)} - ${data.price_range[1].toFixed(2)}
                    </Text>
                </View>
            ))}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { padding: 15, backgroundColor: '#f9f9f9', borderRadius: 10, marginVertical: 10 },
    title: { fontSize: 18, fontWeight: 'bold', marginBottom: 10, color: '#333' },
    conditionBlock: { marginBottom: 10, borderTopWidth: 1, borderTopColor: '#eee', paddingTop: 10 },
    conditionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 5, color: '#1A73E8' },
    detailText: { fontSize: 14, color: '#555', lineHeight: 20 },
});