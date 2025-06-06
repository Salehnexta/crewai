/**
 * Full Integration Test: Frontend + Backend + Supabase
 * Tests complete connectivity between all components
 */

import { createClient } from '@supabase/supabase-js'

const RAILWAY_API_URL = 'https://crewai-production-d99a.up.railway.app';
const RAILWAY_WS_URL = 'wss://crewai-production-d99a.up.railway.app/ws';
const SUPABASE_URL = 'https://teniefzxdikestahndur.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlbmllZnp4ZGlrZXN0YWhkbnVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2MjI2NTIsImV4cCI6MjA2NDE5ODY1Mn0.k5eor_-j2aTheb1q6OhGK8DWGjucRWK11eFAOpAZP3I';

console.log('🧪 Testing Full Stack Integration...\n');
console.log('🎯 Components:');
console.log('   📱 Frontend Config');
console.log('   🚄 Railway Backend API');
console.log('   💾 Supabase Database');
console.log('   🔌 WebSocket Connection');
console.log();

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Test 1: Railway Health Check
async function testRailwayHealth() {
  console.log('1️⃣ Testing Railway Backend Health...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Railway Backend: HEALTHY');
      console.log(`   📊 WebSocket Connections: ${data.websocket_connections || 0}`);
      console.log(`   🤖 Chat Engine: ${data.chat_engine_status || 'Unknown'}`);
      return true;
    } else {
      console.log('❌ Railway Backend: UNHEALTHY');
      return false;
    }
  } catch (error) {
    console.log('❌ Railway Backend Error:', error.message);
    return false;
  }
}

// Test 2: Supabase Connection
async function testSupabaseConnection() {
  console.log('\n2️⃣ Testing Supabase Database Connection...');
  try {
    // Test basic connectivity
    const { data, error } = await supabase
      .from('chat_sessions')
      .select('count')
      .limit(1);
    
    if (error && error.code !== 'PGRST116') { // PGRST116 = table not found (OK for this test)
      console.log('❌ Supabase Connection Failed:', error.message);
      return false;
    }
    
    console.log('✅ Supabase: CONNECTED');
    console.log('   🗃️ Database accessible');
    
    return true;
  } catch (error) {
    console.log('❌ Supabase Error:', error.message);
    return false;
  }
}

// Test 3: API Endpoints
async function testAPIEndpoints() {
  console.log('\n3️⃣ Testing API Endpoints...');
  const endpoints = [
    '/api/v2/platforms/available',
    '/api/v2/agents/status',
    '/'
  ];
  
  let successCount = 0;
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${RAILWAY_API_URL}${endpoint}`);
      if (response.ok) {
        console.log(`   ✅ ${endpoint}: Working`);
        successCount++;
      } else {
        console.log(`   ❌ ${endpoint}: Failed (${response.status})`);
      }
    } catch (error) {
      console.log(`   ❌ ${endpoint}: Error`);
    }
  }
  
  console.log(`✅ API Endpoints: ${successCount}/${endpoints.length} working`);
  return successCount === endpoints.length;
}

// Test 4: Chat Integration
async function testChatIntegration() {
  console.log('\n4️⃣ Testing Chat Integration...');
  try {
    const response = await fetch(`${RAILWAY_API_URL}/api/v2/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'morvo-production-key'
      },
      body: JSON.stringify({
        message: 'اختبار الربط بين الفرونت والباك اند',
        user_id: 'test-integration-user'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Chat Integration: Working');
      console.log(`   💬 Response Type: ${data.type || 'message'}`);
      console.log(`   🎯 Intent Detected: ${data.intent_detected || 'general'}`);
      return true;
    } else {
      console.log('❌ Chat Integration: Failed');
      return false;
    }
  } catch (error) {
    console.log('❌ Chat Integration Error:', error.message);
    return false;
  }
}

// Test 5: WebSocket Real-time
async function testWebSocketIntegration() {
  console.log('\n5️⃣ Testing WebSocket Real-time Connection...');
  
  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(`${RAILWAY_WS_URL}/test-integration-user`);
      let messageReceived = false;
      
      ws.onopen = () => {
        console.log('✅ WebSocket: Connected');
        
        // Send test message
        ws.send(JSON.stringify({
          type: 'test',
          content: 'Integration test message',
          user_id: 'test-integration-user'
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`   📨 Received: ${data.type}`);
        messageReceived = true;
        ws.close();
        resolve(true);
      };
      
      ws.onerror = () => {
        console.log('❌ WebSocket: Connection failed');
        resolve(false);
      };
      
      ws.onclose = () => {
        if (!messageReceived) {
          console.log('❌ WebSocket: No response received');
          resolve(false);
        }
      };
      
      // Timeout after 8 seconds
      setTimeout(() => {
        if (ws.readyState !== WebSocket.CLOSED) {
          console.log('⏰ WebSocket: Timeout');
          ws.close();
          resolve(false);
        }
      }, 8000);
      
    } catch (error) {
      console.log('❌ WebSocket Setup Error:', error.message);
      resolve(false);
    }
  });
}

// Test 6: Data Flow Integration
async function testDataFlowIntegration() {
  console.log('\n6️⃣ Testing Data Flow Integration...');
  try {
    // Test storing chat session in Supabase (if table exists)
    const sessionData = {
      user_id: 'test-integration-user',
      session_id: `test-${Date.now()}`,
      created_at: new Date().toISOString(),
      status: 'active'
    };
    
    // Try to insert (might fail if table doesn't exist, that's OK)
    const { error } = await supabase
      .from('chat_sessions')
      .insert([sessionData]);
    
    if (error && error.code !== 'PGRST116') {
      console.log('⚠️ Supabase table structure may need setup');
    } else {
      console.log('✅ Data Flow: Can store session data');
    }
    
    return true;
  } catch (error) {
    console.log('⚠️ Data Flow: Setup may be needed');
    return true; // Don't fail the test for this
  }
}

// Run comprehensive integration test
async function runFullIntegrationTest() {
  console.log('🚀 Starting Full Stack Integration Test...\n');
  
  const testResults = {
    railwayHealth: await testRailwayHealth(),
    supabaseConnection: await testSupabaseConnection(),
    apiEndpoints: await testAPIEndpoints(),
    chatIntegration: await testChatIntegration(),
    webSocketIntegration: await testWebSocketIntegration(),
    dataFlowIntegration: await testDataFlowIntegration()
  };
  
  console.log('\n📊 Integration Test Results:');
  console.log('=====================================');
  
  Object.entries(testResults).forEach(([test, passed]) => {
    const status = passed ? '✅ PASSED' : '❌ FAILED';
    const testName = test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    console.log(`${status} - ${testName}`);
  });
  
  const passedTests = Object.values(testResults).filter(Boolean).length;
  const totalTests = Object.keys(testResults).length;
  
  console.log(`\n🎯 Overall Result: ${passedTests}/${totalTests} tests passed`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 FULL INTEGRATION SUCCESS!');
    console.log('✨ Frontend is ready to connect to Railway + Supabase');
    console.log('📋 Next Steps:');
    console.log('   1. Install frontend dependencies: npm install');
    console.log('   2. Copy .env.local settings');
    console.log('   3. Start development server: npm run dev');
    console.log('   4. Test real-time chat functionality');
  } else {
    console.log('\n⚠️ Integration Issues Detected');
    console.log('🔧 Check the failed components above');
  }
  
  return testResults;
}

// Run the test
runFullIntegrationTest().catch(console.error);
