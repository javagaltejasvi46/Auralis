# Frontend Implementation Guide

Complete React Native frontend with authentication and patient management.

## 📦 Required Dependencies

Add to `frontend/package.json`:

```json
{
  "dependencies": {
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-native-async-storage/async-storage": "^1.19.5",
    "react-native-gesture-handler": "~2.14.0",
    "react-native-reanimated": "~3.6.0",
    "react-native-safe-area-context": "4.8.2",
    "react-native-screens": "~3.29.0"
  }
}
```

Install:
```bash
cd frontend
npm install @react-navigation/native @react-navigation/stack
npm install @react-native-async-storage/async-storage
npx expo install react-native-gesture-handler react-native-reanimated react-native-safe-area-context react-native-screens
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.tsx          # Login page
│   │   ├── RegisterScreen.tsx       # Registration
│   │   ├── DashboardScreen.tsx      # Main dashboard
│   │   ├── PatientListScreen.tsx    # List of patients
│   │   ├── PatientProfileScreen.tsx # Patient details
│   │   ├── CreatePatientScreen.tsx  # New patient form
│   │   ├── SessionRecordingScreen.tsx # Recording & transcription
│   │   └── SessionDetailsScreen.tsx # Session view
│   ├── components/
│   │   ├── PatientCard.tsx          # Patient list item
│   │   ├── SessionCard.tsx          # Session list item
│   │   └── LoadingSpinner.tsx       # Loading indicator
│   ├── context/
│   │   └── AuthContext.tsx          # Authentication state
│   ├── services/
│   │   └── api.ts                   # API calls
│   ├── navigation/
│   │   └── AppNavigator.tsx         # Navigation setup
│   ├── types.ts                     # TypeScript types
│   └── config.ts                    # Configuration
└── App.tsx                          # Main app entry
```

## 🎨 Color Palette (Already Configured)

```typescript
export const COLORS = {
  raisinBlack: '#201E1F',
  paleAzure: '#90D7EF',
  ultraviolet: '#6457A6',
  saffron: '#E3B505',
  engineeringOrange: '#B81F00',
  backgroundGradient: ['#201E1F', '#6457A6', '#90D7EF', '#201E1F'],
};
```

## 🔐 Authentication Flow

1. **Login Screen** → Enter credentials
2. **JWT Token** → Stored in AsyncStorage
3. **Dashboard** → Show patient list
4. **Protected Routes** → Require authentication

## 📱 Screen Descriptions

### 1. LoginScreen
- Username/password input
- Login button (Pale Azure)
- Register link
- Gradient background

### 2. DashboardScreen
- Welcome message with therapist name
- Patient count card
- "View Patients" button
- "New Patient" button
- Logout button

### 3. PatientListScreen
- Search bar
- List of patient cards
- Each card shows:
  - Patient name
  - Patient ID
  - Session count
  - Last session date
- Tap to view profile

### 4. PatientProfileScreen
- Patient information
- Session count
- "New Session" button
- List of past sessions
- Edit patient button

### 5. SessionRecordingScreen
- Same as current recording screen
- Language selector
- Record button
- Transcription display
- Save session button
- Automatically links to patient

### 6. CreatePatientScreen
- Form fields:
  - Full name (required)
  - Date of birth
  - Gender
  - Phone
  - Email
  - Address
  - Emergency contact
  - Medical history
  - Notes
- Save button

## 🔄 Data Flow

```
Login → Get Token → Store Token
  ↓
Dashboard → Fetch Patients
  ↓
Select Patient → Fetch Patient Details + Sessions
  ↓
New Session → Record → Transcribe → Save
  ↓
Update Patient Session Count
```

## 🛠️ Implementation Steps

### Step 1: Update package.json
```bash
cd frontend
npm install
```

### Step 2: Update App.tsx
Replace with navigation setup:
```typescript
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
}
```

### Step 3: Create Navigation
```typescript
// src/navigation/AppNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useAuth } from '../context/AuthContext';

const Stack = createStackNavigator();

export default function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingScreen />;
  }
  
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        ) : (
          <>
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="PatientList" component={PatientListScreen} />
            <Stack.Screen name="PatientProfile" component={PatientProfileScreen} />
            <Stack.Screen name="CreatePatient" component={CreatePatientScreen} />
            <Stack.Screen name="SessionRecording" component={SessionRecordingScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Step 4: Create Screens
Each screen follows this pattern:
```typescript
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../config';

export default function ScreenName() {
  return (
    <LinearGradient
      colors={COLORS.backgroundGradient}
      locations={[0, 0.3, 0.7, 1]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      {/* Screen content */}
    </LinearGradient>
  );
}
```

## 🎯 Key Features

### Authentication
- ✅ JWT token-based
- ✅ Persistent login (AsyncStorage)
- ✅ Auto-logout on token expiry
- ✅ Protected routes

### Patient Management
- ✅ Create patient profiles
- ✅ View patient list
- ✅ Search patients
- ✅ Edit patient info
- ✅ Soft delete

### Session Management
- ✅ Create new sessions
- ✅ Record audio
- ✅ Real-time transcription
- ✅ Save transcriptions
- ✅ View session history
- ✅ Session counter

### UI/UX
- ✅ Consistent color palette
- ✅ Smooth animations
- ✅ Loading states
- ✅ Error handling
- ✅ Responsive design

## 🔒 Security

- Tokens stored securely in AsyncStorage
- API calls include Authorization header
- Sensitive data encrypted
- HIPAA-compliant architecture

## 📝 API Integration

All API calls use the service layer:
```typescript
import { patientAPI, sessionAPI } from '../services/api';

// Get patients
const { patients } = await patientAPI.getAll();

// Create session
const { session } = await sessionAPI.create({
  patient_id: patientId,
  language: 'hindi',
  original_transcription: text,
});
```

## 🧪 Testing

```bash
# Start backend
cd backend
python main.py  # Port 8002
python transcription_server.py  # Port 8003

# Start frontend
cd frontend
npx expo start

# Test flow:
1. Register new therapist
2. Login
3. Create patient
4. Start session
5. Record & transcribe
6. Save session
7. View patient profile
```

## 🚀 Next Steps

1. Install dependencies
2. Update IP address in `src/config.ts`
3. Create all screen files
4. Test authentication flow
5. Test patient creation
6. Test session recording

## 📱 Screenshots Layout

### Login Screen
```
┌─────────────────────┐
│   AURALIS Logo      │
│ Hear.Understand.Heal│
│                     │
│  [Username Input]   │
│  [Password Input]   │
│                     │
│   [Login Button]    │
│                     │
│  Don't have account?│
│     Register        │
└─────────────────────┘
```

### Dashboard
```
┌─────────────────────┐
│ Welcome, Dr. Smith  │
│     [Logout]        │
│                     │
│ ┌─────────────────┐ │
│ │ Total Patients  │ │
│ │      15         │ │
│ └─────────────────┘ │
│                     │
│ [View All Patients] │
│ [New Patient]       │
└─────────────────────┘
```

### Patient List
```
┌─────────────────────┐
│  [Search...]        │
│                     │
│ ┌─────────────────┐ │
│ │ Jane Doe        │ │
│ │ P20241116ABC    │ │
│ │ 3 Sessions      │ │
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ John Smith      │ │
│ │ P20241116XYZ    │ │
│ │ 5 Sessions      │ │
│ └─────────────────┘ │
└─────────────────────┘
```

---

**All files have been created in `frontend/src/`. Ready to implement the screens!**
