# Auralis Frontend

React Native mobile application for medical voice transcription and therapy session management.

## Features

- 📱 **Cross-Platform** - iOS and Android support via Expo
- 🎨 **Modern UI** - Parchment/Dark Teal/Cool Steel color scheme
- 🔐 **Secure Authentication** - JWT-based login system
- 👥 **Patient Management** - Create, view, and manage patients
- 🎤 **Real-Time Recording** - Live transcription with WebSocket
- 🌍 **Multilingual** - Auto-translation to English
- 🤖 **AI Summaries** - Professional therapy session summaries
- 📝 **Clinical Notes** - Add observations and treatment plans
- 🎯 **Risk Highlighting** - Automatic flagging of sensitive keywords

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Backend URL

The app auto-configures when backend starts, or manually edit:

`src/config.ts`:
```typescript
export const API_BASE_URL = 'http://YOUR_IP:8002';
export const WS_BASE_URL = 'ws://YOUR_IP:8003';
```

### 3. Start Development Server

```bash
npx expo start
```

### 4. Run on Device

**Option A: Expo Go App**
1. Install Expo Go on your phone
2. Scan QR code from terminal
3. App loads automatically

**Option B: Emulator**
```bash
# Android
npx expo start --android

# iOS (Mac only)
npx expo start --ios
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   └── SummaryRenderer.tsx
│   ├── screens/            # App screens
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── PatientListScreen.tsx
│   │   ├── PatientProfileScreen.tsx
│   │   ├── SessionRecordingScreen.tsx
│   │   └── SessionDetailScreen.tsx
│   ├── services/           # API services
│   │   └── api.ts
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   └── config.ts           # Configuration
├── assets/                 # Images and fonts
├── App.tsx                 # Main app component
└── package.json           # Dependencies
```

## Screens

### Authentication
- **LoginScreen** - Therapist login
- **RegisterScreen** - New therapist registration

### Patient Management
- **PatientListScreen** - View all patients
- **PatientProfileScreen** - Patient details, sessions, summaries

### Session Management
- **SessionRecordingScreen** - Record and transcribe sessions
- **SessionDetailScreen** - View transcription and notes

## Features in Detail

### Real-Time Transcription
```typescript
// WebSocket connection
const ws = new WebSocket(WS_BASE_URL);

// Send audio chunks
ws.send(JSON.stringify({
  audio: base64Audio,
  language: 'hindi'
}));

// Receive transcription
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.text); // Transcribed text
};
```

### AI Summary Rendering
The app uses a custom `SummaryRenderer` component that:
- Renders **bold** text from markdown
- Highlights {{RED:urgent}} keywords in red
- Supports React Native Text components

Example:
```typescript
<SummaryRenderer 
  summary={summary} 
  style={styles.summaryText} 
/>
```

### Patient Management
```typescript
// Create patient
await patientAPI.create({
  full_name: "John Doe",
  patient_id: "P001",
  phone: "1234567890",
  email: "john@example.com"
});

// Get patient with sessions
const { patient } = await patientAPI.getById(id, true);
```

### Session Recording
```typescript
// Start recording
const recording = await Audio.Recording.createAsync(
  Audio.RecordingOptionsPresets.HIGH_QUALITY
);

// Get audio URI
const uri = recording.getURI();

// Upload to backend
await sessionAPI.uploadAudio(sessionId, uri);
```

## Color Scheme

### Theme Colors
```typescript
export const COLORS = {
  // Main palette
  parchment: '#F2EFEB',        // Background
  darkTeal: '#113845',          // Sections/Cards
  coolSteel: '#85A3B3',         // Buttons/Text
  
  // UI
  cardBackground: 'rgba(17, 56, 69, 0.95)',
  borderColor: 'rgba(133, 163, 179, 0.5)',
  textPrimary: '#85A3B3',
  textOnDarkTeal: '#FFFFFF',
  buttonBackground: '#85A3B3',
  buttonText: '#FFFFFF',
  
  // Status
  success: '#4ade80',
  error: '#ef4444',
  warning: '#fbbf24',
};
```

