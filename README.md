# Planning AI Backend - Render

Backend بسيط لتجربة ربط صفحة البحث في الأدلة التخطيطية مع API منشور على Render.

## الملفات المطلوبة في جذر مستودع GitHub

يجب أن تكون الملفات بهذا الشكل، وليس داخل مجلد فرعي:

```text
main.py
requirements.txt
render.yaml
runtime.txt
README.md
```

## إعدادات Render

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

ثم:

```text
https://YOUR-RENDER-URL.onrender.com/docs
```
