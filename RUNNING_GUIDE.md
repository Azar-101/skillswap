# SkillSwap — Complete Running Guide

Welcome to **SkillSwap** — AI-Powered Time-Based Skill Exchange and Learning Platform.

---

## ⚡ 1. Quick Start (Run in 30 Seconds)

Open PowerShell or Command Prompt in the `skillswap` directory:

```powershell
# 1. Navigate to the skillswap project directory
cd skillswap

# 2. Activate the virtual environment
.\.venv\Scripts\activate

# 3. Start the application
python run.py
```

Now open your web browser at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 2. Ready-to-Use Demo Accounts

The application automatically seeds realistic demo data on first startup. You can log in immediately with any of these pre-configured accounts:

| User Role | Email | Password | What You Can Demo |
|---|---|---|---|
| **Admin** | `admin@skillswap.com` | `AdminPass123!` | System metrics, dispute resolution, user suspension, re-seeding data |
| **Teacher (Python)** | `alex@skillswap.com` | `UserPass123!` | Python mentor, upcoming Figma session, 4.0 credits balance, reviews |
| **Teacher (UI/UX)** | `sarah@skillswap.com` | `UserPass123!` | Figma expert, scheduled teaching session with Alex, rating 5.0★ |
| **Learner (Excel)** | `marcus@skillswap.com` | `UserPass123!` | Financial analyst, completed session history, reviews |

---

## 💰 3. Credit Exchange Rules

SkillSwap uses a **time-based currency ledger**:

- **1 Hour Teaching = 1.0 Credit**
- **30 Minutes Teaching = 0.5 Credits**
- **90 Minutes Teaching = 1.5 Credits**
- **120 Minutes Teaching = 2.0 Credits**

### Escrow & Security Workflow
1. **Request:** Learner requests a session. Credits are checked, not yet locked.
2. **Acceptance:** Teacher accepts. Credits are transferred into **Escrow Reservation** (`held`).
3. **Session:** Participants join the embedded Jitsi Meet video room.
4. **Completion:** Either party clicks **"Confirm Session Completed"**. Escrow credits are transferred to the teacher's wallet!
5. **Review:** 1-5 star reviews are unlocked.

---

## 🤖 4. AI Learning Features (100% Offline Compatible)

SkillSwap includes a **hybrid AI architecture**:
- **Offline Built-in Engine**: Works with **zero API keys** and zero cost. It generates realistic 4-week learning roadmaps, 5-question multiple choice quizzes, reciprocal peer matching, and SwapBot conversational assistance.
- **External Cloud AI (Optional)**: If you provide an `OPENAI_API_KEY` or `GROQ_API_KEY` in `.env` or in **AI Settings**, the platform seamlessly queries cloud models.

---

## 🧪 5. Running the Test Suite

Run all automated test cases:

```powershell
cd skillswap
.\.venv\Scripts\python.exe -m pytest tests
```

Expected output:
```
======================= 10 passed in 2.5s =======================
```

---

## 🛠️ 6. Useful CLI Commands

```powershell
# Re-seed the database with fresh demo data
flask --app run.py seed-db

# Create an administrator account from command line
flask --app run.py create-admin
```
