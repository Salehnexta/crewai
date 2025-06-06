# 🤖 Morvo AI - Clean Production Build

نسخة نظيفة ومبسطة من Morvo AI مصممة خصيصاً لضمان نجاح النشر على Railway.

## ✅ الميزات
- FastAPI + WebSocket
- Chat API مع اكتشاف القصد
- مكونات تفاعلية (أزرار سريعة)
- دعم اللغة العربية
- Healthcheck endpoint

## 🚀 النشر على Railway
```bash
# إنشاء git repository
git init
git add .
git commit -m "Initial commit"

# ربط بـ GitHub ونشر على Railway
```

## 📋 API Endpoints
- `GET /` - الصفحة الرئيسية
- `GET /health` - فحص الصحة
- `POST /api/v2/chat/message` - API المحادثة
- `WebSocket /ws/{user_id}` - اتصال مباشر

## 🔧 التكوين
- Python 3.10+
- Minimal dependencies
- Nixpacks builder only
- No Node.js conflicts
