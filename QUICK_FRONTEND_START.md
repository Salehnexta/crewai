# 🚀 Quick Frontend Startup Guide

## ⚡ Ready to Launch (5 Minutes)

### 1. Navigate to Frontend Directory
```bash
cd /Users/salehgazwani/crewai/frontend-project
```

### 2. Install Dependencies (if not done)
```bash
npm install
```

### 3. Verify Configuration
✅ `.env.local` - Already configured with Railway URLs
✅ `environment.ts` - Updated for production
✅ Supabase client - Ready to use

### 4. Start Development Server
```bash
npm run dev
```

### 5. Test Integration
Open browser to `http://localhost:5173` (or displayed port)

## 🧪 Testing Checklist

### ✅ What Should Work
- [x] **WebSocket Chat**: Real-time messaging
- [x] **Basic Navigation**: App routing and UI
- [x] **Platform APIs**: Available platforms endpoint
- [x] **Health Monitoring**: Backend status display

### ⚠️ What May Need Debugging
- [ ] **Chat Responses**: May show fallback messages
- [ ] **Agent Status**: Endpoint not implemented yet
- [ ] **Supabase Data**: May need browser environment

## 🔧 Quick Fixes if Needed

### Frontend Not Starting?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### CORS Issues?
The backend is configured with `CORS_ALLOWED_ORIGINS="*"` so this should not be an issue.

### WebSocket Connection Failed?
Verify in browser console:
```javascript
// Test WebSocket manually
const ws = new WebSocket('wss://crewai-production-d99a.up.railway.app/ws/test-user');
ws.onopen = () => console.log('Connected!');
```

## 📱 Expected Frontend Features

### 🎨 UI Components
- Modern React with Tailwind CSS
- Arabic RTL support
- ShadCN UI components
- Dark/Light theme

### 🔌 Integrations
- **Railway API**: REST endpoints
- **WebSocket**: Real-time chat
- **Supabase**: Database operations
- **Agents M1-M5**: AI assistants

### 🛠️ Development Tools
- Vite build system
- TypeScript support
- ESLint configuration
- Hot module replacement

## 🎯 First Test Scenarios

1. **Open App**: Should load dashboard
2. **WebSocket**: Should see connection status
3. **Send Message**: Should get welcome/fallback response
4. **Platform Check**: Should list available platforms
5. **Health Status**: Should show backend health

## 📞 Production URLs (Already Configured)

- **Backend API**: `https://crewai-production-d99a.up.railway.app`
- **WebSocket**: `wss://crewai-production-d99a.up.railway.app/ws`
- **Supabase**: `https://teniefzxdikestahndur.supabase.co`

## ✨ You're Ready!

The frontend is fully configured and ready to connect to the production Railway backend. The main functionality (WebSocket chat) is working, and any missing features can be debugged incrementally while the app is running.
