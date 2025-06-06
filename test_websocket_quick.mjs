#!/usr/bin/env node

import WebSocket from 'ws';

console.log('🔌 Testing WebSocket connection...');

const ws = new WebSocket('wss://crewai-production-d99a.up.railway.app/ws/test_user_123');

ws.on('open', function open() {
    console.log('✅ WebSocket connected successfully!');
    
    // Send test message
    const testMessage = {
        type: 'chat_message',
        content: 'مرحبا من WebSocket',
        user_id: 'test_user_123'
    };
    
    console.log('📤 Sending test message...');
    ws.send(JSON.stringify(testMessage));
});

ws.on('message', function message(data) {
    const response = JSON.parse(data.toString());
    console.log('📥 Received message:', response);
    
    // Close after receiving response
    setTimeout(() => {
        ws.close();
        console.log('🔌 WebSocket test completed successfully!');
    }, 1000);
});

ws.on('error', function error(err) {
    console.error('❌ WebSocket error:', err.message);
});

ws.on('close', function close() {
    console.log('🔌 WebSocket connection closed');
    process.exit(0);
});

// Timeout after 10 seconds
setTimeout(() => {
    console.log('⏰ Test timeout - closing connection');
    ws.close();
    process.exit(1);
}, 10000);
