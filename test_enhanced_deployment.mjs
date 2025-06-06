#!/usr/bin/env node

/**
 * Enhanced Railway Deployment Test Suite
 * Tests health check robustness and WebSocket stability
 */

import { WebSocket } from 'ws';

const PRODUCTION_URL = 'https://crewai-production-d99a.up.railway.app';
const WEBSOCKET_URL = 'wss://crewai-production-d99a.up.railway.app';

console.log('🚀 Testing Enhanced Railway Deployment...\n');

// Test 1: Enhanced Health Check
async function testHealthCheck() {
    console.log('📋 Testing Enhanced Health Check...');
    try {
        const response = await globalThis.fetch(`${PRODUCTION_URL}/health`);
        const data = await response.json();
        
        console.log(`   Status Code: ${response.status}`);
        console.log(`   Service Status: ${data.status}`);
        console.log(`   Environment: ${data.environment}`);
        console.log(`   Version: ${data.version}`);
        console.log(`   Services:`, JSON.stringify(data.services, null, 4));
        
        if (response.status === 200) {
            console.log('   ✅ Health check responding correctly');
            return true;
        } else {
            console.log('   ❌ Health check failed');
            return false;
        }
    } catch (error) {
        console.log(`   ❌ Health check error: ${error.message}`);
        return false;
    }
}

// Test 2: Root Endpoint
async function testRootEndpoint() {
    console.log('\n🏠 Testing Root Endpoint...');
    try {
        const response = await globalThis.fetch(`${PRODUCTION_URL}/`);
        const data = await response.json();
        
        console.log(`   Status Code: ${response.status}`);
        console.log(`   Response:`, JSON.stringify(data, null, 2));
        
        if (response.status === 200) {
            console.log('   ✅ Root endpoint working');
            return true;
        }
    } catch (error) {
        console.log(`   ❌ Root endpoint error: ${error.message}`);
        return false;
    }
}

// Test 3: WebSocket Connection Stability
async function testWebSocketConnection() {
    console.log('\n🔌 Testing WebSocket Connection...');
    
    return new Promise((resolve) => {
        const userId = `test-user-${Date.now()}`;
        const ws = new WebSocket(`${WEBSOCKET_URL}/ws/${userId}`);
        let connected = false;
        let messageReceived = false;
        
        const timeout = setTimeout(() => {
            if (!connected) {
                console.log('   ❌ WebSocket connection timeout');
                ws.close();
                resolve(false);
            }
        }, 10000);
        
        ws.on('open', () => {
            console.log('   ✅ WebSocket connected successfully');
            connected = true;
            clearTimeout(timeout);
            
            // Test sending a message
            const testMessage = {
                type: 'chat',
                content: 'Hello, this is a deployment test!',
                user_id: userId
            };
            
            console.log('   📤 Sending test message...');
            ws.send(JSON.stringify(testMessage));
        });
        
        ws.on('message', (data) => {
            try {
                const message = JSON.parse(data.toString());
                console.log('   📥 Received message:', JSON.stringify(message, null, 2));
                messageReceived = true;
                
                // Close connection after successful test
                setTimeout(() => {
                    ws.close();
                    resolve(true);
                }, 2000);
                
            } catch (error) {
                console.log('   ⚠️ Message parsing error:', error.message);
            }
        });
        
        ws.on('error', (error) => {
            console.log(`   ❌ WebSocket error: ${error.message}`);
            clearTimeout(timeout);
            resolve(false);
        });
        
        ws.on('close', (code, reason) => {
            console.log(`   🔌 WebSocket closed: ${code} - ${reason}`);
            if (!messageReceived && connected) {
                resolve(false);
            }
        });
    });
}

// Test 4: Service Endpoints
async function testServiceEndpoints() {
    console.log('\n🛠️ Testing Service Endpoints...');
    
    const endpoints = [
        '/api/v2/conversation/analyze-business',
        '/api/v2/platforms/status',
        '/docs'
    ];
    
    let successCount = 0;
    
    for (const endpoint of endpoints) {
        try {
            const response = await globalThis.fetch(`${PRODUCTION_URL}${endpoint}`);
            console.log(`   ${endpoint}: ${response.status}`);
            
            if (response.status < 500) {
                successCount++;
                console.log(`   ✅ ${endpoint} accessible`);
            } else {
                console.log(`   ❌ ${endpoint} server error`);
            }
        } catch (error) {
            console.log(`   ❌ ${endpoint} error: ${error.message}`);
        }
    }
    
    return successCount === endpoints.length;
}

// Test 5: Load Test (Multiple Health Checks)
async function testLoadStability() {
    console.log('\n📊 Testing Load Stability (5 concurrent health checks)...');
    
    const promises = Array.from({ length: 5 }, async (_, i) => {
        try {
            const response = await globalThis.fetch(`${PRODUCTION_URL}/health`);
            return { index: i, status: response.status, success: response.status === 200 };
        } catch (error) {
            return { index: i, status: 'error', success: false, error: error.message };
        }
    });
    
    const results = await Promise.all(promises);
    const successCount = results.filter(r => r.success).length;
    
    console.log('   Results:');
    results.forEach(result => {
        const status = result.success ? '✅' : '❌';
        console.log(`   ${status} Request ${result.index}: ${result.status}`);
    });
    
    console.log(`   📊 Success Rate: ${successCount}/5 (${(successCount/5*100).toFixed(1)}%)`);
    return successCount >= 4; // Allow 1 failure
}

// Main Test Runner
async function runAllTests() {
    console.log('🔬 Enhanced Deployment Test Suite');
    console.log('====================================\n');
    
    const results = {
        healthCheck: await testHealthCheck(),
        rootEndpoint: await testRootEndpoint(),
        webSocket: await testWebSocketConnection(),
        serviceEndpoints: await testServiceEndpoints(),
        loadStability: await testLoadStability()
    };
    
    console.log('\n📋 Test Results Summary:');
    console.log('========================');
    
    Object.entries(results).forEach(([test, passed]) => {
        const status = passed ? '✅ PASS' : '❌ FAIL';
        console.log(`${status} ${test}`);
    });
    
    const passedTests = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;
    
    console.log(`\n🎯 Overall: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
        console.log('🎉 All tests passed! Railway deployment is stable and healthy.');
    } else if (passedTests >= totalTests * 0.8) {
        console.log('⚠️ Most tests passed. Minor issues detected but deployment is functional.');
    } else {
        console.log('🚨 Multiple test failures. Deployment needs attention.');
    }
    
    console.log(`\n🌐 Production URL: ${PRODUCTION_URL}`);
    console.log(`🔌 WebSocket URL: ${WEBSOCKET_URL}/ws/{user_id}`);
    console.log(`📋 Health Check: ${PRODUCTION_URL}/health`);
    console.log(`📚 API Docs: ${PRODUCTION_URL}/docs`);
}

// Run the tests
runAllTests().catch(console.error);
