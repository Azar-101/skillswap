from datetime import datetime, timezone
import json
from app.extensions import db


class LearningRoadmap(db.Model):
    __tablename__ = "learning_roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_title = db.Column(db.String(100), nullable=False)
    target_level = db.Column(db.String(50), default="Intermediate")
    summary = db.Column(db.Text, default="")
    plan_json = db.Column(db.Text, nullable=False)  # JSON with structured weeks/milestones
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="roadmaps")
    progress_items = db.relationship("RoadmapProgress", back_populates="roadmap", cascade="all, delete-orphan")

    @property
    def parsed_plan(self):
        try:
            return json.loads(self.plan_json)
        except Exception:
            return {}

    @property
    def completion_percentage(self) -> int:
        items = self.progress_items
        if not items:
            return 0
        done_count = sum(1 for item in items if item.done)
        return int((done_count / len(items)) * 100)

    def __repr__(self):
        return f"<LearningRoadmap id={self.id} skill={self.skill_title}>"


class RoadmapProgress(db.Model):
    __tablename__ = "roadmap_progress"

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("learning_roadmaps.id"), nullable=False, index=True)
    item_key = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), default="")
    done = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    roadmap = db.relationship("LearningRoadmap", back_populates="progress_items")

    def __repr__(self):
        return f"<RoadmapProgress roadmap_id={self.roadmap_id} item={self.item_key} done={self.done}>"


class GeneratedQuiz(db.Model):
    __tablename__ = "generated_quizzes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_title = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), default="Intermediate")
    questions_json = db.Column(db.Text, nullable=False)  # Contains questions, options, server-side answer & explanations
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="quizzes")
    attempts = db.relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan", order_by="desc(QuizAttempt.attempted_at)")

    @property
    def parsed_questions(self):
        try:
            return json.loads(self.questions_json)
        except Exception:
            return []

    @property
    def questions_for_client(self):
        """Strip correct_index and explanation before sending to learner until submitted!"""
        questions = self.parsed_questions
        sanitized = []
        for i, q in enumerate(questions):
            sanitized.append({
                "id": i,
                "question": q.get("question", ""),
                "options": q.get("options", []),
            })
        return sanitized

    def __repr__(self):
        return f"<GeneratedQuiz id={self.id} skill={self.skill_title}>"


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("generated_quizzes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    passed = db.Column(db.Boolean, default=False, nullable=False)
    answers_json = db.Column(db.Text, default="{}")
    attempted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    quiz = db.relationship("GeneratedQuiz", back_populates="attempts")
    user = db.relationship("User")

    @property
    def percentage(self) -> int:
        if not self.total_questions:
            return 0
        return int((self.score / self.total_questions) * 100)

    @property
    def parsed_answers(self):
        try:
            return json.loads(self.answers_json)
        except Exception:
            return {}

    def __repr__(self):
        return f"<QuizAttempt id={self.id} score={self.score}/{self.total_questions}>"


class AIConversation(db.Model):
    __tablename__ = "ai_conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), default="Learning Session")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="ai_conversations")
    messages = db.relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")

    def __repr__(self):
        return f"<AIConversation id={self.id} title={self.title}>"


class AIMessage(db.Model):
    __tablename__ = "ai_messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("ai_conversations.id"), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = db.relationship("AIConversation", back_populates="messages")

    def __repr__(self):
        return f"<AIMessage id={self.id} role={self.role}>"


class UserAIPrefs(db.Model):
    __tablename__ = "user_ai_prefs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    mode = db.Column(db.String(30), default="free")  # 'free', 'platform', 'byok'
    free_provider = db.Column(db.String(30), default="mock")  # 'mock', 'groq', 'ollama'
    encrypted_key = db.Column(db.LargeBinary, nullable=True)
    key_last4 = db.Column(db.String(8), nullable=True)
    model_override = db.Column(db.String(80), nullable=True)

    user = db.relationship("User", back_populates="ai_prefs")

    def __repr__(self):
        return f"<UserAIPrefs user_id={self.user_id} mode={self.mode}>"


class AIUsageLog(db.Model):
    __tablename__ = "ai_usage_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    provider = db.Column(db.String(50), nullable=False)
    feature = db.Column(db.String(50), nullable=False)  # 'roadmap', 'quiz', 'chat', 'matching'
    billing_source = db.Column(db.String(30), default="free")
    tokens_used = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="success")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<AIUsageLog id={self.id} feature={self.feature} status={self.status}>"
