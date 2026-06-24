#!/usr/bin/env python3
"""High-level review (diagram-rich) of building an agentic AI workflow & agent harness.

Frames the agent around Karpathy's "LLM as operating system / brain" model:
model weights = CPU, context window = RAM, external store = disk, tools = peripherals,
the harness = the OS/orchestrator. Covers context engineering, skills, .md files,
tools/MCP, subagents, and a reference architecture.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, PageBreak, Flowable, KeepTogether,
)

OUTPUT = "Agentic-AI-Workflow-Guide.pdf"

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
INK     = colors.HexColor("#16213E")
ACCENT  = colors.HexColor("#0F8B8D")   # teal
ACCENT2 = colors.HexColor("#5B3CC4")   # violet
WARM    = colors.HexColor("#E8833A")   # amber
ROSE    = colors.HexColor("#E94560")
GREEN   = colors.HexColor("#2E8B57")
SOFT    = colors.HexColor("#5C5C70")
PANEL   = colors.HexColor("#F2F5FA")
PANEL2  = colors.HexColor("#EEF6F6")
PANEL3  = colors.HexColor("#F4F0FC")
CODE_BG = colors.HexColor("#1B1B2B")
CODE_FG = colors.HexColor("#E6E6F0")
LINE    = colors.HexColor("#D5DBE6")
CONTENT_W = 6.6 * inch

# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="Helvetica-Bold",
                    fontSize=27, leading=31, textColor=INK, spaceAfter=4, alignment=TA_LEFT)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica",
                     fontSize=12.5, leading=17, textColor=SOFT, spaceAfter=2)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=16.5, leading=20, textColor=ACCENT2, spaceBefore=14, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold",
                    fontSize=12.5, leading=16, textColor=INK, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica",
                      fontSize=10.5, leading=15.5, textColor=INK, spaceAfter=6)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=9, leading=12.5, textColor=SOFT)
CAP = ParagraphStyle("CAP", parent=SMALL, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
BULLET = ParagraphStyle("BULLET", parent=BODY, spaceAfter=3, leftIndent=2)
CODE = ParagraphStyle("CODE", parent=ss["Code"], fontName="Courier",
                      fontSize=8.6, leading=12.2, textColor=CODE_FG)
LABEL = ParagraphStyle("LABEL", parent=BODY, fontName="Helvetica-Bold",
                       fontSize=9, leading=12, textColor=ACCENT)
PB = ParagraphStyle("PB", parent=BODY, fontSize=10, leading=14.5, spaceAfter=4)


# ----------------------------------------------------------------------------
# Layout helpers
# ----------------------------------------------------------------------------
def rule(color=LINE, w=0.8, sb=8, sa=8):
    return HRFlowable(width="100%", thickness=w, color=color, spaceBefore=sb, spaceAfter=sa)


def bullets(items, style=BULLET):
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=10, value="•") for t in items],
        bulletType="bullet", bulletColor=ACCENT, bulletFontSize=8,
        leftIndent=12, spaceBefore=2, spaceAfter=6)


def panel(flowables, bg=PANEL, border=LINE, pad=10):
    t = Table([[flowables]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad), ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def code_block(lines):
    paras = [Paragraph((ln.replace("&", "&amp;").replace("<", "&lt;").replace(" ", "&nbsp;")) or "&nbsp;", CODE) for ln in lines]
    t = Table([[p] for p in paras], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -2), 0),
    ]))
    return t


# ============================================================================
# Drawing primitives shared by diagrams
# ============================================================================
def _box(c, x, y, w, h, fill, stroke, label, sublabel=None, lc=colors.white,
         fs=9, r=5, lw=1.2, sub_fs=7, align="center"):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    c.setFillColor(lc)
    c.setFont("Helvetica-Bold", fs)
    cx = x + w / 2.0
    if sublabel:
        c.drawCentredString(cx, y + h / 2.0 + 2, label)
        c.setFont("Helvetica", sub_fs)
        c.drawCentredString(cx, y + h / 2.0 - 9, sublabel)
    else:
        c.drawCentredString(cx, y + h / 2.0 - fs / 2.0 + 1, label)


def _arrow(c, x1, y1, x2, y2, color=INK, lw=1.3, head=5):
    import math
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (math.radians(150), math.radians(-150)):
        c.line(x2, y2, x2 + head * math.cos(ang + da), y2 + head * math.sin(ang + da))


# ----------------------------------------------------------------------------
# DIAGRAM 1 — Karpathy's LLM-as-OS / "brain" schematic
# ----------------------------------------------------------------------------
class BrainOSDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=3.5 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        cx, cy = W / 2.0, H / 2.0
        # central "CPU/brain"
        cw, ch = 2.0 * inch, 0.95 * inch
        _box(c, cx - cw / 2, cy - ch / 2, cw, ch, INK, ACCENT2,
             "LLM  (the model)", "CPU / Kernel  ·  reasoning core", fs=11, sub_fs=7.5, r=8)
        # satellites: (dx, dy, w, h, fill, label, sub)
        sat = [
            (cx - cw / 2 - 1.55 * inch, cy + 0.55 * inch, 1.45 * inch, 0.62 * inch, ACCENT,
             "Context window", "RAM · working memory"),
            (cx + cw / 2 + 0.1 * inch,  cy + 0.55 * inch, 1.45 * inch, 0.62 * inch, WARM,
             "Tools", "peripherals / I-O"),
            (cx - cw / 2 - 1.55 * inch, cy - 1.17 * inch, 1.45 * inch, 0.62 * inch, GREEN,
             "External memory", "disk · files, vector DB"),
            (cx + cw / 2 + 0.1 * inch,  cy - 1.17 * inch, 1.45 * inch, 0.62 * inch, ROSE,
             "Pretrained weights", "ROM · baked-in knowledge"),
        ]
        for x, y, w, h, fill, lab, sub in sat:
            _box(c, x, y, w, h, fill, fill, lab, sub, fs=9, sub_fs=6.8)
            # connect to center
            tx = cx + (cw / 2 if x > cx else -cw / 2)
            ty = cy + (ch / 2 - 0.12 * inch if y > cy else -ch / 2 + 0.12 * inch)
            sx = x + (0 if x > cx else w)
            sy = y + h / 2
            _arrow(c, tx, ty, sx, sy, color=SOFT, lw=1.1, head=4)
            _arrow(c, sx, sy - 6, tx, ty - 6, color=colors.HexColor("#B7C0D0"), lw=0.9, head=3)
        # orchestrator band (the harness/OS loop) at top
        c.setFillColor(PANEL3); c.setStrokeColor(ACCENT2); c.setLineWidth(1)
        c.roundRect(W * 0.18, H - 0.42 * inch, W * 0.64, 0.34 * inch, 5, fill=1, stroke=1)
        c.setFillColor(ACCENT2); c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(W / 2, H - 0.30 * inch, "AGENT HARNESS  —  the OS / orchestration loop that drives it all")


# ----------------------------------------------------------------------------
# DIAGRAM 2 — the agent loop (cycle)
# ----------------------------------------------------------------------------
class AgentLoopDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=2.7 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        cx, cy = W / 2.0, H / 2.0 - 0.05 * inch
        bw, bh = 1.55 * inch, 0.62 * inch
        rx, ry = 2.05 * inch, 0.92 * inch
        nodes = [
            (cx, cy + ry, ACCENT,  "1 · OBSERVE", "assemble context"),
            (cx + rx, cy, ACCENT2, "2 · REASON", "model plans / decides"),
            (cx, cy - ry, WARM,    "3 · ACT", "call a tool / skill"),
            (cx - rx, cy, GREEN,   "4 · RESULT", "observe output"),
        ]
        pts = []
        for x, y, fill, lab, sub in nodes:
            _box(c, x - bw / 2, y - bh / 2, bw, bh, fill, fill, lab, sub, fs=9.5, sub_fs=7)
            pts.append((x, y))
        # curved-ish arrows around the cycle (clockwise)
        order = [0, 1, 2, 3, 0]
        for i in range(4):
            (x1, y1), (x2, y2) = pts[order[i]], pts[order[i + 1]]
            import math
            ang = math.atan2(y2 - y1, x2 - x1)
            ox1 = x1 + (bw / 2 + 4) * math.cos(ang)
            oy1 = y1 + (bh / 2 + 4) * math.sin(ang)
            ox2 = x2 - (bw / 2 + 8) * math.cos(ang)
            oy2 = y2 - (bh / 2 + 8) * math.sin(ang)
            _arrow(c, ox1, oy1, ox2, oy2, color=SOFT, lw=1.4, head=6)
        # center label
        c.setFillColor(SOFT); c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(cx, cy + 3, "repeat until")
        c.drawCentredString(cx, cy - 7, "task is done")


# ----------------------------------------------------------------------------
# DIAGRAM 3 — the harness as concentric layers
# ----------------------------------------------------------------------------
class HarnessLayersDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=3.15 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        cx, cy = W / 2.0, H / 2.0
        layers = [
            (3.15 * inch, 1.55 * inch, colors.HexColor("#FBE9DC"), WARM,  "GUARDRAILS  ·  orchestration loop  ·  stop conditions", 8.2, H * 0.5 + 1.18 * inch),
            (2.55 * inch, 1.25 * inch, colors.HexColor("#E5F3E9"), GREEN, "MEMORY  ·  history, state, retrieval", 8.0, H * 0.5 + 0.86 * inch),
            (1.95 * inch, 0.97 * inch, colors.HexColor("#FCE7EB"), ROSE,  "TOOLS  ·  SKILLS  ·  subagents", 8.0, H * 0.5 + 0.56 * inch),
            (1.38 * inch, 0.72 * inch, colors.HexColor("#E3F1F1"), ACCENT,"CONTEXT  ASSEMBLY", 8.0, H * 0.5 + 0.30 * inch),
        ]
        for w, h, fill, stroke, lab, fs, ly in layers:
            c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1.1)
            c.roundRect(cx - w / 2, cy - h / 2, w, h, 9, fill=1, stroke=1)
            c.setFillColor(stroke); c.setFont("Helvetica-Bold", fs)
            c.drawCentredString(cx, ly, lab)
        # core
        cw, chh = 1.0 * inch, 0.42 * inch
        _box(c, cx - cw / 2, cy - chh / 2, cw, chh, INK, ACCENT2, "LLM", fs=11, r=7)


# ----------------------------------------------------------------------------
# DIAGRAM 4 — context window composition (stacked bar)
# ----------------------------------------------------------------------------
class ContextBarDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=3.0 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        bx, by = 0.2 * inch, 0.25 * inch
        bw, bh = 1.5 * inch, H - 0.55 * inch
        segs = [  # (frac, color, label)
            (0.14, ACCENT2, "System prompt  ·  role, rules, persona"),
            (0.16, ACCENT,  "Instructions  ·  CLAUDE.md / AGENTS.md, project conventions"),
            (0.13, WARM,    "Skills loaded  ·  tool & SKILL.md definitions in play"),
            (0.18, GREEN,   "Retrieved knowledge  ·  RAG chunks, docs, .md files"),
            (0.15, ROSE,    "Tool results  ·  outputs fed back into the loop"),
            (0.12, colors.HexColor("#7A8699"), "Conversation history  ·  prior turns"),
            (0.12, colors.HexColor("#C7D0DD"), "Headroom  ·  room to think + reply"),
        ]
        y = by
        c.setStrokeColor(colors.white)
        for frac, col, lab in segs:
            seg_h = bh * frac
            c.setFillColor(col)
            c.setLineWidth(1)
            c.rect(bx, y, bw, seg_h, fill=1, stroke=1)
            # label to the right
            lx = bx + bw + 0.18 * inch
            ly = y + seg_h / 2
            c.setStrokeColor(col); c.setLineWidth(0.8)
            c.line(bx + bw, ly, lx - 4, ly)
            c.setFillColor(INK); c.setFont("Helvetica-Bold", 8.2)
            head, _, tail = lab.partition("  ·  ")
            c.drawString(lx, ly + (1 if tail else -3), head)
            if tail:
                c.setFont("Helvetica", 7.2); c.setFillColor(SOFT)
                c.drawString(lx, ly - 8, tail)
            c.setStrokeColor(colors.white)
            y += seg_h
        # axis label
        c.saveState()
        c.translate(bx - 7, by + bh / 2)
        c.rotate(90)
        c.setFillColor(SOFT); c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(0, 0, "finite context window  (the agent's RAM)")
        c.restoreState()


# ----------------------------------------------------------------------------
# DIAGRAM 5 — reference architecture (orchestrator + subagents + tools + memory)
# ----------------------------------------------------------------------------
class ArchitectureDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=3.5 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        # user
        _box(c, 0.15 * inch, H - 0.7 * inch, 1.3 * inch, 0.5 * inch, colors.HexColor("#6C7A91"),
             colors.HexColor("#6C7A91"), "USER / TRIGGER", fs=8.5)
        # orchestrator
        ow, oh = 2.4 * inch, 0.7 * inch
        ox, oy = W / 2 - ow / 2, H - 0.95 * inch
        _box(c, ox, oy, ow, oh, ACCENT2, ACCENT2, "ORCHESTRATOR  AGENT",
             "plans · routes · synthesizes", fs=10.5, sub_fs=7)
        _arrow(c, 1.45 * inch, H - 0.45 * inch, ox, oy + oh / 2, color=SOFT)
        # context sources feeding orchestrator (top right)
        _box(c, W - 1.95 * inch, H - 0.62 * inch, 1.8 * inch, 0.46 * inch,
             colors.HexColor("#E3F1F1"), ACCENT, "Context: .md files, system prompt", lc=ACCENT, fs=7.4)
        _arrow(c, W - 1.95 * inch, H - 0.39 * inch, ox + ow, oy + oh * 0.6, color=ACCENT, lw=1)
        # subagents row
        sy = oy - 1.0 * inch
        subs = [("Research\nsubagent", ACCENT), ("Coding\nsubagent", GREEN), ("Review\nsubagent", ROSE)]
        sw = 1.5 * inch
        gap = (W - 3 * sw) / 4.0
        centers = []
        for i, (lab, col) in enumerate(subs):
            x = gap + i * (sw + gap)
            _box(c, x, sy, sw, 0.62 * inch, col, col, lab.replace("\n", " "), "subagent", fs=8.6, sub_fs=6.5)
            cxn = x + sw / 2
            centers.append(cxn)
            _arrow(c, W / 2, oy, cxn, sy + 0.62 * inch, color=SOFT, lw=1)
            _arrow(c, cxn, sy + 0.62 * inch, W / 2 - 0.3 * inch + i * 0.3 * inch, oy,
                   color=colors.HexColor("#B7C0D0"), lw=0.8, head=3)
        # tools + memory row
        ty = sy - 0.95 * inch
        _box(c, gap, ty, 2.05 * inch, 0.6 * inch, WARM, WARM,
             "TOOLS / MCP servers", "code · web · files · APIs", fs=8.8, sub_fs=6.5)
        _box(c, W - gap - 2.05 * inch, ty, 2.05 * inch, 0.6 * inch, colors.HexColor("#3F7CAC"),
             colors.HexColor("#3F7CAC"), "MEMORY STORE", "vector DB · files · state", fs=8.8, sub_fs=6.5)
        for cxn in centers:
            _arrow(c, cxn, sy, gap + 1.0 * inch, ty + 0.6 * inch, color=colors.HexColor("#C7D0DD"), lw=0.8, head=3)
            _arrow(c, cxn, sy, W - gap - 1.0 * inch, ty + 0.6 * inch, color=colors.HexColor("#C7D0DD"), lw=0.8, head=3)


# ----------------------------------------------------------------------------
# DIAGRAM 6 — progressive disclosure of .md / skills
# ----------------------------------------------------------------------------
class ProgressiveDisclosureDiagram(Flowable):
    def __init__(self, w=CONTENT_W, h=2.6 * inch):
        super().__init__(); self.width = w; self.height = h

    def draw(self):
        c = self.canv; W, H = self.width, self.height
        tiers = [
            (colors.HexColor("#16213E"), "TIER 0 — ALWAYS LOADED", "System prompt + CLAUDE.md / AGENTS.md  (small, every turn)"),
            (ACCENT2, "TIER 1 — NAMES ONLY", "Skill names + one-line descriptions  (cheap index)"),
            (ACCENT,  "TIER 2 — ON DEMAND", "Full SKILL.md pulled in when a skill is triggered"),
            (WARM,    "TIER 3 — AS NEEDED", "Linked files, scripts & docs the skill points to"),
        ]
        n = len(tiers)
        gap = 0.12 * inch
        row_h = (H - (n - 1) * gap) / n
        full_w = W - 0.2 * inch
        for i, (col, head, sub) in enumerate(tiers):
            y = H - (i + 1) * row_h - i * gap
            w = full_w * (1 - i * 0.16)   # narrowing -> funnel
            x = (W - w) / 2
            c.setFillColor(col); c.setStrokeColor(col); c.setLineWidth(1)
            c.roundRect(x, y, w, row_h, 5, fill=1, stroke=1)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 8.6)
            c.drawCentredString(W / 2, y + row_h / 2 + 2, head)
            c.setFont("Helvetica", 7.0)
            c.drawCentredString(W / 2, y + row_h / 2 - 8, sub)
            if i < n - 1:
                _arrow(c, W / 2, y, W / 2, y - gap + 1, color=SOFT, lw=1, head=4)
        c.setFillColor(SOFT); c.setFont("Helvetica-Oblique", 7.5)
        c.saveState(); c.translate(W - 0.06 * inch, H / 2); c.rotate(90)
        c.drawCentredString(0, 0, "loaded only when relevant  ↓  keeps context lean")
        c.restoreState()


# ----------------------------------------------------------------------------
# Page furniture
# ----------------------------------------------------------------------------
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setFillColor(ACCENT2)
    canvas.rect(0, h - 0.16 * inch, w, 0.16 * inch, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, h - 0.16 * inch, w * 0.4, 0.16 * inch, fill=1, stroke=0)
    if doc.page > 1:
        canvas.setFont("Helvetica", 8); canvas.setFillColor(SOFT)
        canvas.drawString(0.9 * inch, 0.55 * inch, "Building Agentic AI Workflows — A High-Level Review")
        canvas.drawRightString(w - 0.9 * inch, 0.55 * inch, "Page %d" % doc.page)
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
        canvas.line(0.9 * inch, 0.72 * inch, w - 0.9 * inch, 0.72 * inch)
    canvas.restoreState()


# ============================================================================
# STORY
# ============================================================================
S = []

# ---------- Cover ----------
S.append(Spacer(1, 0.35 * inch))
S.append(Paragraph("A High-Level Review", SUB))
S.append(Paragraph("Building an Agentic&nbsp;AI Workflow", H1))
S.append(Spacer(1, 3))
S.append(Paragraph("How to design the <b>agent harness</b> — giving an agent its context, "
                   "skills, <font face='Courier'>.md</font> files, tools and memory — framed "
                   "around Andrej Karpathy's <b>“LLM&nbsp;as&nbsp;operating&nbsp;system”</b> model.", SUB))
S.append(Spacer(1, 12))
S.append(BrainOSDiagram())
S.append(Paragraph("Fig.&nbsp;1 — Karpathy's mental model: the LLM is the CPU, the context window "
                   "is RAM, tools are peripherals, weights are ROM, and the harness is the OS.", CAP))
S.append(Spacer(1, 8))
S.append(panel([
    Paragraph("THE ONE-SENTENCE VERSION", LABEL),
    Paragraph("An <b>agent</b> is a loop where a language model is given context, decides on an "
              "action, calls a tool, observes the result, and repeats until the task is done. "
              "The <b>harness</b> is everything around the model that makes that loop reliable — "
              "and your real job as a builder is <b>engineering what enters the context window</b>.", PB),
], bg=PANEL2, border=ACCENT))
S.append(Spacer(1, 8))
S.append(Paragraph("Reference review · prepared June 2026 · sources on the final page.", SMALL))
S.append(PageBreak())

# ---------- 1. The mental model ----------
S.append(Paragraph("1 · The mental model: the LLM is a new kind of computer", H2))
S.append(Paragraph(
    "Karpathy's framing is the most useful starting point for builders. Stop thinking of the model "
    "as a chatbot and start thinking of it as the <b>CPU of an emerging operating system</b>. "
    "Everything you build around it maps cleanly onto computer architecture:", BODY))

t = Table([
    [Paragraph("<b>Classical computer</b>", PB), Paragraph("<b>LLM operating system</b>", PB), Paragraph("<b>What it means for your agent</b>", PB)],
    [Paragraph("CPU / kernel", PB), Paragraph("The <b>model</b> (weights running inference)", PB), Paragraph("Does the reasoning. You don't program it — you <i>prompt</i> it.", PB)],
    [Paragraph("RAM", PB), Paragraph("The <b>context window</b>", PB), Paragraph("Finite working memory. What's in it is all the agent can ‘see’ right now.", PB)],
    [Paragraph("ROM / firmware", PB), Paragraph("<b>Pretrained weights</b>", PB), Paragraph("Baked-in knowledge & skills. Static, always present, not directly editable.", PB)],
    [Paragraph("Disk / storage", PB), Paragraph("<b>External memory</b>", PB), Paragraph("Files, vector DBs, history. Vast but must be <i>loaded</i> into context to matter.", PB)],
    [Paragraph("Peripherals / I&nbsp;O", PB), Paragraph("<b>Tools</b>", PB), Paragraph("Code runner, browser, file system, APIs, other agents.", PB)],
    [Paragraph("Operating system", PB), Paragraph("The <b>agent harness</b>", PB), Paragraph("The loop & plumbing that schedules turns, calls tools, manages memory.", PB)],
], colWidths=[1.25 * inch, 1.95 * inch, 3.4 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT2), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
]))
S.append(t)
S.append(Spacer(1, 8))
S.append(panel([
    Paragraph("WHY THIS MATTERS", LABEL),
    Paragraph("The weights are fixed; you can't retrain them per task. Your entire lever over the "
              "system is <b>what you load into RAM</b> — the context window. That single insight is "
              "why “context engineering” is the core discipline of agent building, and why "
              "<font face='Courier'>.md</font> files, skills, and retrieval all exist: they are how "
              "you decide what the CPU gets to see.", PB),
], bg=PANEL3, border=ACCENT2))
S.append(PageBreak())

# ---------- 2. The agent loop ----------
S.append(Paragraph("2 · The agent loop — the heartbeat of every agent", H2))
S.append(Paragraph(
    "Strip away the jargon and every agent is the same four-step cycle. The model never “runs” "
    "continuously; it takes one turn at a time. The harness runs the loop.", BODY))
S.append(AgentLoopDiagram())
S.append(Paragraph("Fig.&nbsp;2 — The observe → reason → act → result cycle, repeated until a stop "
                   "condition is met.", CAP))
S.append(bullets([
    "<b>Observe</b> — the harness assembles the context window: system prompt, instructions, "
    "relevant memory, the latest tool output.",
    "<b>Reason</b> — the model thinks and chooses the next action (often emitting a tool call).",
    "<b>Act</b> — the harness executes that tool/skill in the real world.",
    "<b>Result</b> — the output is captured and fed back in on the next turn.",
]))
S.append(panel([
    Paragraph("DESIGN THE STOP CONDITION DELIBERATELY", LABEL),
    Paragraph("A loop without a clear exit is how agents burn tokens or spiral. Common stops: task "
              "marked complete, max iterations reached, a verifier agent approves, or a human "
              "confirms. Decide this <i>before</i> you ship.", PB),
], bg=PANEL2, border=WARM))
S.append(PageBreak())

# ---------- 3. The harness ----------
S.append(Paragraph("3 · The agent harness — layers around the model", H2))
S.append(Paragraph(
    "The harness is everything that wraps the bare model to make it dependable. Think of it as "
    "concentric layers: closest to the core is the context the model reads; outermost is the "
    "orchestration and safety logic that governs the whole loop.", BODY))
S.append(HarnessLayersDiagram())
S.append(Paragraph("Fig.&nbsp;3 — The harness as layers around the LLM core.", CAP))
S.append(Spacer(1, 2))
S.append(Paragraph("Each layer, briefly", H3))
S.append(bullets([
    "<b>Context assembly</b> — chooses what enters the window each turn (system prompt + "
    "instructions + retrieved knowledge + recent results). The highest-leverage layer.",
    "<b>Tools · skills · subagents</b> — the actions the agent can take and the specialized "
    "capabilities it can pull in on demand.",
    "<b>Memory</b> — what persists across turns and sessions: conversation history, scratchpad "
    "state, and a retrievable long-term store.",
    "<b>Guardrails &amp; orchestration</b> — the loop driver, permission checks, validation of "
    "tool inputs/outputs, stop conditions, and error recovery.",
]))
S.append(PageBreak())

# ---------- 4. Context engineering ----------
S.append(Paragraph("4 · Context engineering — packing the agent's RAM", H2))
S.append(Paragraph(
    "Because the context window is finite, building an agent is largely the craft of deciding "
    "<b>what to load, when, and what to leave out</b>. Everything competes for the same space.", BODY))
S.append(ContextBarDiagram())
S.append(Paragraph("Fig.&nbsp;4 — Typical composition of an agent's context window. Every segment "
                   "trades off against the others and against headroom to reason.", CAP))
S.append(Paragraph("Principles that pay off", H3))
S.append(bullets([
    "<b>Relevance over volume.</b> More context is not better — irrelevant tokens dilute attention "
    "and cost money. Load what this turn needs.",
    "<b>Just-in-time retrieval.</b> Keep big knowledge on ‘disk’ and pull only the relevant "
    "chunks into RAM when required (RAG, file reads, tool results).",
    "<b>Compaction.</b> As history grows, summarize older turns so the window doesn't overflow — "
    "the agent keeps the gist, not every token.",
    "<b>Stable core, dynamic edges.</b> Keep the system prompt and instructions fixed; vary the "
    "retrieved knowledge and tool results per turn.",
]))
S.append(PageBreak())

# ---------- 5. Skills, .md files, progressive disclosure ----------
S.append(Paragraph("5 · Skills &amp; <font face='Courier'>.md</font> files — instructions the agent loads on demand", H2))
S.append(Paragraph(
    "Karpathy's practical advice: <b>write down what the agent needs to know in plain markdown</b> "
    "and load it into context, rather than relying only on runtime retrieval. This is exactly what "
    "modern agent harnesses formalize as <b>instruction files</b> and <b>skills</b>.", BODY))

t2 = Table([
    [Paragraph("<b>Artifact</b>", PB), Paragraph("<b>What it is</b>", PB), Paragraph("<b>When it loads</b>", PB)],
    [Paragraph("<font face='Courier'>CLAUDE.md</font> / <font face='Courier'>AGENTS.md</font>", PB),
     Paragraph("Project-level instructions: conventions, architecture, do/don't.", PB),
     Paragraph("Every turn (small, always-on).", PB)],
    [Paragraph("A <b>skill</b> (<font face='Courier'>SKILL.md</font>)", PB),
     Paragraph("A packaged capability: a description + instructions + optional scripts/files.", PB),
     Paragraph("Pulled in only when its trigger matches the task.", PB)],
    [Paragraph("Reference <font face='Courier'>.md</font> docs", PB),
     Paragraph("Deeper knowledge a skill or task points to.", PB),
     Paragraph("Read on demand, as the agent needs them.", PB)],
    [Paragraph("Tool / MCP defs", PB),
     Paragraph("Schemas for the actions the agent can call.", PB),
     Paragraph("Names always visible; full schema fetched when used.", PB)],
], colWidths=[1.7 * inch, 3.05 * inch, 1.85 * inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
]))
S.append(t2)
S.append(Spacer(1, 8))
S.append(Paragraph("Progressive disclosure: the key to not drowning the context", H3))
S.append(Paragraph(
    "You can't load every skill and document at once — you'd blow the budget. Harnesses solve this "
    "with <b>progressive disclosure</b>: cheap metadata is always present, and the heavy content is "
    "loaded only when it becomes relevant.", BODY))
S.append(ProgressiveDisclosureDiagram())
S.append(Paragraph("Fig.&nbsp;5 — Progressive disclosure: small always-on instructions at the top, "
                   "heavier capability files loaded just-in-time below.", CAP))
S.append(PageBreak())

# ---------- 6. A skill, concretely ----------
S.append(Paragraph("6 · What a skill actually looks like", H2))
S.append(Paragraph(
    "A skill is just a markdown file with a little front-matter. The front-matter is the cheap "
    "index the harness always sees; the body is the instruction set loaded only when triggered. "
    "Keep the description sharp — that is what decides whether the skill fires.", BODY))
S.append(code_block([
    "---",
    "name: pdf-report",
    "description: Generate a branded PDF report from a data summary.",
    "             Use when the user asks for a PDF, export, or report.",
    "---",
    "",
    "# PDF Report Skill",
    "",
    "## When to use",
    "Trigger when the user wants a polished, shareable document.",
    "",
    "## Steps",
    "1. Collect the data summary and the target audience.",
    "2. Run scripts/build_report.py with the summary as input.",
    "3. Review the rendered output before sending.",
    "",
    "## Files",
    "- scripts/build_report.py   <- loaded only when this skill runs",
    "- templates/brand.css",
]))
S.append(Spacer(1, 6))
S.append(panel([
    Paragraph("THE PATTERN, GENERALIZED", LABEL),
    Paragraph("<b>Metadata</b> (name + description) is always cheap and always loaded → the agent "
              "knows the skill <i>exists</i>. The <b>body</b> is loaded on trigger → the agent learns "
              "<i>how</i>. Linked <b>scripts/files</b> load last → the agent acts. Same idea whether "
              "you call them skills, tools, or playbooks.", PB),
], bg=PANEL2, border=ACCENT))
S.append(PageBreak())

# ---------- 7. Reference architecture ----------
S.append(Paragraph("7 · Putting it together — a reference architecture", H2))
S.append(Paragraph(
    "For non-trivial work, a single agent in a loop gives way to an <b>orchestrator</b> that plans "
    "and delegates to focused <b>subagents</b>, each with its own clean context, tools, and a shared "
    "memory store. This keeps any one context window small and each agent's job sharp.", BODY))
S.append(ArchitectureDiagram())
S.append(Paragraph("Fig.&nbsp;6 — An orchestrator routes work to specialized subagents, which share "
                   "tools/MCP servers and a memory store. Context (.md files, system prompt) feeds the "
                   "orchestrator.", CAP))
S.append(bullets([
    "<b>Orchestrator</b> owns the plan and the stop condition; it rarely touches raw tools itself.",
    "<b>Subagents</b> get a narrow brief and a fresh context window — isolation prevents one task's "
    "clutter from polluting another.",
    "<b>Shared tools / MCP</b> expose real-world actions uniformly to every agent.",
    "<b>Memory store</b> is the ‘disk’: durable state and retrievable knowledge across the run.",
]))
S.append(PageBreak())

# ---------- 8. Build checklist ----------
S.append(Paragraph("8 · A practical build sequence", H2))
S.append(ListFlowable([
    ListItem(Paragraph("<b>Define the job &amp; the done-state.</b> One sentence on the goal; an "
                       "explicit, checkable stop condition.", BODY), value=1),
    ListItem(Paragraph("<b>Write the core context.</b> System prompt (role + rules) and a "
                       "<font face='Courier'>CLAUDE.md</font>/<font face='Courier'>AGENTS.md</font> of "
                       "conventions. Keep it tight.", BODY), value=2),
    ListItem(Paragraph("<b>Pick the model</b> for the reasoning core — a current, capable model "
                       "(e.g. the latest Claude) for planning; a smaller/faster one for narrow "
                       "subtasks.", BODY), value=3),
    ListItem(Paragraph("<b>Give it tools.</b> Start with the minimum set of real actions; add MCP "
                       "servers for external systems.", BODY), value=4),
    ListItem(Paragraph("<b>Add skills &amp; <font face='Courier'>.md</font> docs</b> for repeatable "
                       "procedures, using progressive disclosure so they load only when relevant.", BODY), value=5),
    ListItem(Paragraph("<b>Wire memory.</b> Short-term (history + compaction) and, if needed, a "
                       "long-term retrievable store.", BODY), value=6),
    ListItem(Paragraph("<b>Add guardrails.</b> Input/output validation, permissions on risky tools, "
                       "iteration caps, and a verifier where correctness matters.", BODY), value=7),
    ListItem(Paragraph("<b>Split into subagents</b> once one context window gets crowded or jobs "
                       "diverge. Introduce an orchestrator.", BODY), value=8),
    ListItem(Paragraph("<b>Observe &amp; iterate.</b> Log every turn; watch where context is wasted "
                       "or tools misfire, and tighten.", BODY), value=9),
], bulletType="1", leftIndent=16, bulletColor=ACCENT2, spaceBefore=2, spaceAfter=4))

S.append(rule())
S.append(Paragraph("Common pitfalls", H3))
S.append(bullets([
    "<b>Context stuffing.</b> Dumping everything in ‘just in case’ — it dilutes reasoning and "
    "costs tokens. Curate.",
    "<b>No stop condition.</b> Loops that never decide they're done.",
    "<b>Vague skill descriptions.</b> If the trigger text is fuzzy, the right skill never fires.",
    "<b>Tool sprawl.</b> Dozens of overlapping tools confuse selection — fewer, sharper tools win.",
    "<b>Treating weights as memory.</b> The model won't ‘remember’ your project — that's the "
    "harness's job via context and storage.",
]))

S.append(rule())
S.append(Paragraph("One-page recap", H3))
S.append(panel([
    Paragraph(
        "<b>Model</b> = CPU (you prompt it, not program it).&nbsp;&nbsp; <b>Context window</b> = RAM "
        "(your main lever).<br/>"
        "<b>Weights</b> = ROM · <b>external store</b> = disk · <b>tools</b> = peripherals · "
        "<b>harness</b> = the OS loop.<br/>"
        "<b>Agent</b> = observe → reason → act → result, until done.&nbsp;&nbsp; "
        "<b>Context engineering</b> = the core skill.<br/>"
        "<b>Skills &amp; .md files</b> load by progressive disclosure.&nbsp;&nbsp; "
        "<b>Scale</b> = orchestrator + focused subagents + shared tools/memory.", PB),
], bg=PANEL3, border=ACCENT2))

S.append(Spacer(1, 10))
S.append(rule())
S.append(Paragraph("Sources", H3))
S.append(bullets([
    "Andrej Karpathy — “Software Is Changing (Again)” / Software 3.0, Sequoia Ascent 2026.",
    "Karpathy's LLM-as-OS framing: model = CPU, context window = RAM, tools = peripherals "
    "(coverage at mindstudio.ai, aibuilderclub.com, medium).",
    "Karpathy on writing agent knowledge as plain markdown loaded into context (LLM wiki / "
    "knowledge-base discussions).",
    "Practitioner write-ups on context engineering, progressive disclosure, and multi-agent "
    "orchestration.",
], style=SMALL))

# ----------------------------------------------------------------------------
doc = SimpleDocTemplate(
    OUTPUT, pagesize=letter,
    leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    topMargin=0.85 * inch, bottomMargin=0.85 * inch,
    title="Building an Agentic AI Workflow — A High-Level Review",
    author="TradesmanPass",
)
doc.build(S, onFirstPage=header_footer, onLaterPages=header_footer)
print("Wrote", OUTPUT)
