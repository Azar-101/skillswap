import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib import colors

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#4F46E5")
    dark_color = colors.HexColor("#0F172A")
    success_color = colors.HexColor("#059669")
    card_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=dark_color,
        spaceBefore=14,
        spaceAfter=8,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=body_style,
        leftIndent=15,
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # Title & Header
    story.append(Paragraph("SkillSwap — Complete Project Flow & User Guide", title_style))
    story.append(Paragraph("AI-Powered Time-Based Skill Exchange and Learning Platform | College Major Project", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=14))

    # 1. Concept & Time Currency
    story.append(Paragraph("1. Project Concept & Time-Based Economics", h1_style))
    story.append(Paragraph(
        "SkillSwap removes financial barriers to learning by using <b>Time</b> as a universal, community currency. "
        "Members earn credits by teaching what they know and spend them learning from anyone else.", body_style
    ))

    # Rules Table
    rules_data = [
        [Paragraph("<b>Duration</b>", body_style), Paragraph("<b>Credit Value</b>", body_style), Paragraph("<b>Typical Session Use-Case</b>", body_style)],
        [Paragraph("30 Minutes", body_style), Paragraph("<b>0.5 Credits</b>", body_style), Paragraph("Quick code review, bug fix, pronunciation drill", body_style)],
        [Paragraph("60 Minutes", body_style), Paragraph("<b>1.0 Credit</b>", body_style), Paragraph("Standard deep-dive lesson, interactive workshop", body_style)],
        [Paragraph("90 Minutes", body_style), Paragraph("<b>1.5 Credits</b>", body_style), Paragraph("System design, architectural walkthrough, portfolio review", body_style)],
        [Paragraph("120 Minutes", body_style), Paragraph("<b>2.0 Credits</b>", body_style), Paragraph("Intensive pair-programming or mock interview module", body_style)],
    ]
    t_rules = Table(rules_data, colWidths=[100, 100, 340])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2FF")),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 10))

    # Tri-Swap Liquidity
    story.append(Paragraph("<b>The Tri-Swap Liquidity Model:</b>", h2_style))
    story.append(Paragraph("• <b>User A</b> teaches Python to <b>User B</b> (+1.0 Cr earned by User A).", bullet_style))
    story.append(Paragraph("• <b>User B</b> teaches Graphic Design to <b>User C</b> (+1.0 Cr earned by User B).", bullet_style))
    story.append(Paragraph("• <b>User C</b> teaches Excel to <b>User A</b> (+1.0 Cr earned by User C).", bullet_style))
    story.append(Paragraph("<i>No direct 1:1 barter is needed. Real money is never required.</i>", body_style))

    # 2. Step-by-Step User Flow
    story.append(Paragraph("2. End-to-End User Journey Workflow", h1_style))

    steps = [
        ("Step 1: Registration & Welcome Bonus",
         "When a new user signs up at <b>/auth/register</b>, the system auto-initializes a wallet and credits <b>+2.0 Free Welcome Credits</b>. This cold-start grant allows learners to immediately book their first session without waiting to teach."),
        ("Step 2: Listing Skills (Teach & Learn)",
         "Users head to <b>/skills/new</b> to list: (a) <i>Skills Offered to Teach</i> (hourly rate, duration, proficiency level) and (b) <i>Skills Wanted to Learn</i> (learning target level)."),
        ("Step 3: AI Smart Matching",
         "The AI engine (<b>/ai/matching</b>) compares user wanted skills against active community listings, computing a compatibility score (0-100%) based on skill match, level fit, teacher ratings, and reciprocal swap bonuses ('They want to learn what you teach!')."),
        ("Step 4: Marketplace Discovery & Search",
         "Learners can browse the marketplace (<b>/skills</b>) with full-text search, category filter (Programming, Design, Languages, Business, Music, Academics), and level filtering."),
        ("Step 5: Session Booking & Proposal",
         "Learner clicks <b>Book Swap</b> on any teacher's listing, selects an upcoming date/time, picks session length (30 to 120 mins), and adds notes. The system validates that the learner has sufficient available balance."),
        ("Step 6: Teacher Acceptance & Escrow Lock",
         "The teacher receives an in-app notification. When accepted, the required credits are transferred from the learner's available balance to <b>Escrow Reservation (held)</b>. No credits can be double-spent."),
        ("Step 7: Live Video Session (Jitsi Meet)",
         "Both participants enter the dedicated secure video room (<b>/video/&lt;room_id&gt;</b>). The interface embeds Jitsi Meet video/audio, live countdown timer, and a shared session notepad."),
        ("Step 8: Completion & Escrow Transfer",
         "When the swap concludes, clicking <b>'Confirm Session Completed'</b> unlocks the escrow and immediately transfers the credits into the teacher's wallet. Review unlocks for both participants."),
        ("Step 9: Reviews & Rating Update",
         "The learner rates the mentor from 1 to 5 stars and writes feedback at <b>/reviews/new/&lt;id&gt;</b>. The mentor's public profile rating automatically recalculates."),
    ]

    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # 3. AI Learning Suite Workflow
    story.append(Paragraph("3. AI Learning Suite Architecture", h1_style))
    story.append(Paragraph(
        "SkillSwap provides a hybrid AI architecture (built-in offline engine + optional Groq/OpenAI cloud integration) ensuring zero-downtime reliability:", body_style
    ))
    story.append(Paragraph("• <b>Learning Roadmaps (/ai/roadmap):</b> Enter any skill to generate a structured 4-week step-by-step curriculum with weekly themes, tasks, projects, and interactive milestone checkboxes.", bullet_style))
    story.append(Paragraph("• <b>Skill Verification Quizzes (/ai/quiz):</b> Generates 5-question multiple choice tests with server-side answer verification, instant score calculation, detailed explanations, and profile certification badges.", bullet_style))
    story.append(Paragraph("• <b>SwapBot Learning Assistant (/ai/assistant):</b> 24/7 conversational tutor assisting students with interview rehearsal, lesson preparation, and credit explanations.", bullet_style))

    story.append(Spacer(1, 10))

    # 4. Administration & Dispute Flow
    story.append(Paragraph("4. Administration & Dispute Arbitrage", h1_style))
    story.append(Paragraph(
        "Superusers access <b>/admin</b> for system-wide governance:", body_style
    ))
    story.append(Paragraph("• <b>Platform Metrics:</b> Real-time analytics of registered users, active sessions, completed swaps, and total credits in circulation.", bullet_style))
    story.append(Paragraph("• <b>Dispute Mediation (/admin/disputes):</b> If a participant is absent or technical failure occurs, users raise a dispute. Admins inspect the log and click either <i>'Refund to Learner'</i> or <i>'Award to Teacher'</i>, automatically settling escrow.", bullet_style))
    story.append(Paragraph("• <b>Moderation & Seeding:</b> One-click user suspension/reactivation and database re-seeding.", bullet_style))

    story.append(Spacer(1, 10))

    # 5. Quick Reference Demo Accounts
    story.append(Paragraph("5. Pre-Configured Demo Accounts for Testing", h1_style))
    accounts_data = [
        [Paragraph("<b>Role</b>", body_style), Paragraph("<b>Email / Username</b>", body_style), Paragraph("<b>Password</b>", body_style), Paragraph("<b>Features to Showcase</b>", body_style)],
        [Paragraph("Tutor (Python)", body_style), Paragraph("alex@skillswap.com", code_style), Paragraph("UserPass123!", code_style), Paragraph("Python listings, upcoming Figma swap, 4.0 Cr balance", body_style)],
        [Paragraph("Designer (UI)", body_style), Paragraph("sarah@skillswap.com", code_style), Paragraph("UserPass123!", code_style), Paragraph("Figma expert, 5.0★ rating, incoming session request", body_style)],
        [Paragraph("Analyst (Excel)", body_style), Paragraph("marcus@skillswap.com", code_style), Paragraph("UserPass123!", code_style), Paragraph("Advanced Excel tutor, completed swap transaction history", body_style)],
        [Paragraph("Platform Admin", body_style), Paragraph("admin@skillswap.com", code_style), Paragraph("AdminPass123!", code_style), Paragraph("Admin panel, dispute arbitrage, system metrics, re-seed", body_style)],
    ]
    t_acc = Table(accounts_data, colWidths=[95, 140, 95, 210])
    t_acc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2FF")),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_acc)

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=8))
    story.append(Paragraph("<i>SkillSwap MVP • Built with Python 3.12, Flask, SQLite, Bootstrap 5.3 & Jitsi Meet</i>", subtitle_style))

    doc.build(story)
    print(f"PDF built successfully: {filename}")

if __name__ == "__main__":
    out1 = "SkillSwap_Complete_Project_Flow_Guide.pdf"
    out2 = os.path.join("..", "SkillSwap_Complete_Project_Flow_Guide.pdf")
    build_pdf(out1)
    try:
        build_pdf(out2)
    except Exception as e:
        print("Note on root copy:", e)
