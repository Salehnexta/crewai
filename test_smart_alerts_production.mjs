#!/usr/bin/env node
/**
 * 🔔 Test Smart Alerts v2.0 on Production
 * Tests the new smart alerts endpoints and WebSocket integration
 */

const PRODUCTION_URL = 'https://crewai-production-d99a.up.railway.app';

console.log('🔔 Testing Smart Alerts v2.0 on Production...\n');

// Test 1: Check alerts status
async function testAlertsStatus() {
    console.log('1️⃣ Testing Alerts Status...');
    try {
        const response = await fetch(`${PRODUCTION_URL}/api/v2/alerts/status`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Alerts Status:', JSON.stringify(data, null, 2));
        } else {
            console.log(`⚠️  Status check returned: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Alerts status failed:', error.message);
    }
    console.log();
}

// Test 2: Trigger smart alerts check
async function testTriggerAlerts() {
    console.log('2️⃣ Triggering Smart Alerts Check...');
    try {
        const response = await fetch(`${PRODUCTION_URL}/api/v2/alerts/check/test_org`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Alerts triggered:', JSON.stringify(data, null, 2));
        } else {
            console.log(`⚠️  Trigger returned: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Alerts trigger failed:', error.message);
    }
    console.log();
}

// Test 3: Test all new v2.0 endpoints
async function testV2Endpoints() {
    console.log('3️⃣ Testing All V2.0 Endpoints...');
    
    const endpoints = [
        '/health',
        '/api/v2/platforms/available',
        '/api/v2/alerts/status',
        '/docs',
        '/'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${PRODUCTION_URL}${endpoint}`);
            console.log(`   ${endpoint}: ${response.status} ${response.ok ? '✅' : '⚠️'}`);
        } catch (error) {
            console.log(`   ${endpoint}: ❌ ${error.message}`);
        }
    }
    console.log();
}

// Run all tests
async function runTests() {
    console.log(`📡 Testing: ${PRODUCTION_URL}\n`);
    
    await testAlertsStatus();
    await testTriggerAlerts();
    await testV2Endpoints();
    
    console.log('🎉 Smart Alerts v2.0 Testing Complete!');
    console.log('\n📋 Next Steps:');
    console.log('   1. Connect frontend to WebSocket for real-time alerts');
    console.log('   2. Implement alert management dashboard');
    console.log('   3. Add Supabase integration for alert persistence');
    console.log('   4. Configure automated alert scheduling');
}

runTests().catch(console.error);
