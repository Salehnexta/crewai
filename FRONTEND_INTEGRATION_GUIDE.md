# 🚀 Morvo AI v2.0 Frontend Integration Guide

## 📋 Overview

This guide provides everything needed to integrate with Morvo AI v2.0's enhanced WebSocket and REST API features, including smart alerts, intent detection, and rich components.

## 🔗 Production Endpoints

- **API Base**: `https://crewai-production-d99a.up.railway.app`
- **WebSocket**: `wss://crewai-production-d99a.up.railway.app/ws/{user_id}`
- **Documentation**: `https://crewai-production-d99a.up.railway.app/docs`

## 🎯 Core Features

### 1. Enhanced WebSocket Chat

```javascript
class MorvoWebSocket {
    constructor(userId) {
        this.userId = userId;
        this.ws = null;
        this.messageHandlers = new Map();
    }
    
    connect() {
        const wsUrl = `wss://crewai-production-d99a.up.railway.app/ws/${this.userId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('🔌 Connected to Morvo AI v2.0');
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };
    }
    
    handleMessage(message) {
        const { type } = message;
        
        switch(type) {
            case 'welcome':
                this.showWelcomeMessage(message);
                break;
            case 'message':
                this.showChatMessage(message);
                break;
            case 'smart_alert':
                this.showSmartAlert(message);
                break;
            case 'alert_check_started':
                this.showNotification(message);
                break;
            default:
                console.log('Unknown message type:', type);
        }
    }
    
    sendMessage(content) {
        const message = {
            content,
            user_id: this.userId,
            session_id: `session_${Date.now()}`,
            message_type: 'user'
        };
        
        this.ws.send(JSON.stringify(message));
    }
    
    showChatMessage(message) {
        const chatContainer = document.getElementById('chat-container');
        
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message morvo-message';
        
        // Intent indicator
        if (message.intent_detected) {
            const intentBadge = document.createElement('span');
            intentBadge.className = `intent-badge intent-${message.intent_detected}`;
            intentBadge.textContent = message.intent_detected;
            messageDiv.appendChild(intentBadge);
        }
        
        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message.content;
        messageDiv.appendChild(contentDiv);
        
        // Rich components
        if (message.rich_components && message.rich_components.length > 0) {
            const componentsDiv = document.createElement('div');
            componentsDiv.className = 'rich-components';
            
            message.rich_components.forEach(component => {
                const componentElement = this.createRichComponent(component);
                componentsDiv.appendChild(componentElement);
            });
            
            messageDiv.appendChild(componentsDiv);
        }
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    createRichComponent(component) {
        const div = document.createElement('div');
        div.className = `rich-component ${component.type}`;
        
        switch(component.type) {
            case 'button':
                const button = document.createElement('button');
                button.textContent = component.text;
                button.onclick = () => this.sendMessage(component.action);
                div.appendChild(button);
                break;
                
            case 'card':
                div.innerHTML = `
                    <div class="card">
                        <h4>${component.title}</h4>
                        <p>${component.description}</p>
                        ${component.action_url ? `<a href="${component.action_url}" target="_blank">View Details</a>` : ''}
                    </div>
                `;
                break;
                
            case 'alert_card':
                div.innerHTML = `
                    <div class="alert-card priority-${component.priority}">
                        <h4>🔔 ${component.title}</h4>
                        <p>${component.description}</p>
                        <button onclick="this.parentElement.style.display='none'">
                            ${component.action_button?.text || 'Acknowledge'}
                        </button>
                    </div>
                `;
                break;
        }
        
        return div;
    }
    
    showSmartAlert(alert) {
        // Create floating alert notification
        const alertDiv = document.createElement('div');
        alertDiv.className = `smart-alert priority-${alert.priority}`;
        alertDiv.innerHTML = `
            <div class="alert-header">
                <span class="alert-category">${alert.category}</span>
                <span class="alert-priority">${alert.priority.toUpperCase()}</span>
            </div>
            <h4>${alert.title}</h4>
            <p>${alert.message}</p>
            <div class="alert-actions">
                <button onclick="this.parentElement.parentElement.remove()">Dismiss</button>
                ${alert.action_url ? `<button onclick="window.open('${alert.action_url}')">View Details</button>` : ''}
            </div>
        `;
        
        // Add to notifications container
        const notificationsContainer = document.getElementById('notifications') || 
                                      document.body.appendChild(document.createElement('div'));
        notificationsContainer.id = 'notifications';
        notificationsContainer.appendChild(alertDiv);
        
        // Auto-remove after 10 seconds for non-critical alerts
        if (alert.priority !== 'critical') {
            setTimeout(() => {
                if (alertDiv.parentElement) {
                    alertDiv.remove();
                }
            }, 10000);
        }
    }
}
```

### 2. Smart Alerts Management

```javascript
class SmartAlertsManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.alerts = [];
    }
    
    async getAlertsStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/api/v2/alerts/status`);
            return await response.json();
        } catch (error) {
            console.error('Error getting alerts status:', error);
            return null;
        }
    }
    
    async triggerAlertsCheck(organizationId) {
        try {
            const response = await fetch(`${this.apiUrl}/api/v2/alerts/check/${organizationId}`);
            return await response.json();
        } catch (error) {
            console.error('Error triggering alerts:', error);
            return null;
        }
    }
    
    async renderAlertsStatus() {
        const status = await this.getAlertsStatus();
        if (!status) return;
        
        const statusDiv = document.getElementById('alerts-status');
        statusDiv.innerHTML = `
            <div class="alerts-status">
                <h3>🔔 Smart Alerts Status</h3>
                <p>Status: <span class="status-${status.status}">${status.status}</span></p>
                <p>WebSocket Connections: ${status.websocket_connections}</p>
                <p>Last Check: ${new Date(status.last_check).toLocaleString()}</p>
                
                <div class="alert-categories">
                    <h4>Alert Categories:</h4>
                    <ul>
                        ${status.categories.map(cat => `<li>${cat}</li>`).join('')}
                    </ul>
                </div>
                
                <button onclick="smartAlerts.triggerCheck()">
                    🔍 Trigger Alerts Check
                </button>
            </div>
        `;
    }
    
    async triggerCheck() {
        const result = await this.triggerAlertsCheck('your_org_id');
        if (result) {
            alert('Smart alerts check started! You\'ll receive notifications via WebSocket.');
        }
    }
}
```

