import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/FontAwesome';

// Screens
import CampaignsScreen from './src/screens/CampaignsScreen';
import EncountersScreen from './src/screens/EncountersScreen';
import NPCsScreen from './src/screens/NPCsScreen';
import LootScreen from './src/screens/LootScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';

// Types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type MainTabParamList = {
  Campaigns: undefined;
  Encounters: undefined;
  NPCs: undefined;
  Loot: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

const AuthNavigator = () => (
  <AuthStack.Navigator>
    <AuthStack.Screen name="Login" component={LoginScreen} />
    <AuthStack.Screen name="Register" component={RegisterScreen} />
  </AuthStack.Navigator>
);

const MainNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ color, size }) => {
        let iconName: string;

        switch (route.name) {
          case 'Campaigns':
            iconName = 'book';
            break;
          case 'Encounters':
            iconName = 'shield';
            break;
          case 'NPCs':
            iconName = 'users';
            break;
          case 'Loot':
            iconName = 'treasure-chest';
            break;
          default:
            iconName = 'question';
        }

        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#E40712',
      tabBarInactiveTintColor: '#666666',
      tabBarStyle: {
        backgroundColor: '#1A1A1A',
        borderTopColor: '#383838',
      },
      headerStyle: {
        backgroundColor: '#1A1A1A',
      },
      headerTintColor: '#FFFFFF',
    })}
  >
    <Tab.Screen name="Campaigns" component={CampaignsScreen} />
    <Tab.Screen name="Encounters" component={EncountersScreen} />
    <Tab.Screen name="NPCs" component={NPCsScreen} />
    <Tab.Screen name="Loot" component={LootScreen} />
  </Tab.Navigator>
);

const App = () => {
  // TODO: Add authentication state management
  const isAuthenticated = false;

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App; 