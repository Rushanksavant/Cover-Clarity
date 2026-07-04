import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"


import cognee
import httpx
import reportlab
from dotenv import load_dotenv

load_dotenv()

COGNEE_URL = os.environ["COGNEE_SERVICE_URL"]
COGNEE_API_KEY = os.environ["COGNEE_API_KEY"]
DATASET = os.environ.get("COGNEE_DATASET", "dental_insurance_kb")

_initialized = False


async def init_cognee():
    global _initialized
    if not _initialized:
        await cognee.serve()
        _initialized = True


# ── Session validation ──────────────────────────────────────────────────────

async def is_session_valid(session_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{COGNEE_URL}/api/v1/sessions/{session_id}",
            headers={"X-Api-Key": COGNEE_API_KEY},
        )
        return resp.status_code == 200


# ── Chat ────────────────────────────────────────────────────────────────────

async def chat(session_id: str, query: str, medical_history: dict = None) -> dict:
    await init_cognee()

    # Inject medical history as context prefix
    if medical_history:
        patient_ctx = f"""
Patient's medical context:
- Age: {medical_history.get('age', 'unknown')}
- Chronic Conditions: {', '.join(c['condition_name'] for c in medical_history.get('chronic_conditions', [])) or 'None'}
- Current Medications: {', '.join(m['name'] for m in medical_history.get('current_medications', [])) or 'None'}
- Allergies: {', '.join(medical_history.get('allergies', [])) or 'None'}
- Past Dental Procedures: {', '.join(medical_history.get('past_dental_procedures', [])) or 'None'}
"""
    else:
        patient_ctx = ""

    instructive_system_prompt=f"""You are a dental insurance assistant. Your job is to answer the patient's specific question using ONLY the knowledge base provided.

Rules:
- Be concise and direct.
- If question is not related to dental insurance related or dental treatment/medication claim, refuse to comment.
- Answer for THIS specific patient, not generically.
- If the knowledge base has a specific limit or restriction, state it plainly.
- Do not explain what documentation is needed unless the patient asked or context states.
- Do not add "bottom line" summaries or generic advice.
- If the answer is not in the knowledge base, say so in one sentence.

{patient_ctx}

Answer the patient's question as if you are speaking directly to them."""

    results = await cognee.recall(
        query_text=query,
        session_id=session_id,
        datasets=[DATASET],
        system_prompt=instructive_system_prompt
    )

    answer = "No relevant information found in the knowledge base."
    if results:
        # Extract .text field if it's a cognee result object, else fallback to str
        texts = []
        for r in (results if isinstance(results, list) else [results]):
            if hasattr(r, 'text'):
                texts.append(r.text)
            elif isinstance(r, dict):
                texts.append(r.get('text') or r.get('answer') or str(r))
            else:
                texts.append(str(r))
        answer = "\n\n".join(t for t in texts if t)

    history = await get_chat_history(session_id, last_n=1)
    trace_ids = []
    if history:
        trace_ids = history[-1].get("used_session_context_ids") or []

    return {"answer": answer, "trace_ids": trace_ids}


# ── History ─────────────────────────────────────────────────────────────────

async def get_chat_history(session_id: str, last_n: int = None) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{COGNEE_URL}/api/v1/sessions/{session_id}",
            headers={"X-Api-Key": COGNEE_API_KEY},
        )
        if resp.status_code != 200:
            return []
        data = resp.json()

    qas = data.get("qas", [])
    if last_n:
        qas = qas[-last_n:]

    return [
        {
            "qa_id": e["qa_id"],
            "time": e["time"],
            "question": e["question"],
            "answer": e["answer"],
            "used_session_context_ids": e.get("used_session_context_ids") or [],
        }
        for e in qas
    ]


# ── Export ───────────────────────────────────────────────────────────────────

def history_to_markdown(session_id: str, history: list[dict]) -> str:
    lines = [f"# Chat History — Session `{session_id}`\n"]
    for i, turn in enumerate(history, 1):
        lines.append(f"## Turn {i} — {turn['time']}")
        lines.append(f"**Q:** {turn['question']}\n")
        lines.append(f"**A:** {turn['answer']}\n")
    return "\n".join(lines)


# ── PDF logo — rendered once at startup ──────────────────────────────────────
_LOGO_PNG_PATH: str | None = None

_LOGO_PNG_PATH: str | None = None

def _get_logo_png() -> str:
    global _LOGO_PNG_PATH
    if _LOGO_PNG_PATH is None:
        from pathlib import Path
        _LOGO_PNG_PATH = str(Path(__file__).parent / "assets" / "logo_pdf.png")
    return _LOGO_PNG_PATH


