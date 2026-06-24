#!/usr/bin/env python3
"""Generate a high-level PDF guide: placing, editing, prompting and using boxes in Ideogram 4."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, PageBreak, KeepTogether, Flowable,
)

OUTPUT = "Ideogram-4-Boxes-Guide.pdf"

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
INK      = colors.HexColor("#1A1A2E")
ACCENT   = colors.HexColor("#E94560")   # Ideogram-ish warm accent
ACCENT2  = colors.HexColor("#5B3CC4")   # violet
SOFT     = colors.HexColor("#6C6C80")
PANEL    = colors.HexColor("#F4F2FB")
PANEL2   = colors.HexColor("#FDEEF1")
CODE_BG  = colors.HexColor("#1E1E2E")
CODE_FG  = colors.HexColor("#E6E6F0")
LINE     = colors.HexColor("#D9D6EA")

# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
ss = getSampleStyleSheet()

H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="Helvetica-Bold",
                    fontSize=30, leading=34, textColor=INK, spaceAfter=4, alignment=TA_LEFT)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica",
                     fontSize=12.5, leading=17, textColor=SOFT, spaceAfter=2)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=17, leading=21, textColor=ACCENT2, spaceBefore=16, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold",
                    fontSize=12.5, leading=16, textColor=INK, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica",
                      fontSize=10.5, leading=15.5, textColor=INK, spaceAfter=6)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=9, leading=13, textColor=SOFT)
BULLET = ParagraphStyle("BULLET", parent=BODY, spaceAfter=3, leftIndent=2)
CODE = ParagraphStyle("CODE", parent=ss["Code"], fontName="Courier",
                      fontSize=8.6, leading=12.2, textColor=CODE_FG, spaceAfter=0)
LABEL = ParagraphStyle("LABEL", parent=BODY, fontName="Helvetica-Bold",
                       fontSize=9, leading=12, textColor=ACCENT)
PANELBODY = ParagraphStyle("PANELBODY", parent=BODY, fontSize=10, leading=14.5, spaceAfter=4)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def rule(color=LINE, w=0.8, space_b=8, space_a=8):
    return HRFlowable(width="100%", thickness=w, color=color,
                      spaceBefore=space_b, spaceAfter=space_a)


def bullets(items, style=BULLET):
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=10, value="•") for t in items],
        bulletType="bullet", bulletColor=ACCENT, bulletFontSize=8,
        leftIndent=12, spaceBefore=2, spaceAfter=6,
    )


def panel(flowables, bg=PANEL, border=LINE, pad=10):
    t = Table([[flowables]], colWidths=[6.6 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def code_block(lines):
    paras = [Paragraph(ln.replace(" ", "&nbsp;") or "&nbsp;", CODE) for ln in lines]
    t = Table([[p] for p in paras], colWidths=[6.6 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.8, CODE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 0),
    ]))
    return t


# ---- Diagram: the canvas / coordinate grid ----
class CanvasDiagram(Flowable):
    """A simple illustration of the 0-1000 box-coordinate canvas with placed elements."""
    def __init__(self, width=6.6 * inch, height=3.5 * inch):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        W, H = self.width, self.height
        pad = 0.45 * inch
        gx, gy = pad, pad * 0.6
        gw, gh = W - pad * 1.4, H - pad * 1.3

        # canvas frame
        c.setFillColor(colors.HexColor("#FBFAFF"))
        c.setStrokeColor(INK)
        c.setLineWidth(1.4)
        c.roundRect(gx, gy, gw, gh, 6, fill=1, stroke=1)

        # light grid
        c.setStrokeColor(colors.HexColor("#E4E0F2"))
        c.setLineWidth(0.5)
        for i in range(1, 10):
            x = gx + gw * i / 10.0
            c.line(x, gy, x, gy + gh)
            y = gy + gh * i / 10.0
            c.line(gx, y, gx + gw, y)

        def place(fx, fy, fw, fh, col, label):
            bx = gx + gw * fx
            # top-left origin: y grows downward
            by = gy + gh * (1 - fy - fh)
            bw, bh = gw * fw, gh * fh
            c.setStrokeColor(col)
            c.setLineWidth(1.6)
            c.setFillColor(col)
            c.setFillAlpha(0.12)
            c.roundRect(bx, by, bw, bh, 4, fill=1, stroke=1)
            c.setFillAlpha(1)
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(bx + 4, by + bh - 11, label)

        # elements (fx, fy from top-left, fw, fh as fractions)
        place(0.06, 0.06, 0.55, 0.16, ACCENT2, "TITLE  text")
        place(0.06, 0.30, 0.40, 0.55, ACCENT, "SUBJECT")
        place(0.55, 0.45, 0.38, 0.40, colors.HexColor("#1F8A70"), "PRODUCT")
        place(0.55, 0.06, 0.38, 0.16, colors.HexColor("#C77D00"), "LOGO")

        # origin marker
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(gx - 2, gy + gh + 6, "(0,0) origin  —  x →   y ↓")
        c.setFont("Helvetica", 6.5)
        c.setFillColor(SOFT)
        c.drawRightString(gx + gw, gy - 9, "coordinates normalized 0–1000")


# ----------------------------------------------------------------------------
# Page furniture
# ----------------------------------------------------------------------------
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    # top accent bar
    canvas.setFillColor(ACCENT2)
    canvas.rect(0, h - 0.18 * inch, w, 0.18 * inch, fill=1, stroke=0)
    if doc.page > 1:
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(SOFT)
        canvas.drawString(0.9 * inch, 0.55 * inch, "Ideogram 4 — Working with Boxes")
        canvas.drawRightString(w - 0.9 * inch, 0.55 * inch, "Page %d" % doc.page)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(0.9 * inch, 0.72 * inch, w - 0.9 * inch, 0.72 * inch)
    canvas.restoreState()


# ----------------------------------------------------------------------------
# Build story
# ----------------------------------------------------------------------------
story = []

# ---- Cover ----
story.append(Spacer(1, 0.5 * inch))
story.append(Paragraph("A High-Level Guide to", SUB))
story.append(Paragraph("Boxes in Ideogram&nbsp;4", H1))
story.append(Spacer(1, 4))
story.append(Paragraph("How to <b>place</b>, <b>edit</b>, <b>prompt</b>, and <b>use</b> "
                       "bounding boxes for layout-controlled image generation.", SUB))
story.append(Spacer(1, 14))
story.append(CanvasDiagram())
story.append(Spacer(1, 14))
story.append(panel([
    Paragraph("WHAT ARE “BOXES”?", LABEL),
    Paragraph(
        "In Ideogram&nbsp;4, a <b>box</b> (bounding box) is a rectangular region you assign to a "
        "single element — a headline, a subject, a product, a logo, a background fill. Instead of "
        "describing a whole scene in one sentence and hoping the model arranges it well, you "
        "<b>declare a canvas and place each element by coordinate</b>, the way you would drag a "
        "frame in a design editor. Each box is an addressable element with its own position, its "
        "own style, and — for text — its own literal string.", PANELBODY),
], bg=PANEL2, border=ACCENT))
story.append(Spacer(1, 10))
story.append(Paragraph("Reference guide · prepared June 2026 · sources listed on the final page.", SMALL))
story.append(PageBreak())

# ---- 1. Mental model ----
story.append(Paragraph("1 · The mental model", H2))
story.append(Paragraph(
    "Ideogram&nbsp;4 introduces <b>layout control</b> through a structured prompt. The shift is "
    "from <i>describing</i> a picture to <i>composing</i> one. You think like a designer laying "
    "out a poster: a title goes near the top, the product sits in the lower-right, a logo pins to "
    "a corner, a background fills the rest. Every one of those is a box.", BODY))
story.append(bullets([
    "<b>Plain-text prompt</b> — still works. Best for loose, illustrative, or exploratory images "
    "where exact placement doesn't matter.",
    "<b>Structured / JSON prompt</b> — the box-driven mode. Best for posters, ads, UI mockups, "
    "packaging, and anything where text and elements must land in specific spots.",
    "<b>Magic Prompt</b> — a hosted layer that rewrites your plain-text idea into a full "
    "structured caption, so you get box-level layout without writing JSON by hand.",
]))
story.append(panel([
    Paragraph("RULE OF THUMB", LABEL),
    Paragraph("Reach for boxes the moment placement, multiple text blocks, or repeatable layout "
              "matters. For a single hero image with no strict composition, a sentence is enough.",
              PANELBODY),
]))

# ---- 2. The coordinate system ----
story.append(Paragraph("2 · How boxes are addressed (the coordinate system)", H2))
story.append(Paragraph(
    "Every box is positioned on a <b>normalized 0–1000 grid</b>. The origin (0,&nbsp;0) is the "
    "<b>top-left</b> corner; x increases to the right and y increases downward. A box is written "
    "as four numbers:", BODY))
story.append(code_block([
    "bounding_box = [ y_min , x_min , y_max , x_max ]",
    "",
    "# all values 0–1000, origin top-left",
    "# y first, then x  (note the order!)",
    "",
    "[0, 0, 1000, 1000]   -> the entire canvas",
    "[0, 0, 200, 1000]    -> a full-width strip across the top",
    "[450, 550, 850, 950] -> a block in the lower-right quadrant",
]))
story.append(Paragraph(
    "Because coordinates are normalized, the same box description works at any output resolution "
    "(Ideogram&nbsp;4 renders up to native 2K). Boxes may overlap — useful for placing text on "
    "top of a background — and the model treats each as an explicit instruction rather than a hint.",
    SMALL))

story.append(PageBreak())

# ---- 3. Placing boxes ----
story.append(Paragraph("3 · Placing boxes", H2))
story.append(Paragraph("There are two ways to place a box, depending on where you are working.", BODY))

story.append(Paragraph("A · On the Canvas (visual)", H3))
story.append(bullets([
    "Open the <b>Canvas / Editor</b> and start from a blank frame or an existing image.",
    "<b>Drag a rectangle</b> where the element should live — this is your box.",
    "Type the prompt for <i>that region only</i>; the rest of the image stays as context.",
    "Repeat for each element. Move or resize a box by dragging its handles.",
]))
story.append(Paragraph("B · In a structured prompt (precise)", H3))
story.append(Paragraph("Declare the canvas, then add one entry per element with its box and "
                       "description. This is exact, repeatable, and easy to version-control.", BODY))
story.append(code_block([
    "{",
    '  "canvas": { "width": 1024, "height": 1024 },',
    '  "elements": [',
    "    {",
    '      "type": "background",',
    '      "bounding_box": [0, 0, 1000, 1000],',
    '      "desc": "soft studio gradient, warm neutral tones"',
    "    },",
    "    {",
    '      "type": "text",',
    '      "bounding_box": [60, 60, 220, 700],',
    '      "text": "SUMMER SALE",',
    '      "desc": "bold condensed sans-serif, deep navy"',
    "    },",
    "    {",
    '      "type": "object",',
    '      "bounding_box": [450, 550, 880, 950],',
    '      "desc": "a glass bottle of cold-pressed juice, studio lit"',
    "    }",
    "  ]",
    "}",
]))
story.append(Paragraph("Notice each element carries its own <b>bounding_box</b> and <b>desc</b>; "
                       "text elements add a literal <b>text</b> string (covered next).", SMALL))

story.append(PageBreak())

# ---- 4. Prompting inside a box ----
story.append(Paragraph("4 · Prompting a box (text vs. visual description)", H2))
story.append(Paragraph(
    "A box does two jobs at once: it says <i>where</i> something goes and <i>what</i> it is. For "
    "<b>text</b> elements this splits into two distinct fields — and keeping them separate is the "
    "single biggest reason Ideogram&nbsp;4 renders clean, accurate type.", BODY))

t = Table([
    [Paragraph("<b>Field</b>", PANELBODY), Paragraph("<b>What it controls</b>", PANELBODY), Paragraph("<b>Example</b>", PANELBODY)],
    [Paragraph("<font face='Courier'>text</font>", PANELBODY),
     Paragraph("The exact literal characters to render — spelled exactly as they should appear.", PANELBODY),
     Paragraph('"GRAND OPENING"', PANELBODY)],
    [Paragraph("<font face='Courier'>desc</font>", PANELBODY),
     Paragraph("The visual styling — font feel, weight, color, finish. No content here.", PANELBODY),
     Paragraph('"bold serif, gold foil, slight emboss"', PANELBODY)],
], colWidths=[1.0 * inch, 3.3 * inch, 2.3 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT2),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
]))
story.append(t)
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Because each box styles its own text independently, you can mix fonts and treatments in one "
    "image — a heavy display headline, a light subhead, and a small caption strip, each in its own "
    "box. This per-element control is what makes multi-line, multi-font in-image text reliable.", BODY))

story.append(Paragraph("Color and palette", H3))
story.append(Paragraph(
    "Layout pairs with <b>palette conditioning</b>: supply up to <b>16 hex colors</b> to constrain "
    "the whole composition, and set per-element colors inside each box's <b>desc</b> for finer "
    "control. Keep brand colors consistent by reusing the same hex values across boxes.", BODY))
story.append(panel([
    Paragraph("WRITING GOOD BOX DESCRIPTIONS", LABEL),
    Paragraph(
        "• Put the <b>literal words</b> in <font face='Courier'>text</font>, never in "
        "<font face='Courier'>desc</font>.<br/>"
        "• Describe <b>style, not content</b> in <font face='Courier'>desc</font>.<br/>"
        "• Size the box to the content — cramped boxes shrink or clip text.<br/>"
        "• Leave breathing room; don't pack every region edge-to-edge.<br/>"
        "• Reuse exact hex codes across boxes to lock brand color.", PANELBODY),
]))

story.append(PageBreak())

# ---- 5. Editing boxes ----
story.append(Paragraph("5 · Editing boxes", H2))
story.append(Paragraph(
    "Editing is where the two modes diverge most — and it's important to understand the difference "
    "so you pick the right tool.", BODY))

story.append(Paragraph("A · Editing the structured prompt (re-generation)", H3))
story.append(Paragraph(
    "Change a box's coordinates, swap its <font face='Courier'>desc</font>, or rewrite its "
    "<font face='Courier'>text</font>, then run again. This is fast and precise for iterating on "
    "layout. <b>Caveat:</b> editing a JSON field <i>regenerates the entire image from scratch</i>. "
    "Even if you changed one word, the characters, background, and lighting can all shift. Use this "
    "while you are still exploring a layout.", BODY))

story.append(Paragraph("B · Editing the pixels (localized, preserves the rest)", H3))
story.append(Paragraph(
    "When you have an image you like and want a <b>surgical change</b> — swap the text on a sign, "
    "change a product label, replace one object — use the <b>Canvas editor / Magic Fill</b> "
    "(Ideogram&nbsp;3.0-style Edit). You select the region (your box), prompt only that area, and "
    "the rest of the frame is preserved. This is true localized editing, not a re-roll.", BODY))

t2 = Table([
    [Paragraph("<b>You want to…</b>", PANELBODY), Paragraph("<b>Use</b>", PANELBODY)],
    [Paragraph("Explore / restructure the whole layout", PANELBODY), Paragraph("Edit the <b>structured JSON</b> and re-run", PANELBODY)],
    [Paragraph("Reposition or resize an element quickly", PANELBODY), Paragraph("Drag the <b>box on the Canvas</b>", PANELBODY)],
    [Paragraph("Change one thing, keep everything else", PANELBODY), Paragraph("<b>Magic Fill / region edit</b> (Edit mode)", PANELBODY)],
    [Paragraph("Fix a typo in rendered text", PANELBODY), Paragraph("Region-select the text, <b>edit that box only</b>", PANELBODY)],
], colWidths=[3.3 * inch, 3.3 * inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
]))
story.append(Spacer(1, 4))
story.append(t2)

story.append(PageBreak())

# ---- 6. Workflow ----
story.append(Paragraph("6 · A practical end-to-end workflow", H2))
story.append(ListFlowable([
    ListItem(Paragraph("<b>Sketch the layout.</b> Decide the major regions — headline, subject, "
                       "supporting text, logo, background — before touching a prompt.", BODY), value=1),
    ListItem(Paragraph("<b>Declare the canvas</b> and add a full-canvas background box first so the "
                       "scene has a base.", BODY), value=2),
    ListItem(Paragraph("<b>Place each element</b> with its bounding box, working back-to-front "
                       "(background → subjects → text → logo on top).", BODY), value=3),
    ListItem(Paragraph("<b>Prompt each box:</b> literal <font face='Courier'>text</font> + visual "
                       "<font face='Courier'>desc</font>; add palette hex codes for brand color.", BODY), value=4),
    ListItem(Paragraph("<b>Generate and review</b> placement. Adjust coordinates and re-run while "
                       "the layout is still settling.", BODY), value=5),
    ListItem(Paragraph("<b>Lock it in.</b> Once you love the composition, switch to <b>Magic Fill / "
                       "region edit</b> for any final, surgical fixes so the rest is preserved.", BODY), value=6),
    ListItem(Paragraph("<b>Export</b> at the resolution you need (up to native 2K).", BODY), value=7),
], bulletType="1", leftIndent=16, bulletColor=ACCENT2, spaceBefore=2, spaceAfter=4))

story.append(rule())
story.append(Paragraph("Common pitfalls", H3))
story.append(bullets([
    "<b>Wrong coordinate order.</b> It's [y_min, x_min, y_max, x_max] — y comes first.",
    "<b>Content in the wrong field.</b> Literal words belong in <font face='Courier'>text</font>; "
    "<font face='Courier'>desc</font> is style only.",
    "<b>Expecting a JSON edit to be surgical.</b> Re-running regenerates everything; use region "
    "edit for localized changes.",
    "<b>Over-stuffed boxes.</b> Too much text in a small box clips or shrinks — size to fit.",
    "<b>Inconsistent color.</b> Reuse the same hex values rather than re-describing colors in words.",
]))

story.append(rule())
story.append(Paragraph("Quick reference", H3))
story.append(panel([
    Paragraph(
        "<b>Box</b> = one element's rectangular region.&nbsp;&nbsp; "
        "<b>Coords</b> = [y_min, x_min, y_max, x_max], 0–1000, top-left origin.<br/>"
        "<b>text</b> = literal characters.&nbsp;&nbsp; <b>desc</b> = visual style.&nbsp;&nbsp; "
        "<b>palette</b> = up to 16 hex colors.<br/>"
        "<b>Edit JSON</b> → re-generates all.&nbsp;&nbsp; <b>Magic Fill</b> → edits one region, "
        "keeps the rest.", PANELBODY),
], bg=PANEL2, border=ACCENT))

# ---- Sources ----
story.append(Spacer(1, 12))
story.append(rule(color=LINE))
story.append(Paragraph("Sources", H3))
story.append(bullets([
    "Ideogram official docs — Prompt Box &amp; Editor (docs.ideogram.ai)",
    "Ideogram 4.0 technical announcement (ideogram.ai/blog/ideogram-4.0)",
    "Runware — Structured prompts for Ideogram 4.0",
    "Ideogram 4.0 prompt &amp; layout-control guides (imagine.art, theplanettools.ai, creeta.com)",
], style=SMALL))

# ----------------------------------------------------------------------------
doc = SimpleDocTemplate(
    OUTPUT, pagesize=letter,
    leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    topMargin=0.85 * inch, bottomMargin=0.85 * inch,
    title="A High-Level Guide to Boxes in Ideogram 4",
    author="TradesmanPass",
)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print("Wrote", OUTPUT)
