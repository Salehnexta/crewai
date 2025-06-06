#!/usr/bin/env node

/**
 * 🤖 Test Chat Features - Morvo AI
 * اختبار شامل لميزات الشات التفاعلية
 */

import fetch from 'node-fetch';

const BASE_URL = 'https://crewai-production-d99a.up.railway.app';

// ألوان للطباعة
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

const log = (color, message) => console.log(`${colors[color]}${message}${colors.reset}`);

async function testChatMessage(content, expectedComponents = true) {
    log('blue', `\n🧪 Testing: "${content}"`);
    
    try {
        const response = await fetch(`${BASE_URL}/api/v2/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                user_id: 'test-user-' + Date.now(),
                session_id: 'test-session-' + Date.now()
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // التحقق من البيانات الأساسية
        log('green', `✅ Content: ${data.content?.substring(0, 50)}...`);
        log('cyan', `📊 Message Type: ${data.message_type}`);
        log('cyan', `🎯 Intent: ${data.intent_detected || 'N/A'}`);
        log('cyan', `🔢 Confidence: ${data.confidence_score || 'N/A'}`);
        
        // التحقق من المكونات التفاعلية
        const components = data.components || data.rich_components || [];
        const componentField = data.components ? 'components' : 'rich_components';
        
        log('magenta', `🧩 Using field: ${componentField}`);
        log('magenta', `🧩 Components count: ${components.length}`);
        
        if (expectedComponents && components.length > 0) {
            log('green', `✅ Has interactive components!`);
            
            components.forEach((comp, index) => {
                log('yellow', `  Component ${index + 1}:`);
                log('yellow', `    Type: ${comp.type}`);
                log('yellow', `    Title: ${comp.title || 'N/A'}`);
                
                if (comp.buttons) {
                    log('yellow', `    Buttons: ${comp.buttons.length}`);
                    comp.buttons.forEach((btn, btnIndex) => {
                        log('cyan', `      ${btnIndex + 1}. ${btn.text} (${btn.action})`);
                    });
                }
                
                if (comp.fields) {
                    log('yellow', `    Form Fields: ${comp.fields.length}`);
                }
            });
        } else if (expectedComponents) {
            log('red', `❌ Expected components but got none`);
        } else {
            log('green', `✅ No components expected and none received`);
        }
        
        return {
            success: true,
            hasComponents: components.length > 0,
            componentField: componentField,
            data: data
        };
        
    } catch (error) {
        log('red', `❌ Error: ${error.message}`);
        return {
            success: false,
            error: error.message
        };
    }
}

async function testUserDataSaving() {
    log('blue', `\n💾 Testing User Data Saving`);
    
    try {
        const response = await fetch(`${BASE_URL}/api/v2/user/data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 'test-user-data-' + Date.now(),
                data: {
                    company_name: 'شركة اختبار',
                    industry: 'تقنية',
                    website: 'https://test.com'
                }
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        log('green', `✅ User data saved successfully`);
        log('cyan', `📄 Response: ${JSON.stringify(data)}`);
        
        return { success: true, data };
        
    } catch (error) {
        log('red', `❌ Error saving user data: ${error.message}`);
        return { success: false, error: error.message };
    }
}

async function runTests() {
    log('bold', '🚀 بدء اختبار ميزات مورفو AI الشات');
    log('bold', '=====================================\n');
    
    const tests = [
        // اختبار رسالة الترحيب مع الأزرار
        {
            name: 'Greeting with Quick Actions',
            content: 'مرحبا',
            expectComponents: true
        },
        
        // اختبار طلب تحليل موقع
        {
            name: 'Website Analysis Request', 
            content: 'أريد تحليل موقعي',
            expectComponents: true
        },
        
        // اختبار سؤال عام
        {
            name: 'General Question',
            content: 'ما هو التسويق الرقمي؟',
            expectComponents: false
        },
        
        // اختبار ربط منصة
        {
            name: 'Platform Connection',
            content: 'كيف أربط متجري؟',
            expectComponents: true
        }
    ];
    
    const results = [];
    
    for (const test of tests) {
        const result = await testChatMessage(test.content, test.expectComponents);
        results.push({
            ...test,
            ...result
        });
        
        // انتظار قصير بين الاختبارات
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    // اختبار حفظ بيانات المستخدم
    const userDataResult = await testUserDataSaving();
    results.push({
        name: 'User Data Saving',
        ...userDataResult
    });
    
    // تقرير النتائج
    log('bold', '\n📊 ملخص نتائج الاختبار');
    log('bold', '====================\n');
    
    let passed = 0;
    let total = results.length;
    
    results.forEach(result => {
        if (result.success) {
            log('green', `✅ ${result.name}: PASSED`);
            passed++;
        } else {
            log('red', `❌ ${result.name}: FAILED - ${result.error}`);
        }
    });
    
    log('bold', `\n🎯 النتيجة النهائية: ${passed}/${total} اختبارات نجحت`);
    
    if (passed === total) {
        log('green', '🎉 جميع الاختبارات نجحت! الشات جاهز للاستخدام');
    } else {
        log('yellow', '⚠️ بعض الاختبارات فشلت، يرجى المراجعة');
    }
    
    // اختبار field name
    const componentsFieldTest = results.find(r => r.hasComponents);
    if (componentsFieldTest) {
        log('cyan', `\n🔧 API يستخدم حقل: ${componentsFieldTest.componentField}`);
        if (componentsFieldTest.componentField === 'components') {
            log('green', '✅ API يستخدم التسمية الصحيحة: components');
        } else {
            log('yellow', '⚠️ API لا يزال يستخدم: rich_components (يحتاج إصلاح)');
        }
    }
}

// تشغيل الاختبارات
runTests().catch(console.error);
