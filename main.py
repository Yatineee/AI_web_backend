from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from sqlmodel import Session, SQLModel, create_engine
from databases.session import SessionLog
from config.middleware import setup_middlewares
import httpx
from typing import Optional

app = FastAPI()
setup_middlewares(app)

# ✅ 注册详细的 422 错误捕获器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ 422 Validation Error:")
    print("➡️ 请求体:", await request.body())
    print("➡️ 错误详情:", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )


# ✅ 正确字段映射 + Pydantic v2 写法
class SessionData(BaseModel):
    user_id: str
    session_start_time: str
    session_duration_min: float
    active_period_label: str
    avg_video_duration_sec: float
    switch_frequency: float
    content_emotion_score: float
    content_type_keywords: List[str]
    repeated_viewing_ratio: float
    skipped_intro_ratio: float
    saved_to_favorites: bool
    # three_day_total_watch_time: float = Field(..., alias="3_day_total_watch_time")
    three_day_total_watch_time: Optional[float] = Field(0.0, alias="3_day_total_watch_time")
    short_video_ratio: float
    self_reported_goal: str
    ai_tone_description: str

    class Config:
        populate_by_name = True  # ✅ Pydantic v2 正确配置


engine = create_engine("sqlite:///./sessions.db")
SQLModel.metadata.create_all(engine)


def should_intervene(session: SessionData) -> bool:
    score = 0
    if session.session_duration_min > 20:
        score += 1
    if session.switch_frequency > 1.5:
        score += 1
    if session.content_emotion_score < -0.2:
        score += 1
    if session.short_video_ratio > 0.9:
        score += 1
    return score >= 2

# def should_intervene(session: SessionData) -> bool:
#     return (
#         session.session_duration_min > 45 and
#         session.switch_frequency > 2.0 and
#         session.content_emotion_score < -0.3
#     )

novita_client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key="sk_AAuPB1pBdcAHu85cbXj3w7-dE3KJAEqmuLmYlQMesDM"
)

def call_novita_gpt(goal: str, label: str, tone_desc: str) -> str:
    prompt = (
        f"The user currently feels '{label}' and their self-set goal is: '{goal}'.\n"
        f"They hope you respond in the following style: \"{tone_desc}\".\n"
        "Please provide a one-paragraph piece of advice in this tone that is supportive and emotionally appropriate."
    )
    chat_completion_res = novita_client.chat.completions.create(
        model="deepseek/deepseek-v3-0324",
        messages=[
            {"role": "system", "content": "You are a wellness AI that adapts to the user's tone."},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return chat_completion_res.choices[0].message.content

@app.post("/api/intervene")
async def intervene(session: SessionData):
    print("✅ 收到请求:", session.dict(by_alias=True))

    predict_payload = {
        "session_duration_min": session.session_duration_min,
        "active_period_label": session.active_period_label,
        "avg_video_duration_sec": session.avg_video_duration_sec,
        "switch_frequency": session.switch_frequency,
        "content_emotion_score": session.content_emotion_score,
        "content_type_keywords": session.content_type_keywords,
        "repeated_viewing_ratio": session.repeated_viewing_ratio,
        "skipped_intro_ratio": session.skipped_intro_ratio,
        "saved_to_favorites": session.saved_to_favorites,
        "3_day_total_watch_time": session.three_day_total_watch_time,
        "short_video_ratio": session.short_video_ratio
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://127.0.0.1:8001/predict", json=predict_payload)
            resp.raise_for_status()
            predicted_label = resp.json().get("predicted_state", "unknown")
    except Exception as e:
        print("❌ 分类模型调用失败:", e)
        predicted_label = "unknown"

    intervene_flag = should_intervene(session)
    advice = call_novita_gpt(session.self_reported_goal, predicted_label, session.ai_tone_description) \
        if intervene_flag else "You're doing fine!"

    session_dict = session.dict()
    session_dict["content_type_keywords"] = ",".join(session.content_type_keywords)

    log = SessionLog(
        **session_dict,
        predicted_label=predicted_label,
        intervention_level="medium" if intervene_flag else "normal",
        gpt_response=advice
    )

    with Session(engine) as db:
        db.add(log)
        db.commit()

    return {
        "level": "medium" if intervene_flag else "normal",
        "advice_text": advice
    }
