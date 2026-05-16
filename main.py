import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(
    title="Planning AI Search API",
    description="Backend API connected to OpenAI Vector Store for planning guideline search.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # لاحقًا يمكنك استبدالها برابط Netlify فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Planning AI Search API is running with OpenAI Vector Store support",
        "vector_store_configured": bool(OPENAI_VECTOR_STORE_ID),
        "model": OPENAI_MODEL,
    }


def extract_output_text(response: Any) -> str:
    """يحاول استخراج النص النهائي من استجابة Responses API."""
    text = getattr(response, "output_text", None)
    if text:
        return text

    data = response.model_dump() if hasattr(response, "model_dump") else response
    chunks: List[str] = []

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                if content.get("text"):
                    chunks.append(content["text"])

    return "\n".join(chunks).strip()


def extract_file_search_sources(response: Any) -> List[Dict[str, str]]:
    """
    يستخرج نتائج file_search إن وجدت.
    ملاحظة: OpenAI Vector Store لا يضمن إرجاع رقم الصفحة الأصلي دائماً.
    الأفضل لإظهار رقم الصفحة بدقة أن تكون ملفاتك مفهرسة مع page markers قبل رفعها.
    """
    data = response.model_dump() if hasattr(response, "model_dump") else response
    sources: List[Dict[str, str]] = []

    for item in data.get("output", []):
        if item.get("type") == "file_search_call":
            for result in item.get("results", []) or []:
                content_text = ""
                for c in result.get("content", []) or []:
                    if isinstance(c, dict) and c.get("text"):
                        content_text += c.get("text", "")[:700]

                filename = (
                    result.get("filename")
                    or result.get("file_name")
                    or result.get("title")
                    or result.get("file_id")
                    or "مصدر من قاعدة الأدلة"
                )

                sources.append({
                    "guide_name": filename,
                    "issue_date": "غير مذكور",
                    "page": "غير متاح مباشرة",
                    "excerpt": content_text or "تم استخدام هذا المصدر في البحث، ولم يظهر مقتطف نصي واضح."
                })

    # إزالة التكرار حسب الاسم والمقتطف
    unique = []
    seen = set()
    for src in sources:
        key = (src["guide_name"], src["excerpt"][:120])
        if key not in seen:
            seen.add(key)
            unique.append(src)

    return unique[:5]


@app.post("/ask")
def ask(request: AskRequest):
    if not OPENAI_API_KEY or not client:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured in Render environment variables."
        )

    if not OPENAI_VECTOR_STORE_ID:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_VECTOR_STORE_ID is not configured in Render environment variables."
        )

    question = request.question.strip()

    if not question:
        return {
            "answer": "لم يتم إدخال سؤال.",
            "sources": []
        }

    system_prompt = """
أنت مساعد متخصص في الأدلة التخطيطية والاشتراطات العمرانية.
أجب فقط بناءً على الملفات الموجودة في قاعدة المعرفة.
لا تخترع أي معلومة غير موجودة في المصادر.
إذا لم تجد إجابة واضحة، قل: لا توجد معلومة كافية في الأدلة المتاحة.
اكتب الإجابة بالعربية الرسمية المختصرة.
عند وجود متطلبات، اعرضها كنقاط واضحة.
اذكر اسم الدليل أو المصدر إن ظهر لك.
إذا كان رقم الصفحة غير موجود في النص المسترجع، لا تخترع رقم صفحة.
"""

    user_input = f"""
السؤال:
{question}

المطلوب:
- أجب بناءً على الأدلة التخطيطية فقط.
- استخرج المتطلبات أو الاشتراطات ذات العلاقة.
- لا تضف معلومات من خارج الأدلة.
- إذا ظهرت أرقام أو نسب أو مدد أو مساحات، اذكرها كما وردت.
"""

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            tools=[{
                "type": "file_search",
                "vector_store_ids": [OPENAI_VECTOR_STORE_ID],
                "max_num_results": 5
            }],
            include=["file_search_call.results"],
        )

        answer = extract_output_text(response)
        sources = extract_file_search_sources(response)

        return {
            "answer": answer or "لم يتم العثور على إجابة واضحة في الأدلة المتاحة.",
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI Vector Store search failed: {str(e)}"
        )