### Gradients
```typescript
<LinearGradient
  colors={COLORS.backgroundGradient}
  locations={[0, 0.3, 0.7, 1]}
  style={styles.container}
>
  {/* Content */}
</LinearGradient>
```

## API Integration

### Authentication
```typescript
// Login
const response = await fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const { access_token } = await response.json();
```

### Authenticated Requests
```typescript
const response = await fetch(`${API_BASE_URL}/patients/`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Summarization
```typescript
const response = await fetch(`${API_BASE_URL}/summarize-sessions`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ patient_id: patientId })
});

const { summary } = await response.json();
```

## Components

### SummaryRenderer
Renders AI-generated summaries with formatting:

```typescript
<SummaryRenderer 
  summary="**Chief Complaint:** Anxiety. {{RED:self-harm thoughts}}"
  style={styles.text}
/>
```

Features:
- **Bold** text rendering
- Red highlighting for urgent keywords
- React Native compatible
- Automatic text parsing

## Configuration

### Environment Variables
Create `.env` file:
```
API_BASE_URL=http://192.168.1.100:8002
WS_BASE_URL=ws://192.168.1.100:8003
```

### Auto-Configuration
Backend automatically updates `src/config.ts` when network changes.

## Development

### Adding New Screens
1. Create screen in `src/screens/`
2. Add to navigation in `App.tsx`
3. Update types in `src/types/`

### Adding API Endpoints
1. Add function to `src/services/api.ts`
2. Use in screen components
3. Handle errors appropriately

### Styling Guidelines
- Use `COLORS` from config
- Follow existing component patterns
- Maintain consistent spacing
- Use LinearGradient for backgrounds

## Testing

### On Physical Device
1. Connect to same WiFi as backend
2. Scan QR code in Expo Go
3. Test all features

### Common Issues
- **Can't connect**: Check IP address in config
- **Audio not recording**: Check permissions
- **Transcription not working**: Verify WebSocket connection

## Permissions

### Required Permissions
- **Microphone**: Audio recording
- **Storage**: Save recordings (optional)

### Requesting Permissions
```typescript
import { Audio } from 'expo-av';

const { status } = await Audio.requestPermissionsAsync();
if (status !== 'granted') {
  Alert.alert('Permission required');
}
```

## Build & Deploy

### Development Build
```bash
npx expo start
```

### Production Build
```bash
# Android APK
eas build --platform android

# iOS IPA
eas build --platform ios
```

### Publishing
```bash
# Publish to Expo
expo publish

# Or build standalone app
eas build
```

## Troubleshooting

### Metro Bundler Issues
```bash
# Clear cache
npx expo start -c

# Reset
rm -rf node_modules
npm install
```

### Network Errors
1. Check backend is running
2. Verify IP address in config
3. Check firewall settings
4. Ensure same WiFi network

### Audio Recording Issues
1. Check microphone permissions
2. Test on physical device (not emulator)
3. Verify Audio.Recording setup

### WebSocket Connection
```typescript
// Add error handling
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

## Performance

### Optimization Tips
1. **Images**: Use optimized assets
2. **Lists**: Use FlatList for large datasets
3. **State**: Minimize re-renders
4. **Navigation**: Use React Navigation best practices

### Memory Management
- Clean up WebSocket connections
- Stop audio recording when done
- Clear large state when unmounting

## Dependencies

### Core
- `expo` - Development platform
- `react-native` - Mobile framework
- `react-navigation` - Navigation
- `expo-av` - Audio recording
- `expo-linear-gradient` - Gradients

### UI
- `@expo/vector-icons` - Icons
- `react-native-gesture-handler` - Gestures
- `react-native-safe-area-context` - Safe areas

## Support

### Common Questions
- **Q**: App won't connect to backend
  **A**: Check IP address and ensure same network

- **Q**: Transcription not working
  **A**: Verify WebSocket URL and backend is running

- **Q**: Summaries not showing
  **A**: Check Gemini API key in backend

### Debugging
```bash
# View logs
npx expo start

# Remote debugging
# Shake device → "Debug Remote JS"
```

## License

Proprietary - Auralis Medical Transcription System

---

**Status**: Production Ready
**Platform**: iOS & Android
**Framework**: React Native (Expo)
**Last Updated**: November 2025
