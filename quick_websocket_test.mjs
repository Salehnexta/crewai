#!/usr/bin/env node

import { WebSocket } from 'ws';

const WEBSOCKET_URL = 'wss://crewai-production-d99a.up.railway.app';

console.log('🔌 Testing WebSocket Connection...');

const userId = `test-user-${Date.now()}`;
const ws = new WebSocket(`${WEBSOCKET_URL}/ws/${userId}`);

const timeout = setTimeout(() => {
    console.log('❌ WebSocket connection timeout');
    ws.close();
    process.exit(1);
}, 10000);

ws.on('open', () => {
    console.log('✅ WebSocket connected successfully');
    clearTimeout(timeout);
    
    const testMessage = {
        type: 'chat',
        content: 'Hello from test!',
        user_id: userId
    };
    
    console.log('📤 Sending test message...');
    ws.send(JSON.stringify(testMessage));
    
    setTimeout(() => {
        console.log('✅ WebSocket test completed successfully');
        ws.close();
        process.exit(0);
    }, 3000);
});

ws.on('message', (data) => {
    try {
        const message = JSON.parse(data.toString());
        console.log('📥 Received:', JSON.stringify(message, null, 2));
    } catch (error) {
        console.log('📥 Raw message:', data.toString());
    }
});

ws.on('error', (error) => {
    console.log(`❌ WebSocket error: ${error.message}`);
    clearTimeout(timeout);
    process.exit(1);
});

ws.on('close', (code, reason) => {
    console.log(`🔌 WebSocket closed: ${code} - ${reason}`);
    clearTimeout(timeout);
});
