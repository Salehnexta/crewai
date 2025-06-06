// test_production_websocket.mjs
import { WebSocket } from 'ws';

console.log('🚀 TESTING WEBSOCKET PATHS ON PRODUCTION');
console.log('==========================================');
console.log('');

// Railway production URL
const baseUrl = 'wss://crewai-production-d99a.up.railway.app';

// Array of paths to test
const pathsToTest = [
  '/ws/test_user',
  '/websocket/test_user',
  '/api/ws/test_user',
  '/api/v2/ws/test_user'
];

// Test one path at a time
async function testWebSocketPath(path) {
  return new Promise((resolve) => {
    console.log(`🔌 Testing WebSocket Path: ${baseUrl}${path}`);
    
    // Create WebSocket connection
    const ws = new WebSocket(`${baseUrl}${path}`);
    
    // Connection opened
    ws.on('open', () => {
      console.log(`✅ Connected successfully to ${path}`);
      
      // Send a test message
      const message = JSON.stringify({
        type: 'message',
        content: 'Hello from WebSocket test!',
        userId: 'test_user'
      });
      
      ws.send(message);
      console.log(`📤 Sent message: ${message}`);
      
      // Close after 2 seconds
      setTimeout(() => {
        ws.close();
        resolve();
      }, 2000);
    });
    
    // Listen for messages
    ws.on('message', (data) => {
      try {
        const parsedData = JSON.parse(data);
        console.log(`📥 Received: ${JSON.stringify(parsedData)}`);
      } catch (e) {
        console.log(`📥 Received: ${data}`);
      }
    });
    
    // Handle errors
    ws.on('error', (error) => {
      console.log(`❌ Error: ${error.message}`);
    });
    
    // Connection closed
    ws.on('close', (code, reason) => {
      console.log(`🔌 Connection closed: ${code} - ${reason || ''}`);
      console.log('');
      resolve();
    });
    
    // Timeout after 5 seconds
    setTimeout(() => {
      if (ws.readyState !== WebSocket.CLOSED) {
        ws.close();
        console.log('⏱️ Connection timed out');
        resolve();
      }
    }, 5000);
  });
}

// Test all paths sequentially
async function runTests() {
  for (const path of pathsToTest) {
    await testWebSocketPath(path);
  }
  console.log('==========================================');
}

runTests();
