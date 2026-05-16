# Planning AI Backend - Render

Backend بسيط لتجربة ربط صفحة البحث في الأدلة التخطيطية مع API منشور على Render.

## الملفات

- `main.py`: تطبيق FastAPI.
- `requirements.txt`: مكتبات Python المطلوبة.
- `render.yaml`: إعدادات النشر على Render.

## أوامر Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## اختبار الخدمة

بعد النشر افتح:

```text
https://YOUR-RENDER-URL.onrender.com
```

ثم جرّب:

```text
https://YOUR-RENDER-URL.onrender.com/docs
```

## ربطه مع صفحة Netlify

في ملف `index.html` غيّر:

```javascript
const API_BASE_URL = "http://localhost:8000";
```

إلى رابط Render، مثل:

```javascript
const API_BASE_URL = "https://planning-ai-backend.onrender.com";
```