### 3. Platform Integration Components

```javascript
class PlatformIntegration {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
    }
    
    async getAvailablePlatforms() {
        const response = await fetch(`${this.apiUrl}/api/v2/platforms/available`);
        return await response.json();
    }
    
    async renderPlatformSelector() {
        const data = await this.getAvailablePlatforms();
        const container = document.getElementById('platforms-container');
        
        container.innerHTML = `
            <div class="platforms-grid">
                ${data.platforms.map(platform => `
                    <div class="platform-card ${platform.type}">
                        <img src="${platform.logo}" alt="${platform.name}" class="platform-logo">
                        <h4>${platform.name}</h4>
                        <p>${platform.description}</p>
                        <div class="platform-features">
                            ${platform.supported_features.map(feature => 
                                `<span class="feature-tag">${feature}</span>`
                            ).join('')}
                        </div>
                        <div class="platform-difficulty difficulty-${platform.setup_difficulty}">
                            Setup: ${platform.setup_difficulty}
                        </div>
                        <button onclick="connectPlatform('${platform.id}')">
                            Connect ${platform.name}
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }
}
```

### 4. Complete Integration Example

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morvo AI Dashboard</title>
    <style>
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .chat-message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
            background: #f5f5f5;
        }
        
        .intent-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-bottom: 5px;
            background: #007bff;
            color: white;
        }
        
        .rich-components {
            margin-top: 10px;
        }
        
        .smart-alert {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 300px;
            z-index: 1000;
        }
        
        .priority-high { border-left: 4px solid #ff6b35; }
        .priority-medium { border-left: 4px solid #f7931e; }
        .priority-low { border-left: 4px solid #2ecc71; }
        .priority-critical { border-left: 4px solid #e74c3c; }
        
        .platforms-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .platform-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .platform-logo {
            width: 48px;
            height: 48px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div id="app">
        <h1>🤖 Morvo AI Dashboard v2.0</h1>
        
        <!-- Chat Section -->
        <div class="section">
            <h2>💬 Smart Chat</h2>
            <div id="chat-container" class="chat-container"></div>
            <div class="chat-input">
                <input type="text" id="message-input" placeholder="اكتب رسالتك هنا..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <!-- Alerts Status -->
        <div class="section">
            <div id="alerts-status"></div>
        </div>
        
        <!-- Platform Integration -->
        <div class="section">
            <h2>🔗 Platform Integration</h2>
            <div id="platforms-container"></div>
        </div>
        
        <!-- Notifications Container -->
        <div id="notifications"></div>
    </div>

    <script>
        // Initialize components
        const morvoWS = new MorvoWebSocket('user_123');
        const smartAlerts = new SmartAlertsManager('https://crewai-production-d99a.up.railway.app');
        const platformIntegration = new PlatformIntegration('https://crewai-production-d99a.up.railway.app');
        
        // Connect on page load
        window.onload = () => {
            morvoWS.connect();
            smartAlerts.renderAlertsStatus();
            platformIntegration.renderPlatformSelector();
        };
        
        // Send message function
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (message) {
                morvoWS.sendMessage(message);
                input.value = '';
            }
        }
        
        // Platform connection function
        function connectPlatform(platformId) {
            alert(`Connecting to ${platformId}... (Integration coming soon!)`);
        }
    </script>
</body>
</html>
```

## 🎯 API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health and version |
| `/api/v2/platforms/available` | GET | Available platforms list |
| `/api/v2/alerts/status` | GET | Smart alerts system status |
| `/api/v2/alerts/check/{org_id}` | GET | Trigger alerts check |
| `/api/v2/website/analyze` | POST | Start website analysis |

### WebSocket Messages

#### Outgoing (Client → Server)
```json
{
    "content": "أريد تحليل موقعي",
    "user_id": "user_123",
    "session_id": "session_456",
    "message_type": "user"
}
```

#### Incoming (Server → Client)
```json
{
    "type": "message",
    "content": "سأساعدك في تحليل موقعك...",
    "intent_detected": "website_analysis",
    "confidence_score": 0.92,
    "rich_components": [
        {
            "type": "button",
            "text": "ابدأ التحليل",
            "action": "start_analysis"
        }
    ],
    "timestamp": "2025-06-06T12:00:00Z"
}
```

## 🚀 Next Steps

1. **Implement the WebSocket connection** using the provided `MorvoWebSocket` class
2. **Add the smart alerts management** with real-time notifications
3. **Integrate platform selector** for e-commerce connections
4. **Style the components** to match your design system
5. **Add error handling** and reconnection logic
6. **Implement user authentication** for production use

## 📞 Support

- **API Documentation**: `https://crewai-production-d99a.up.railway.app/docs`
- **WebSocket Debugging**: Use browser DevTools Network tab
- **Test Endpoints**: Use the provided test scripts

This integration guide provides everything needed to build a complete frontend for Morvo AI v2.0's enhanced features!
