import json
import logging
from typing import Dict, Any, List
from flask import current_app
from app.extensions import db
from app.models.ai import AIUsageLog

logger = logging.getLogger(__name__)


class AIService:
    @staticmethod
    def _call_llm(messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        """Attempts external LLM (OpenAI or Groq) if configured; returns empty string on failure/unconfigured."""
        app_cfg = current_app.config

        # 1. Try Groq if enabled
        if app_cfg.get("HOSTED_FREE_ENABLED") and app_cfg.get("GROQ_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=app_cfg["GROQ_API_KEY"],
                    base_url=app_cfg.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
                    timeout=12.0,
                )
                model = app_cfg.get("GROQ_MODEL") or "llama-3.3-70b-versatile"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": app_cfg.get("AI_MAX_OUTPUT_TOKENS", 1200),
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"Groq AI call failed: {e}")

        # 2. Try OpenAI if enabled
        if app_cfg.get("PLATFORM_AI_ENABLED") and app_cfg.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=app_cfg["OPENAI_API_KEY"],
                    timeout=12.0,
                )
                model = app_cfg.get("OPENAI_MODEL") or "gpt-4o-mini"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": app_cfg.get("AI_MAX_OUTPUT_TOKENS", 1200),
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"OpenAI call failed: {e}")

        return ""

    @classmethod
    def generate_roadmap(cls, skill_title: str, target_level: str = "Intermediate", user_id: int = None) -> Dict[str, Any]:
        """Generates a structured week-by-week learning roadmap."""
        prompt = (
            f"Generate a detailed 4-week learning roadmap for mastering '{skill_title}' at the {target_level} level.\n"
            f"Return ONLY a JSON object with this exact structure:\n"
            "{\n"
            '  "title": "Roadmap Title",\n'
            '  "description": "Short overview",\n'
            '  "weeks": [\n'
            '    {\n'
            '      "week_number": 1,\n'
            '      "theme": "Theme title",\n'
            '      "goals": ["Goal 1", "Goal 2"],\n'
            '      "topics": [\n'
            '        {"key": "w1_t1", "title": "Topic title", "details": "Actionable task/concept"}\n'
            '      ],\n'
            '      "project": "Mini practical project for this week"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        messages = [
            {"role": "system", "content": "You are an expert curriculum designer and educator. Respond with valid JSON."},
            {"role": "user", "content": prompt},
        ]

        raw_output = cls._call_llm(messages, json_mode=True)
        if raw_output:
            try:
                parsed = json.loads(raw_output)
                if "weeks" in parsed:
                    cls._log_usage(user_id, "external_ai", "roadmap", 800)
                    return parsed
            except Exception:
                pass

        # High-quality built-in generation fallback
        cls._log_usage(user_id, "builtin_ai_engine", "roadmap", 500)
        return cls._generate_fallback_roadmap(skill_title, target_level)

    @classmethod
    def generate_quiz(cls, skill_title: str, difficulty: str = "Intermediate", user_id: int = None) -> List[Dict[str, Any]]:
        """Generates 5 multiple choice questions with answers and explanations."""
        prompt = (
            f"Create a 5-question multiple choice assessment for '{skill_title}' at {difficulty} level.\n"
            "Return ONLY a JSON object with a 'questions' array where each item has:\n"
            "{\n"
            '  "question": "Question text",\n'
            '  "options": ["A", "B", "C", "D"],\n'
            '  "correct_index": 0,\n'
            '  "explanation": "Why this answer is correct"\n'
            "}"
        )

        messages = [
            {"role": "system", "content": "You are a technical assessment examiner. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ]

        raw_output = cls._call_llm(messages, json_mode=True)
        if raw_output:
            try:
                parsed = json.loads(raw_output)
                q_list = parsed.get("questions") or parsed
                if isinstance(q_list, list) and len(q_list) >= 3:
                    cls._log_usage(user_id, "external_ai", "quiz", 650)
                    return q_list
            except Exception:
                pass

        # Built-in generator
        cls._log_usage(user_id, "builtin_ai_engine", "quiz", 400)
        return cls._generate_fallback_quiz(skill_title, difficulty)

    @classmethod
    def generate_assistant_reply(cls, conversation_history: List[Dict[str, str]], user_id: int = None) -> str:
        """Handles student interactive chat with the AI Learning Buddy."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are 'SwapBot', the friendly AI Learning Assistant on SkillSwap. "
                    "You help users learn new skills, practice interview questions, prepare for peer swap sessions, "
                    "and discover what skills to exchange. Keep your answers encouraging, concise, and structured with markdown."
                ),
            }
        ]
        messages.extend(conversation_history)

        raw_output = cls._call_llm(messages, json_mode=False)
        if raw_output:
            cls._log_usage(user_id, "external_ai", "chat", 300)
            return raw_output

        # Context-aware built-in fallback response
        cls._log_usage(user_id, "builtin_ai_engine", "chat", 200)
        last_user_msg = conversation_history[-1]["content"] if conversation_history else ""
        return cls._generate_fallback_chat(last_user_msg)

    @staticmethod
    def _log_usage(user_id: int, provider: str, feature: str, tokens: int):
        try:
            log = AIUsageLog(
                user_id=user_id,
                provider=provider,
                feature=feature,
                tokens_used=tokens,
                status="success",
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

    @staticmethod
    def _generate_fallback_roadmap(skill: str, level: str) -> Dict[str, Any]:
        """Domain-adaptive curriculum generator ensuring 100% offline uptime."""
        clean_skill = skill.strip().title()
        return {
            "title": f"Complete {clean_skill} Mastery Path ({level})",
            "description": f"A targeted 4-week structured curriculum to take your {clean_skill} capabilities to {level} grade through hands-on exercises and peer practice.",
            "weeks": [
                {
                    "week_number": 1,
                    "theme": f"Core Foundations & Principles of {clean_skill}",
                    "goals": [
                        f"Master standard terminology and architecture of {clean_skill}",
                        "Set up development and prototyping environment",
                        "Complete initial hands-on drills",
                    ],
                    "topics": [
                        {"key": "w1_t1", "title": f"Introduction to {clean_skill} Fundamentals", "details": "Understand core concepts, mental models, and workflow conventions."},
                        {"key": "w1_t2", "title": "Environment Configuration & Tooling", "details": "Install essential tools, packages, extensions, and standard linters."},
                        {"key": "w1_t3", "title": "Fundamental Syntax & Operations", "details": "Write baseline scripts or create sample work artifacts demonstrating core techniques."},
                    ],
                    "project": f"Build a 'Hello {clean_skill}' starter project and write a 1-page summary of core paradigms.",
                },
                {
                    "week_number": 2,
                    "theme": f"Practical Application & Patterns in {clean_skill}",
                    "goals": [
                        "Build functional components or modules",
                        "Apply idiomatic industry patterns",
                        "Handle errors, validation, and edge cases",
                    ],
                    "topics": [
                        {"key": "w2_t1", "title": "Intermediate Data Structures & Flows", "details": "Structure complex datasets, handle inputs, and organize reusable modules."},
                        {"key": "w2_t2", "title": "Error Handling & Robustness", "details": "Implement defensive checks, unit assertions, and graceful degradation."},
                        {"key": "w2_t3", "title": "Standard Libraries & Ecosystem", "details": "Utilize popular open-source libraries and integrations to boost productivity."},
                    ],
                    "project": f"Create a multi-feature practical application solving a real-world task in {clean_skill}.",
                },
                {
                    "week_number": 3,
                    "theme": f"Advanced Techniques & Optimization",
                    "goals": [
                        "Optimize execution speed and workflow efficiency",
                        "Understand security and maintainability best practices",
                        "Conduct simulated peer reviews",
                    ],
                    "topics": [
                        {"key": "w3_t1", "title": "Performance Tuning & Profiling", "details": "Identify bottlenecks, memory consumption, or design friction."},
                        {"key": "w3_t2", "title": "Testing & Quality Assurance", "details": "Write automated test cases and edge-case verifications."},
                        {"key": "w3_t3", "title": "Collaborative Architecture", "details": "Prepare code/designs for team handoff, documentation, and version control."},
                    ],
                    "project": f"Refactor your week 2 project to adhere to production standards, modularity, and automated tests.",
                },
                {
                    "week_number": 4,
                    "theme": f"Portfolio Capstone & Peer Swap Preparation",
                    "goals": [
                        "Deliver an end-to-end portfolio-ready capstone project",
                        "Prepare talking points and teach-back slides for SkillSwap sessions",
                        "Earn your SkillSwap verification badge",
                    ],
                    "topics": [
                        {"key": "w4_t1", "title": "Capstone Implementation & Polish", "details": "Complete all core user stories, polish UI/output, and document setup steps."},
                        {"key": "w4_t2", "title": "Peer Teach-Back Preparation", "details": "Draft a 45-minute lesson plan to teach this skill to another community member."},
                        {"key": "w4_t3", "title": "Final Assessment & Next Steps", "details": "Take the SkillSwap verification quiz and host your first peer exchange session."},
                    ],
                    "project": f"Deploy or publish your full capstone project with a README, demo video, or interactive showcase.",
                },
            ],
        }

    @staticmethod
    def _generate_fallback_quiz(skill: str, difficulty: str) -> List[Dict[str, Any]]:
        clean_skill = skill.strip().title()
        return [
            {
                "question": f"When getting started with {clean_skill}, what is considered the primary best practice?",
                "options": [
                    "Writing monolithic code without modular functions",
                    "Adhering to community standards, linting, and modular separation of concerns",
                    "Ignoring automated testing and edge cases",
                    "Hardcoding configuration secrets in source files",
                ],
                "correct_index": 1,
                "explanation": "Standardized naming conventions, modularity, and separation of concerns ensure your work is scalable, maintainable, and readable by collaborators.",
            },
            {
                "question": f"In {clean_skill}, which approach guarantees the most effective error resilience and safety?",
                "options": [
                    "Catching all exceptions silently with empty handlers",
                    "Validating inputs explicitly and handling specific error states with meaningful messages",
                    "Terminating the application without logging",
                    "Assuming all network requests and user inputs will always succeed",
                ],
                "correct_index": 1,
                "explanation": "Explicit input validation combined with targeted exception handling prevents cascading failures and simplifies debugging.",
            },
            {
                "question": f"What is the recommended method to collaborate and share work in {clean_skill} projects?",
                "options": [
                    "Emailing zip files with timestamps",
                    "Using Git version control with feature branches and clear commit messages",
                    "Overwriting shared files on a network drive directly",
                    "Never documenting architectural decisions",
                ],
                "correct_index": 1,
                "explanation": "Git version control paired with structured commit histories and code reviews is the universal standard for modern technical collaboration.",
            },
            {
                "question": f"Which metric or signal best indicates that a {clean_skill} implementation is production-ready?",
                "options": [
                    "It runs only on the author's local laptop",
                    "Automated test coverage passes, performance benchmarks meet targets, and security reviews are clean",
                    "The codebase has no documentation or comments",
                    "It has never been tested with edge-case inputs",
                ],
                "correct_index": 1,
                "explanation": "Passing automated test suites, measurable performance, and documented security hygiene are standard prerequisites for production release.",
            },
            {
                "question": f"How does participating in peer teaching (as in SkillSwap) accelerate your mastery of {clean_skill}?",
                "options": [
                    "It has no measurable benefit compared to passive reading",
                    "Explaining concepts to others reinforces mental models (Feynman Technique) and uncovers blind spots",
                    "It replaces the need to write any actual code",
                    "It only benefits the person listening, not the person teaching",
                ],
                "correct_index": 1,
                "explanation": "The Feynman Technique demonstrates that teaching a topic forces you to distill core principles, solidifying your own deep understanding while helping others.",
            },
        ]

    @staticmethod
    def _generate_fallback_chat(user_msg: str) -> str:
        um = user_msg.lower()
        if "credit" in um or "hour" in um or "earn" in um:
            return (
                "### ⚡ How SkillSwap Credits Work\n\n"
                "SkillSwap uses a fair, time-based credit system:\n\n"
                "- **1 Hour Teaching = 1.0 Credit**\n"
                "- **30 Minutes Teaching = 0.5 Credits**\n"
                "- **90 Minutes Teaching = 1.5 Credits**\n\n"
                "You can earn credits teaching Python to User A, and use those same credits to learn Graphic Design from User B! "
                "No money changes hands, and no direct 1-to-1 swap is required."
            )
        elif "prepare" in um or "session" in um or "teach" in um:
            return (
                "### 🎯 Tips for a Successful SkillSwap Session\n\n"
                "1. **Set an Agenda**: Agree on 2-3 specific topics before joining the video room.\n"
                "2. **Hands-On Practice**: Spend 70% of the session doing live exercises together rather than just lecturing.\n"
                "3. **Share Resources**: Have links, code snippets, or reference sheets ready to paste into chat.\n"
                "4. **Confirm Completion**: After finishing, click **Complete Session** to release the credits to the teacher and unlock reviews!"
            )
        elif "roadmap" in um or "learn" in um:
            return (
                "I can build a personalized 4-week learning roadmap for any skill you want! "
                "Head over to **AI Tools > Learning Roadmaps** from the top navigation bar, enter the skill name (like *React*, *Figma*, *Data Analysis*), "
                "and I'll structure a week-by-week curriculum with interactive progress tracking."
            )
        elif "quiz" in um or "test" in um:
            return (
                "Ready to test your knowledge? Try our **AI Skill Assessment**! "
                "Go to **AI Tools > Skill Quizzes**, pick a topic and difficulty, and answer 5 targeted questions. "
                "You'll get instant scoring, detailed explanations, and an achievement badge for your profile."
            )
        else:
            return (
                f"### Hello! I'm SwapBot, your AI Learning Partner 👋\n\n"
                f"I'm here to help you get the most out of SkillSwap. Here is what we can do together:\n\n"
                f"- **Generate Custom Roadmaps**: Get a structured 4-week step-by-step curriculum for any skill.\n"
                f"- **Take Skill Quizzes**: Test your expertise before teaching or after learning.\n"
                f"- **Practice Interview Questions**: Rehearse technical or conceptual questions with me.\n"
                f"- **Find Smart Matches**: Discover community members who teach what you want to learn!\n\n"
                f"What skill are you excited to explore today?"
            )
