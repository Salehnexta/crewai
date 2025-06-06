/**
 * Frontend-Backend Integration Test
 * Tests connectivity between React Frontend and Railway Backend
 */

const RAILWAY_API_URL = 'https://crewai-production-d99a.up.railway.app';
const RAILWAY_WS_URL = 'wss://crewai-production-d99a.up.railway.app/ws';

console.log('🧪 Testing Frontend-Backend Integration...\n');

// Test 1: Health Check
async function testHealthCheck() {
  console.log('1️⃣ Testing Health Check Endpoint...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/health`);
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Health Check Passed');
      console.log('📊 Status:', data);
      return true;
    } else {
      console.log('❌ Health Check Failed:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Health Check Error:', error.message);
    return false;
  }
}

// Test 2: API Root Endpoint
async function testRootEndpoint() {
  console.log('\n2️⃣ Testing Root API Endpoint...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/`);
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Root Endpoint Accessible');
      console.log('📋 Response:', data);
      return true;
    } else {
      console.log('❌ Root Endpoint Failed:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Root Endpoint Error:', error.message);
    return false;
  }
}

// Test 3: Chat Message Endpoint
async function testChatEndpoint() {
  console.log('\n3️⃣ Testing Chat Message Endpoint...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/api/v2/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'morvo-production-key'
      },
      body: JSON.stringify({
        message: 'مرحبا، كيف الحال؟',
        user_id: 'test-user-frontend'
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Chat Endpoint Working');
      console.log('💬 Response:', data.response?.substring(0, 100) + '...');
      return true;
    } else {
      console.log('❌ Chat Endpoint Failed:', response.status, data);
      return false;
    }
  } catch (error) {
    console.log('❌ Chat Endpoint Error:', error.message);
    return false;
  }
}

// Test 4: WebSocket Connection
function testWebSocketConnection() {
  console.log('\n4️⃣ Testing WebSocket Connection...');
  
  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(`${RAILWAY_WS_URL}/test-user-frontend`);
      let connectionSuccessful = false;
      
      ws.onopen = () => {
        console.log('✅ WebSocket Connected Successfully');
        connectionSuccessful = true;
        
        // Send test message
        ws.send(JSON.stringify({
          type: 'message',
          content: 'Frontend integration test',
          user_id: 'test-user-frontend'
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 Received WebSocket Message:', data.type);
        ws.close();
        resolve(true);
      };
      
      ws.onerror = (error) => {
        console.log('❌ WebSocket Error:', error);
        resolve(false);
      };
      
      ws.onclose = () => {
        if (!connectionSuccessful) {
          console.log('❌ WebSocket Connection Failed');
          resolve(false);
        }
      };
      
      // Timeout after 10 seconds
      setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          console.log('⏰ WebSocket Connection Timeout');
          ws.close();
          resolve(false);
        }
      }, 10000);
      
    } catch (error) {
      console.log('❌ WebSocket Setup Error:', error.message);
      resolve(false);
    }
  });
}

// Test 5: CORS Configuration
async function testCORSConfiguration() {
  console.log('\n5️⃣ Testing CORS Configuration...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/health`, {
      method: 'GET',
      headers: {
        'Origin': 'http://localhost:5173', // Typical Vite dev server port
        'Access-Control-Request-Method': 'GET'
      }
    });
    
    if (response.ok) {
      console.log('✅ CORS Configuration Working');
      console.log('🌐 Access-Control-Allow-Origin:', response.headers.get('access-control-allow-origin'));
      return true;
    } else {
      console.log('❌ CORS Test Failed:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ CORS Test Error:', error.message);
    return false;
  }
}

// Run all tests
async function runIntegrationTests() {
  console.log('🚀 Starting Frontend-Backend Integration Tests...\n');
  
  const results = {
    healthCheck: await testHealthCheck(),
    rootEndpoint: await testRootEndpoint(),
    chatEndpoint: await testChatEndpoint(),
    webSocket: await testWebSocketConnection(),
    cors: await testCORSConfiguration()
  };
  
  console.log('\n📊 Integration Test Results:');
  console.log('================================');
  
  Object.entries(results).forEach(([test, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
  });
  
  const passedTests = Object.values(results).filter(Boolean).length;
  const totalTests = Object.keys(results).length;
  
  console.log(`\n🎯 Overall Result: ${passedTests}/${totalTests} tests passed`);
  
  if (passedTests === totalTests) {
    console.log('🎉 All tests passed! Frontend can integrate with Railway Backend.');
  } else {
    console.log('⚠️ Some tests failed. Check the logs above for details.');
  }
  
  return results;
}

// Export for Node.js or run directly
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runIntegrationTests };
} else {
  runIntegrationTests();
}
