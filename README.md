# Planning AI Backend with OpenAI Vector Store

هذا Backend يربط صفحة Netlify مع OpenAI Vector Store.

## الملفات

- `main.py`: API endpoint `/ask`.
- `upload_to_vector_store.py`: سكربت محلي لرفع ملفات الأدلة إلى OpenAI Vector Store.
- `requirements.txt`: مكتبات Python.
- `render.yaml`: إعدادات Render.
- `.python-version`: لتثبيت Python 3.11.9 على Render.

## متغيرات البيئة المطلوبة في Render

```text
OPENAI_API_KEY=ضع مفتاح OpenAI API هنا
OPENAI_VECTOR_STORE_ID=ضع رقم Vector Store هنا
OPENAI_MODEL=gpt-4.1-mini
```

## رفع الأدلة إلى Vector Store

على جهازك:

```bash
pip install -r requirements.txt
set OPENAI_API_KEY=sk-...
python upload_to_vector_store.py --folder "C:\path\to\Planning_Knowledge_Base" --name "Planning Knowledge Base"
```

على Mac/Linux:

```bash
export OPENAI_API_KEY=sk-...
python upload_to_vector_store.py --folder "/path/to/Planning_Knowledge_Base" --name "Planning Knowledge Base"
```

بعد الانتهاء سيظهر:

```text
OPENAI_VECTOR_STORE_ID=vs_...
```

انسخه وضعه في Render.

## إعدادات Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
