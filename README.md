# SkillSwap — AI-Powered Time-Based Skill Exchange and Learning Platform

> **College Major Project Final MVP**  
> **Backend:** Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug  
> **Database:** SQLite (default with automated table bootstrapping and foreign key enforcement)  
> **Frontend:** Responsive Bootstrap 5.3, Bootstrap Icons, Modern Inter Typography  
> **Video:** Integrated Jitsi Meet External API  
> **AI Architecture:** Multi-provider (OpenAI, Groq, Ollama) with intelligent built-in domain fallback engine

---

## 🌟 Executive Summary

SkillSwap is a community-driven peer learning platform where users exchange knowledge without monetary transactions. By treating time as a universal currency (1 hour teaching = 1 credit), SkillSwap removes financial barriers to skill acquisition while guaranteeing fair exchange via an automated credit escrow ledger.

---

## 🚀 Key Modules & Architecture

```
Browser (Bootstrap 5.3 + JavaScript)
   │   HTTPS, CSRF Protection, REST
Flask Blueprints:
   ├── auth: User authentication, registration, profiles, signup bonus
   ├── dashboard: Central user hub, stats, notifications, quick actions
   ├── skills: Marketplace, search, category filters, listings (offers & wants)
   ├── bookings: Session request, acceptance, credit escrow hold, completion
   ├── video: Embedded Jitsi video rooms, timer, live notepad
   ├── wallet: Credit balances, escrow reservations, transaction ledger
   ├── reviews: 5-star ratings and written peer feedback
   ├── notifications: In-app real-time alerts
   ├── ai: Smart matchmaker, 4-week roadmaps, skill quizzes, SwapBot
   ├── admin: System oversight, dispute arbitrage, user moderation, database seeding
   └── settings: AI provider configuration (Groq, OpenAI, Ollama, Mock)
   │
Services Layer: (wallet_service, booking_service, matching_service, ai_service, notification_service)
   │
SQLAlchemy ORM ──> SQLite (skillswap.db)
```

---

## ⏱️ Credit Economics

- **1 Hour Teaching = 1.0 Credit**
- **30 Minutes Teaching = 0.5 Credits**
- **90 Minutes Teaching = 1.5 Credits**
- **120 Minutes Teaching = 2.0 Credits**
- **Non-Reciprocal Liquidity:** User A teaches Python to User B (earns 1.0 credit). User A spends that 1.0 credit learning UI/UX from User C. No direct barter required!
- **Escrow Integrity:** When a session is accepted, credits are locked in reservation status (`held`). Upon completion, credits transfer to the tutor. If cancelled, credits return to the learner.

---

## 🎬 3-Minute College Evaluation Demo Script

Follow this step-by-step walkthrough to impress your project evaluator:

### Step 1: Landing Page & Concept (40 seconds)
1. Run `python run.py` and open `http://127.0.0.1:5000`.
2. Show the evaluator the hero section: explain the **Tri-Swap diagram** (Alex -> Marcus -> Sarah -> Alex). Emphasize that **time is the currency, zero cash required**.
3. Point out the popular skill categories (Programming, Design, Languages, Business, Music).

### Step 2: Login & Student Dashboard (40 seconds)
1. Click **Sign In** and use the pre-seeded account: `alex@skillswap.com` / `UserPass123!`.
2. Highlight the top navigation bar:
   - Available balance pill (`⚡ 4.0 Credits`).
   - Notification bell.
3. Show the **Dashboard**: stats cards, upcoming session with Sarah Chen, and the **AI Recommended Matches** widget.

### Step 3: Marketplace & Booking with Escrow (40 seconds)
1. Navigate to **Marketplace** (`/skills`).
2. Search for "Figma" or filter by "Design & Creative Arts".
3. Show a skill listing with session duration, level, and credit cost.
4. Click **Book Swap** to show the booking proposal screen where credits and times are computed automatically.

