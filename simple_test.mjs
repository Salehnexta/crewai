#!/usr/bin/env node

/**
 * 🤖 Simple Chat Test - Morvo AI
 */

const BASE_URL = 'https://crewai-production-d99a.up.railway.app';

async function testGreeting() {
    console.log('🧪 Testing Greeting Message...\n');
    
    try {
        const response = await fetch(`${BASE_URL}/api/v2/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: 'مرحبا',
                user_id: 'test-user',
                session_id: 'test-session'
            })
        });

        const data = await response.json();
        
        console.log('✅ Response received:');
        console.log('📝 Content:', data.content?.substring(0, 50) + '...');
        console.log('🧩 Fields:', Object.keys(data));
        
        const hasComponents = data.components && data.components.length > 0;
        const hasRichComponents = data.rich_components && data.rich_components.length > 0;
        
        if (hasComponents) {
            console.log('✅ Using COMPONENTS field:', data.components.length, 'components');
            console.log('🎯 First component type:', data.components[0]?.type);
        } else if (hasRichComponents) {
            console.log('⚠️ Using RICH_COMPONENTS field:', data.rich_components.length, 'components');
            console.log('🎯 First component type:', data.rich_components[0]?.type);
            console.log('🔧 Frontend should adapt to use "rich_components" field');
        } else {
            console.log('❌ No components found');
        }
        
        // اختبار بيانات المستخدم
        console.log('\n💾 Testing User Data...');
        
        const userResponse = await fetch(`${BASE_URL}/api/v2/user/data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 'test-user',
                data: {
                    company_name: 'شركة اختبار',
                    industry: 'تقنية'
                }
            })
        });
        
        const userData = await userResponse.json();
        console.log('✅ User data response:', userData);
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

testGreeting();
