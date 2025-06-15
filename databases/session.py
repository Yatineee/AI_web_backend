from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SessionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # 自动编号主键
    user_id: str
    session_start_time: str
    session_duration_min: float
    active_period_label: str
    avg_video_duration_sec: float
    switch_frequency: float
    content_emotion_score: float
    content_type_keywords: str  # 列表转字符串后存入
    repeated_viewing_ratio: float
    skipped_intro_ratio: float
    saved_to_favorites: bool
    _3_day_total_watch_time: float
    short_video_ratio: float
    self_reported_goal: str
    predicted_label: str         # AI分类结果
    intervention_level: str      # 提醒等级
    gpt_response: str            # GPT生成的文本
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # 自动记录保存时间
