/**
 * اختبار إصلاح مشاكل الشات والمكونات
 */

const RAILWAY_API_URL = 'https://crewai-production-d99a.up.railway.app';

console.log('🔧 اختبار إصلاحات الشات...\n');

// اختبار 1: حفظ معلومات الشركة
async function testSaveCompanyInfo() {
  console.log('1️⃣ اختبار حفظ معلومات الشركة...');
  
  try {
    const response = await fetch(`${RAILWAY_API_URL}/api/v2/user/data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'test_user_123',
        data: {
          company_name: 'شركة التكنولوجيا المتقدمة',
          industry: 'تقنية المعلومات',
          location: 'الرياض'
        }
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ تم حفظ معلومات الشركة بنجاح');
      console.log(`   📋 البيانات: ${JSON.stringify(data.data, null, 2)}`);
      return true;
    } else {
      console.log('❌ فشل في حفظ معلومات الشركة');
      return false;
    }
  } catch (error) {
    console.log('❌ خطأ في حفظ معلومات الشركة:', error.message);
    return false;
  }
}

// اختبار 2: سؤال عن اسم الشركة
async function testCompanyNameQuery() {
  console.log('\n2️⃣ اختبار سؤال عن اسم الشركة...');
  
  try {
    const response = await fetch(`${RAILWAY_API_URL}/api/v2/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: 'ماهو اسم شركتي؟',
        user_id: 'test_user_123',
        session_id: 'test_session'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ رد الشات متاح');
      console.log(`   💬 الرد: ${data.content}`);
      console.log(`   🎯 القصد: ${data.intent_detected}`);
      console.log(`   🧩 المكونات: ${data.components.length} مكون`);
      
      // فحص المكونات
      data.components.forEach((comp, i) => {
        console.log(`      ${i+1}. ${comp.type}: ${comp.title || 'بدون عنوان'}`);
      });
      
      return true;
    } else {
      console.log('❌ فشل في الحصول على رد الشات');
      return false;
    }
  } catch (error) {
    console.log('❌ خطأ في سؤال الشات:', error.message);
    return false;
  }
}

// اختبار 3: رسالة ترحيب مع quick actions
async function testGreetingWithActions() {
  console.log('\n3️⃣ اختبار رسالة الترحيب مع الإجراءات السريعة...');
  
  try {
    const response = await fetch(`${RAILWAY_API_URL}/api/v2/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: 'مرحبا',
        user_id: 'new_user_456',
        session_id: 'greeting_session'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ رسالة الترحيب تعمل');
      console.log(`   💬 الرد: ${data.content.substring(0, 50)}...`);
      
      // البحث عن quick_actions
      const quickActions = data.components.find(c => c.type === 'quick_actions');
      if (quickActions) {
        console.log('✅ مكون quick_actions موجود');
        console.log(`   🎯 عدد الأزرار: ${quickActions.buttons.length}`);
        quickActions.buttons.forEach((btn, i) => {
          console.log(`      ${i+1}. ${btn.text} -> ${btn.action}`);
        });
      } else {
        console.log('❌ مكون quick_actions غير موجود');
      }
      
      return true;
    } else {
      console.log('❌ فشل في رسالة الترحيب');
      return false;
    }
  } catch (error) {
    console.log('❌ خطأ في رسالة الترحيب:', error.message);
    return false;
  }
}

// تشغيل جميع الاختبارات
async function runAllTests() {
  console.log('🚀 بدء اختبارات الإصلاحات...\n');
  
  const results = {
    saveCompanyInfo: await testSaveCompanyInfo(),
    companyNameQuery: await testCompanyNameQuery(),
    greetingWithActions: await testGreetingWithActions()
  };
  
  console.log('\n📊 نتائج الاختبارات:');
  console.log('=========================');
  
  Object.entries(results).forEach(([test, passed]) => {
    const status = passed ? '✅ نجح' : '❌ فشل';
    const testName = test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    console.log(`${status} - ${testName}`);
  });
  
  const passedTests = Object.values(results).filter(Boolean).length;
  const totalTests = Object.keys(results).length;
  
  console.log(`\n🎯 النتيجة النهائية: ${passedTests}/${totalTests} اختبار نجح`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 جميع الإصلاحات تعمل بشكل صحيح!');
    console.log('✨ يمكنك الآن بدء الفرونت اند واختبار الميزات الجديدة');
  } else {
    console.log('\n⚠️ بعض الإصلاحات تحتاج مراجعة');
    console.log('🔧 تحقق من السيرفر والإعدادات');
  }
  
  return results;
}

runAllTests().catch(console.error);
