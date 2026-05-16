from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(
    title="Planning AI Search API",
    description="Backend API for the Planning Guidelines AI Search Page",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "message": "Planning AI Search API is running"
    }


@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        return {
            "answer": "لم يتم إدخال سؤال.",
            "sources": []
        }

    return {
        "answer": (
            "تم استقبال السؤال التالي:\n\n"
            f"{question}\n\n"
            "هذه إجابة تجريبية من Backend المنشور على Render. "
            "في المرحلة التالية سيتم ربط هذا المسار بقاعدة الأدلة التخطيطية لاستخراج الإجابة الموثقة حسب اسم الدليل ورقم الصفحة."
        ),
        "sources": [
            {
                "guide_name": "مثال: دليل متطلبات اعتماد المخططات",
                "issue_date": "غير مذكور",
                "page": "12",
                "excerpt": "هذا مقتطف تجريبي. لاحقًا سيتم استبداله بالنص الفعلي المستخرج من ملفات الأدلة التخطيطية."
            }
        ]
    }
