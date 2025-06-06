#!/usr/bin/env node
/**
 * 🚀 Morvo AI v2.0 Production Test Suite
 * Tests enhanced WebSocket and API endpoints on Railway
 */

import WebSocket from 'ws';

const PRODUCTION_URL = 'https://crewai-production-d99a.up.railway.app';
const WS_URL = 'wss://crewai-production-d99a.up.railway.app';

console.log('🔍 Testing Morvo AI v2.0 on Railway Production...\n');

// Test 1: Health Check
async function testHealthCheck() {
    console.log('1️⃣ Testing Health Check...');
    try {
        const response = await fetch(`${PRODUCTION_URL}/health`);
        const data = await response.json();
        console.log('✅ Health Check Response:', JSON.stringify(data, null, 2));
        
        // Check for v2.0 indicators
        if (data.version === '2.0.0' || data.services) {
            console.log('🎉 V2.0 API detected!\n');
        } else {
            console.log('⚠️  Still using v1.0 API\n');
        }
    } catch (error) {
        console.error('❌ Health check failed:', error.message);
    }
}

// Test 2: API Root Information
async function testRootInfo() {
    console.log('2️⃣ Testing Root API Info...');
    try {
        const response = await fetch(`${PRODUCTION_URL}/`);
        const data = await response.json();
        console.log('✅ Root API Response:');
        console.log(`   Service: ${data.service || 'Unknown'}`);
        console.log(`   Version: ${data.version || 'Unknown'}`);
        console.log(`   Features: ${data.features ? data.features.length : 0} available`);
        if (data.features) {
            data.features.forEach((feature, i) => {
                console.log(`     ${i + 1}. ${feature}`);
            });
        }
        console.log();
    } catch (error) {
        console.error('❌ Root info failed:', error.message);
    }
}

// Test 3: Enhanced WebSocket with v2.0 features
function testEnhancedWebSocket() {
    return new Promise((resolve) => {
        console.log('3️⃣ Testing Enhanced WebSocket with v2.0 Features...');
        
        const ws = new WebSocket(`${WS_URL}/ws/test_user_v2`);
        let messageCount = 0;
        
        ws.on('open', () => {
            console.log('✅ WebSocket connected successfully');
            
            // Test messages for different intents
            const testMessages = [
                { content: 'مرحبا', expected_intent: 'greeting' },
                { content: 'أريد تحليل موقع https://example.com', expected_intent: 'website_analysis' },
                { content: 'كيف أربط منصة سلة؟', expected_intent: 'platform_connection' },
                { content: 'أريد إنشاء حملة تسويقية', expected_intent: 'marketing_campaign' }
            ];
            
            // Send test messages with delay
            testMessages.forEach((test, index) => {
                setTimeout(() => {
                    console.log(`📤 Sending: ${test.content}`);
                    ws.send(JSON.stringify({
                        content: test.content,
                        user_id: 'test_user_v2',
                        session_id: 'test_session_v2',
                        message_type: 'user'
                    }));
                }, index * 2000);
            });
            
            // Close connection after all tests
            setTimeout(() => {
                ws.close();
            }, 10000);
        });
        
        ws.on('message', (data) => {
            messageCount++;
            try {
                const message = JSON.parse(data);
                console.log(`📥 Message ${messageCount}:`, {
                    type: message.type,
                    intent: message.intent_detected || 'none',
                    content: message.content || message.message,
                    rich_components: message.rich_components?.length || 0
                });
                
                // Check for v2.0 features
                if (message.intent_detected) {
                    console.log(`   🎯 Intent Detected: ${message.intent_detected}`);
                }
                if (message.rich_components && message.rich_components.length > 0) {
                    console.log(`   📊 Rich Components: ${message.rich_components.length} components`);
                }
            } catch (error) {
                console.log(`📥 Raw message: ${data}`);
            }
        });
        
        ws.on('close', () => {
            console.log('🔐 WebSocket connection closed');
            console.log(`📊 Total messages received: ${messageCount}\n`);
            resolve();
        });
        
        ws.on('error', (error) => {
            console.error('❌ WebSocket error:', error.message);
            resolve();
        });
    });
}

// Test 4: V2.0 API Endpoints
async function testV2Endpoints() {
    console.log('4️⃣ Testing V2.0 API Endpoints...');
    
    const endpoints = [
        '/api/v2/platforms/available',
        '/api/v2/platforms/status/test_org',
        '/docs',
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`   Testing: ${endpoint}`);
            const response = await fetch(`${PRODUCTION_URL}${endpoint}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`   ✅ ${endpoint}: ${response.status} - ${Object.keys(data).length} keys`);
            } else {
                console.log(`   ⚠️  ${endpoint}: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.log(`   ❌ ${endpoint}: ${error.message}`);
        }
    }
    console.log();
}

// Test 5: Documentation Check
async function testDocumentation() {
    console.log('5️⃣ Testing API Documentation...');
    try {
        const response = await fetch(`${PRODUCTION_URL}/docs`);
        if (response.ok) {
            console.log('✅ API Documentation is accessible');
            console.log(`   URL: ${PRODUCTION_URL}/docs`);
        } else {
            console.log(`⚠️  Documentation returned: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Documentation test failed:', error.message);
    }
    console.log();
}

// Run all tests
async function runAllTests() {
    console.log('🧪 Starting Morvo AI v2.0 Production Test Suite...\n');
    console.log(`📡 Production URL: ${PRODUCTION_URL}`);
    console.log(`🔌 WebSocket URL: ${WS_URL}\n`);
    
    await testHealthCheck();
    await testRootInfo();
    await testEnhancedWebSocket();
    await testV2Endpoints();
    await testDocumentation();
    
    console.log('🏁 All tests completed!');
    console.log('📋 Summary:');
    console.log('   - Health checks and API info retrieval');
    console.log('   - Enhanced WebSocket with intent detection');
    console.log('   - V2.0 API endpoints verification');
    console.log('   - Documentation accessibility');
    console.log('\n🎉 Morvo AI v2.0 Production Testing Complete!');
}

// Execute tests
runAllTests().catch(console.error);
