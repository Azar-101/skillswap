import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib import colors

def build_presentation_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#4F46E5")
    dark_color = colors.HexColor("#0F172A")
    success_color = colors.HexColor("#059669")
    accent_color = colors.HexColor("#D97706")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "PresTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "PresSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "PresH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=dark_color,
        spaceBefore=12,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        "PresH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "PresBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "PresBullet",
        parent=body_style,
        leftIndent=14,
        spaceAfter=3,
    )

    script_box_style = ParagraphStyle(
        "ScriptBox",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
    )

    code_style = ParagraphStyle(
        "PresCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("SkillSwap — College Presentation & Viva Defense Guide", title_style))
    story.append(Paragraph("Slide-by-Slide Speaking Script • Technology Stack Deep Dive • AI Engine Explanation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=10))

    # SECTION 1: Elevator Pitch
    story.append(Paragraph("1. The 30-Second Elevator Pitch (Start Your Presentation with This!)", h1_style))
    story.append(Paragraph(
        "<i>\"Good morning Respected Evaluators and Professors. Today I am presenting <b>SkillSwap</b>, an AI-powered, "
        "time-based peer learning and skill exchange platform. Traditional learning platforms demand high subscription fees, "
        "while direct barter systems fail because two people rarely need exactly what each other teaches. SkillSwap introduces "
        "a zero-cash, time-banked credit economy where 1 hour of teaching equals 1 credit. Credits earned teaching one person "
        "can be spent learning from anyone else in the community, backed by an automated credit escrow ledger and an intelligent AI learning suite.\"</i>",
        script_box_style
    ))
    story.append(Spacer(1, 8))

    # SECTION 2: Tech Stack Used
    story.append(Paragraph("2. Technologies Used & Why You Chose Them (Technical Justification)", h1_style))
    
    tech_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology Used</b>", body_style), Paragraph("<b>Why It Was Chosen (What to Tell Evaluators)</b>", body_style)],
        [
            Paragraph("<b>Backend</b>", body_style),
            Paragraph("Python 3.12 + Flask", body_style),
            Paragraph("Lightweight, micro-framework architecture with zero unnecessary bloat. Modular Blueprints ensure clean separation of concerns (Auth, Skills, Bookings, Wallet, AI).", body_style)
        ],
        [
            Paragraph("<b>Database</b>", body_style),
            Paragraph("SQLite + SQLAlchemy ORM", body_style),
            Paragraph("Zero-configuration, self-contained, serverless ACID-compliant database. SQLAlchemy ORM guarantees easy migration to MySQL/PostgreSQL by simply updating the connection string.", body_style)
        ],
        [
            Paragraph("<b>Security</b>", body_style),
            Paragraph("Flask-Login, Flask-WTF, Werkzeug", body_style),
            Paragraph("CSRF protection tokens on all POST forms, PBKDF2/SHA-256 password hashing, session cookie hardening (HttpOnly, SameSite=Lax), and role-based access control.", body_style)
        ],
        [
            Paragraph("<b>Video Calling</b>", body_style),
            Paragraph("Jitsi Meet External API", body_style),
            Paragraph("Open-source WebRTC video conferencing embedded directly in the browser. Zero client downloads required; generates cryptographically secure room IDs per session.", body_style)
        ],
        [
            Paragraph("<b>Frontend</b>", body_style),
            Paragraph("Bootstrap 5.3 + Custom CSS", body_style),
            Paragraph("Responsive modern UI with glassmorphism touches, badge indicators, live countdown timer, and accessible interactive milestone trackers.", body_style)
        ],
        [
            Paragraph("<b>DevOps</b>", body_style),
            Paragraph("Docker + Docker Compose", body_style),
            Paragraph("Containerized deployment ensuring environment reproducibility across macOS, Linux, and Windows with automated health checks.", body_style)
        ],
    ]
    t_tech = Table(tech_data, colWidths=[90, 130, 320])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2FF")),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # SECTION 3: The AI Engine
    story.append(Paragraph("3. How the AI Components Work (Detailed Breakdown)", h1_style))
    story.append(Paragraph(
        "SkillSwap employs a <b>Decoupled Hybrid AI Provider Architecture</b>. It features a built-in domain intelligence engine "
        "that functions 100% offline (guaranteeing zero exam-day API failures) while supporting optional cloud LLMs (Groq, OpenAI, Ollama).", body_style
    ))

    ai_features = [
        ("A. AI Smart Matchmaker (/ai/matching)",
         "<b>Algorithm Formula:</b> Score = 0.35*(Skill Name Match) + 0.15*(Category Alignment) + 0.15*(Teacher Rating) + 0.15*(Reciprocal Bonus) + 0.20*(Skill Level Compatibility).<br/>"
         "• <b>What it does:</b> It solves the 'coincidence of wants' problem. If User A offers Python and wants Figma, and User B offers Figma and wants Python, the engine flags a <b>Reciprocal Swap Bonus</b> and explains why the match is optimal in plain English."),
        ("B. AI 4-Week Learning Roadmap Generator (/ai/roadmap)",
         "• <b>What it does:</b> Students input any skill or programming language. The AI acts as a curriculum designer, outputting a structured JSON schema divided into 4 weekly themes with goals, granular tasks, and practical projects.<br/>"
         "• <b>Interactive Progress:</b> Each milestone has a real-time checkbox stored in the database, rendering dynamic percentage progress bars."),
        ("C. AI Skill Verification Quizzes & Badges (/ai/quiz)",
         "• <b>What it does:</b> Evaluates competence before teaching or verifies learning after a session.<br/>"
         "• <b>Security Architecture:</b> Correct answer indices and explanations are <b>stored server-side only</b> and never sent to the client browser until after submission, preventing inspection tampering. Passing (≥60%) awards a verified skill badge."),
        ("D. SwapBot Conversational Assistant (/ai/assistant)",
         "• <b>What it does:</b> An interactive learning buddy providing 24/7 coaching on interview rehearsal, peer teaching agendas, and platform credit questions."),
    ]
    for heading, desc in ai_features:
        story.append(Paragraph(heading, h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 8))

    # SECTION 4: Slide-by-Slide Speaking Script
    story.append(Paragraph("4. Slide-by-Slide Presentation Speaking Script", h1_style))
    story.append(Paragraph("Use these exact talking points during your presentation slides:", body_style))

    slides = [
        ("Slide 1: Title & Problem Statement",
         "\"Good morning everyone. Peer learning is powerful, but two major obstacles prevent it: cost barriers on commercial platforms and the 'coincidence of wants' in barter. If I want to learn graphic design and know Python, finding someone who wants the exact reverse trade is nearly impossible. SkillSwap solves this with a time-banked ledger.\""),
        ("Slide 2: Time-Based Credit Economics & Escrow",
         "\"Our platform rules are simple: 1 hour of teaching equals 1 credit; 30 minutes equals 0.5 credits. To protect users against fraud, we built a Two-Phase Escrow System. When a student requests a session, credits are checked. When the tutor accepts, credits move into 'Held Escrow'. Only when both parties complete the video call are credits released to the tutor. If cancelled, funds return automatically.\""),
        ("Slide 3: Architecture & Technology Stack",
         "\"We implemented a clean layered architecture using Python 3.12 and Flask. Thin routes handle HTTP requests, while fat services (wallet_service, booking_service, matching_service) hold business rules and database transactions. We chose SQLite for portable, zero-configuration persistence, styled the frontend with responsive Bootstrap 5.3, and integrated Jitsi Meet for WebRTC video calling.\""),
        ("Slide 4: AI Learning Suite Demonstration",
         "\"Next is our AI Learning Suite. Our AI Matchmaker computes compatibility scores and highlights reciprocal swap potential. Our AI Roadmap Generator crafts 4-week step-by-step curricula with interactive progress tracking, and our AI Quiz Assessment generates 5-question tests with server-side answer verification. Best of all, our hybrid architecture ensures these AI features run 100% reliably even offline without API failure risk.\""),
        ("Slide 5: Live Demonstration & Results",
         "\"Now let's switch to the live demo. We can see our pre-seeded accounts: Alex teaching Python, Sarah teaching Figma, and Marcus teaching Excel. We see credit balances, book a session with escrow lock, join the embedded video room with timer, and complete the swap. Finally, we show the Admin Dashboard mediating disputes.\"",),
    ]

    for s_title, s_script in slides:
        story.append(Paragraph(f"<b>{s_title}</b>", h2_style))
        story.append(Paragraph(s_script, script_box_style))

    story.append(Spacer(1, 10))

    # SECTION 5: Top 7 Viva Questions & Bulletproof Answers
    story.append(Paragraph("5. Top 7 Evaluator Viva Questions & How to Answer", h1_style))

    viva_qas = [
        ("Q1: What happens if a teacher doesn't show up after accepting a booking?",
         "<b>Answer:</b> The credits are not lost! They are held in the <code>credit_reservations</code> escrow table. The learner can cancel before start or open a dispute. The admin reviews the dispute in the Admin Panel and clicks 'Refund to Learner', which immediately returns the reserved credits."),
        ("Q2: Why did you not use real money payment gateways like Stripe or Razorpay?",
         "<b>Answer:</b> That is the fundamental philosophical premise of SkillSwap. We wanted to eliminate financial disparity and create an equitable learning community. Time is our universal currency, making education accessible to students regardless of financial background."),
        ("Q3: How do you prevent double-spending of credits?",
         "<b>Answer:</b> In <code>wallet_service.py</code>, we use transactional credit reservation. When a booking is accepted, the learner's <code>available_balance</code> is decremented and <code>reserved_balance</code> is incremented simultaneously. All balance modifications require sufficient available funds and write idempotent audit transaction logs."),
        ("Q4: Can the platform run without an active internet connection?",
         "<b>Answer:</b> Yes! Our AI engine has a built-in domain fallback generator. If external cloud APIs (Groq/OpenAI) are unavailable or internet is disconnected, the system automatically switches to the built-in generator, delivering roadmaps and quizzes without throwing errors."),
        ("Q5: How is video security maintained?",
         "<b>Answer:</b> We generate unique, cryptographically random room IDs using <code>secrets.token_urlsafe(16)</code>. Our video route verifies that only the booking's learner, teacher, or an admin can access the room."),
        ("Q6: How does the AI matchmaker calculate reciprocal swap fit?",
         "<b>Answer:</b> It checks if the teacher's wanted learning skills overlap with skills the current user offers to teach. If a cross-match is detected, it grants a 15% reciprocal bonus and generates an explanation highlighting that both users can teach each other."),
        ("Q7: How did you test your application?",
         "<b>Answer:</b> We wrote an automated Pytest suite (<code>tests/test_mvp.py</code>) with 11 automated test cases covering authentication, escrow lifecycle, credit math, AI matching, roadmap generation, quiz scoring, and route status codes. All 11 tests pass with 100% success."),
    ]

    for q, a in viva_qas:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
    story.append(Paragraph("<i>SkillSwap College Presentation Guide • Created for Major Project Viva Defense</i>", subtitle_style))

    doc.build(story)
    print(f"Presentation PDF built successfully: {filename}")

if __name__ == "__main__":
    out1 = "SkillSwap_Presentation_and_Viva_Defense_Guide.pdf"
    out2 = os.path.join("..", "SkillSwap_Presentation_and_Viva_Defense_Guide.pdf")
    build_presentation_pdf(out1)
    try:
        build_presentation_pdf(out2)
    except Exception as e:
        print("Note on root copy:", e)