### Step 4: Live Video Room & Session Completion (30 seconds)
1. Go to **My Sessions** (`/bookings`).
2. Open the scheduled session and click **Enter Video Room** (`/video/skillswap-demo-session-102`).
3. Show the embedded **Jitsi Meet** interface, session timer, and live notepad.
4. Click **Finish & Transfer Credits** to trigger the server-side escrow release.
5. Demonstrate that the tutor earned the credits and reviews are now unlocked!

### Step 5: AI Learning Suite & Admin Panel (30 seconds)
1. Open **AI Learning Suite > Learning Roadmaps** (`/ai/roadmap`). Show the 4-week structured curriculum with interactive milestone checkboxes.
2. Open **AI Learning Suite > Skill Quizzes** (`/ai/quiz`). Show the interactive 5-question test with instant scoring and badge certification.
3. Open **Admin Panel** (`admin@skillswap.com` / `AdminPass123!`) to show system metrics, user moderation, dispute resolution, and audit logs.

---

## 🎓 College Viva & Oral Examination Q&A

### Q1: What is the core problem SkillSwap solves?
**Answer:** Traditional skill learning requires monetary payment, creating financial barriers. Direct barter systems (1-to-1) fail due to the "coincidence of wants" problem (User A wants what B teaches, but B doesn't want what A teaches). SkillSwap introduces a time-based currency ledger where credits earned teaching one person can be spent learning from anyone else in the community.

### Q2: Why did you choose SQLite as the primary database?
**Answer:** SQLite is lightweight, serverless, self-contained, and requires zero external daemon processes or network socket configuration. It guarantees zero-configuration portability for evaluations while remaining ACID-compliant. Our SQLAlchemy models use standard constraints and foreign key PRAGMA enforcement so the application can migrate to PostgreSQL or MySQL simply by updating `DATABASE_URL`.

### Q3: How do you prevent fraud and double-spending of credits?
**Answer:** We implemented a two-phase escrow reservation system inside `wallet_service.py`. When a session is scheduled, the learner's credits are locked into a `held` state in the `credit_reservations` table and deducted from spendable balance. The tutor only receives the funds after session completion confirmation. If a dispute arises, platform admin can review and arbitrate funds.

### Q4: How does the AI smart matching work?
**Answer:** The matchmaker computes a normalized fit score (0-100%) based on five key factors:
1. Exact or partial skill title matching against user's wanted learning goals (35%).
2. Category alignment (15%).
3. Teacher rating and completed session history (15%).
4. Direct reciprocal swap bonus (if the tutor wants what the student teaches) (15%).
5. Level fit (Beginner/Intermediate/Advanced) (20%).
The system also generates a transparent, human-readable explanation string explaining why the match was recommended.

### Q5: How do the AI features work if there is no internet or no OpenAI API key?
**Answer:** SkillSwap uses a decoupled provider architecture. While it supports external providers (OpenAI, Groq, Ollama), it contains a high-quality built-in domain generation engine. If external API calls fail or no API key is provided, the system dynamically crafts complete, customized 4-week roadmaps, 5-question multiple choice quizzes, and chatbot responses without crashing or throwing errors.

### Q6: How is video calling implemented?
**Answer:** We embed the open-source Jitsi Meet External API directly in the browser. Each booking generates a cryptographically secure, unique `room_id` (`secrets.token_urlsafe(16)`). Access is restricted to session participants and platform admins, with live timers and session notepads synchronized in local storage.

### Q7: What security measures did you implement?
**Answer:**
- CSRF Protection on all POST/PUT/DELETE forms via Flask-WTF.
- Password hashing using PBKDF2/SHA256 via Werkzeug (`generate_password_hash`).
- Session hijacking prevention with `HttpOnly` and `SameSite=Lax` cookies.
- Rate limiting using Flask-Limiter.
- Input validation and sanitization using WTForms.
- Role-Based Access Control (`@admin_required` and `@login_required` decorators).

---

## 🧪 Automated Testing

Run the test suite:
```powershell
.\.venv\Scripts\python.exe -m pytest tests
```
10 automated unit and integration tests covering authentication, wallet math, booking escrow lifecycle, reviews, AI matching, roadmap generation, quiz scoring, and route rendering.