def history_to_pdf_bytes(session_id: str, history: list[dict], username: str = "") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
    from datetime import date
    import io, re

    W, H = A4
    TEAL        = colors.HexColor('#30A2AE')
    LIGHT_TEAL  = colors.HexColor('#A1E2EB')
    DARK        = colors.HexColor('#1a1a2e')
    GREY        = colors.HexColor('#64748b')
    LIGHT_GREY  = colors.HexColor('#f1f5f9')
    BORDER_GREY = colors.HexColor('#e2e8f0')

    HEADER_H = 18*mm
    LOGO_H   = 10*mm
    LOGO_W   = LOGO_H * (839 / 679)   # matches SVG-render aspect ratio
    generated = date.today().isoformat()

    def clean(text: str) -> str:
        text = text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
        text = text.replace('\u202f',' ').replace('\u00a0',' ').replace('\u2019',"'")
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = text.replace('&','&amp;')
        text = text.replace('<b>','\x00B').replace('</b>','\x00E')
        text = text.replace('<','&lt;').replace('>','&gt;')
        text = text.replace('\x00B','<b>').replace('\x00E','</b>')
        text = text.replace('\n','<br/>')
        return text

    def make_header(canvas, doc):
        canvas.saveState()

        canvas.setFillColor(TEAL)
        canvas.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

        logo_y = H - HEADER_H + (HEADER_H - LOGO_H) / 2
        canvas.drawImage(_get_logo_png(), 12*mm, logo_y,
                         width=LOGO_W, height=LOGO_H,
                         preserveAspectRatio=False, mask='auto')

        text_x = 12*mm + LOGO_W + 3*mm
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 11)
        canvas.drawString(text_x, H - 9*mm, 'Claim-Clarity')
        canvas.setFont('Helvetica', 6.5)
        canvas.drawString(text_x, H - 14.5*mm,
                          'Where insurance payers verify claims from policy knowledge graphs')

        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(W - 14*mm, H - 11*mm, f'Page {doc.page}')

        canvas.setStrokeColor(LIGHT_TEAL)
        canvas.setLineWidth(0.5)
        canvas.line(0, H - HEADER_H - 0.5*mm, W, H - HEADER_H - 0.5*mm)

        canvas.setStrokeColor(BORDER_GREY)
        canvas.setLineWidth(0.5)
        canvas.line(14*mm, 14*mm, W - 14*mm, 14*mm)
        canvas.setFillColor(GREY)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(14*mm, 9*mm,
                          f'Session: {session_id}   ·   Generated: {generated}   ·   User: {username}')
        canvas.drawRightString(W - 14*mm, 9*mm, 'CONFIDENTIAL — FOR POLICYHOLDER USE ONLY')

        canvas.restoreState()

    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=14*mm, rightMargin=14*mm,
                          topMargin=HEADER_H + 10*mm, bottomMargin=22*mm)
    frame = Frame(14*mm, 22*mm, W - 28*mm, H - HEADER_H - 32*mm, id='main')
    doc.addPageTemplates([PageTemplate(id='main', frames=frame, onPage=make_header)])

    styles = getSampleStyleSheet()
    def S(name, **kw): return ParagraphStyle(name, parent=styles['Normal'], **kw)

    title_s = S('title', fontName='Helvetica-Bold', fontSize=16, textColor=DARK, spaceAfter=2)
    sub_s   = S('sub',   fontName='Helvetica',      fontSize=9,  textColor=GREY, spaceAfter=10)
    turn_s  = S('turn',  fontName='Helvetica-Bold', fontSize=8,  textColor=colors.white)
    ql_s    = S('ql',    fontName='Helvetica-Bold', fontSize=9,  textColor=TEAL, spaceBefore=4, spaceAfter=2)
    q_s     = S('q',     fontName='Helvetica-Bold', fontSize=10, textColor=DARK, leading=15, spaceAfter=6)
    al_s    = S('al',    fontName='Helvetica-Bold', fontSize=9,  textColor=GREY, spaceAfter=2)
    a_s     = S('a',     fontName='Helvetica',      fontSize=10, textColor=DARK, leading=16, spaceAfter=4)
    tp_s    = S('tp',    fontSize=8, textColor=GREY, leading=14)

    story = []
    story.append(Paragraph('Insurance Claim Chat Report', title_s))
    story.append(Paragraph(f'Session ID: {session_id}   ·   Date: {generated}   ·   User: {username}', sub_s))
    story.append(HRFlowable(width='100%', thickness=1, color=TEAL, spaceAfter=10))
    story.append(Spacer(1, 3*mm))

    for i, turn in enumerate(history, 1):
        time_str = turn['time'][:19].replace('T', ' at ')
        badge = Table([[Paragraph(f'  Turn {i}  ', turn_s)]], colWidths=[20*mm])
        badge.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),TEAL),
            ('TOPPADDING',(0,0),(-1,-1),3),
            ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('LEFTPADDING',(0,0),(-1,-1),4),
        ]))
        hrow = Table([[badge, Paragraph(time_str, tp_s)]], colWidths=[22*mm, None])
        hrow.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),0),
            ('RIGHTPADDING',(0,0),(-1,-1),0),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        story.append(hrow)
        story.append(Paragraph('QUESTION', ql_s))
        story.append(Paragraph(clean(turn['question']), q_s))
        a_block = Table(
            [[Paragraph('ANSWER', al_s)], [Paragraph(clean(turn['answer']), a_s)]],
            colWidths=[W - 28*mm]
        )
        a_block.setStyle(TableStyle([
            ('LEFTPADDING',(0,0),(-1,-1),8),
            ('RIGHTPADDING',(0,0),(-1,-1),4),
            ('TOPPADDING',(0,0),(-1,-1),2),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LINEBEFORE',(0,0),(0,-1),2,LIGHT_TEAL),
            ('BACKGROUND',(0,0),(-1,-1),LIGHT_GREY),
        ]))
        story.append(a_block)
        story.append(Spacer(1, 6*mm))
        if i < len(history):
            story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER_GREY, spaceAfter=6))

    doc.build(story)
    return buf.getvalue()