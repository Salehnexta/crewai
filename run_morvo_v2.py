#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 مورفو AI v2.0 - تشغيل الخادم المحلي
خادم FastAPI محسن للتسويق الذكي
"""

import os
import sys
import logging
import subprocess
import signal
from pathlib import Path

# إضافة المجلد الحالي إلى المسار
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# تكوين السجلات البسيط
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('morvo_api.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة إذا توفرت
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ تم تحميل متغيرات البيئة من .env")
except ImportError:
    logger.warning("⚠️ python-dotenv غير مثبت - سيتم استخدام متغيرات النظام")

def check_dependencies():
    """التحقق من المتطلبات الأساسية"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ المتطلبات المفقودة: {', '.join(missing_packages)}")
        logger.info("قم بتشغيل: pip install fastapi uvicorn pydantic")
        return False
    
    logger.info("✅ جميع المتطلبات الأساسية متوفرة")
    return True

def start_server():
    """بدء تشغيل الخادم"""
    try:
        # التحقق من وجود ملف API
        api_file = current_dir / "morvo_api_v2.py"
        if not api_file.exists():
            logger.error(f"❌ ملف API غير موجود: {api_file}")
            return False
        
        logger.info("🚀 بدء تشغيل مورفو AI v2.0...")
        logger.info(f"📂 المجلد: {current_dir}")
        logger.info(f"🌐 الخادم: http://localhost:8090")
        logger.info(f"📚 المستندات: http://localhost:8090/docs")
        
        # تشغيل الخادم
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "morvo_api_v2:app",
            "--host", "0.0.0.0",
            "--port", "8090",
            "--reload"
        ], cwd=current_dir)
        
        # التعامل مع إيقاف الخادم
        def signal_handler(sig, frame):
            logger.info("🛑 إيقاف الخادم...")
            process.terminate()
            process.wait()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # انتظار انتهاء العملية
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 تم إيقاف الخادم بواسطة المستخدم")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل الخادم: {e}")
        return False
    
    return True

def main():
    """الوظيفة الرئيسية"""
    print("🤖 مورفو AI v2.0 - مساعد التسويق الذكي")
    print("=" * 50)
    
    # التحقق من المتطلبات
    if not check_dependencies():
        sys.exit(1)
    
    # بدء الخادم
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()
