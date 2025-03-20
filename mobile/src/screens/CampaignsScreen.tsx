import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import axios from 'axios';

interface Campaign {
  id: number;
  title: string;
  description: string;
}

const CampaignsScreen = ({ navigation }: any) => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get('http://your-api-url/api/campaigns');
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      // TODO: Add error handling UI
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchCampaigns();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const renderCampaign = ({ item }: { item: Campaign }) => (
    <TouchableOpacity
      style={styles.campaignCard}
      onPress={() => navigation.navigate('CampaignDetail', { id: item.id })}
    >
      <Text style={styles.campaignTitle}>{item.title}</Text>
      <Text style={styles.campaignDescription}>{item.description}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={campaigns}
        renderItem={renderCampaign}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.listContainer}
      />
      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate('CreateCampaign')}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#242527',
  },
  listContainer: {
    padding: 16,
  },
  campaignCard: {
    backgroundColor: '#383838',
    padding: 16,
    marginBottom: 12,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  campaignTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  campaignDescription: {
    color: '#CCCCCC',
    fontSize: 14,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
    backgroundColor: '#E40712',
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  fabText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default CampaignsScreen; 