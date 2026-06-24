#!/usr/bin/env python3
"""Generate the local Ideogram-4 dashboard research/strategy report (diagram-rich PDF)."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, PageBreak, Flowable, KeepTogether,
)

OUTPUT = "Local-Ideogram4-Dashboard-Report.pdf"

# ---------------------------------------------------------------- palette ----
INK     = colors.HexColor("#12182B")
ACCENT  = colors.HexColor("#0F8B8D")   # teal
ACCENT2 = colors.HexColor("#5B3CC4")   # violet
WARM    = colors.HexColor("#E8833A")   # amber
ROSE    = colors.HexColor("#E94560")
GREEN   = colors.HexColor("#2E8B57")
BLUE    = colors.HexColor("#3F7CAC")
SOFT    = colors.HexColor("#56607A")
PANEL   = colors.HexColor("#F2F5FA")
PANEL2  = colors.HexColor("#EEF6F6")
PANEL3  = colors.HexColor("#F4F0FC")
WARNBG  = colors.HexColor("#FCEEE6")
CODE_BG = colors.HexColor("#1B1B2B")
CODE_FG = colors.HexColor("#E6E6F0")
LINE    = colors.HexColor("#D5DBE6")
GREY    = colors.HexColor("#C7D0DD")
CW = 6.6 * inch

# ----------------------------------------------------------------- styles ----
ss = getSampleStyleSheet()
H1   = ParagraphStyle("H1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
SUB  = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica", fontSize=12.5, leading=17, textColor=SOFT)
H2   = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=16, leading=19.5, textColor=ACCENT2, spaceBefore=14, spaceAfter=6)
H3   = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=15.5, textColor=INK, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica", fontSize=10.3, leading=15, textColor=INK, spaceAfter=6)
SMALL= ParagraphStyle("SMALL", parent=BODY, fontSize=8.6, leading=12, textColor=SOFT)
CAP  = ParagraphStyle("CAP", parent=SMALL, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
BUL  = ParagraphStyle("BUL", parent=BODY, spaceAfter=2.5, leftIndent=2)
LABEL= ParagraphStyle("LABEL", parent=BODY, fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=ACCENT)
PB   = ParagraphStyle("PB", parent=BODY, fontSize=9.8, leading=14, spaceAfter=4)
TH   = ParagraphStyle("TH", parent=BODY, fontName="Helvetica-Bold", fontSize=8.8, leading=11, textColor=colors.white)
TD   = ParagraphStyle("TD", parent=BODY, fontSize=8.6, leading=11, spaceAfter=0)
TDB  = ParagraphStyle("TDB", parent=TD, fontName="Helvetica-Bold")
CODE = ParagraphStyle("CODE", parent=ss["Code"], fontName="Courier", fontSize=8.3, leading=11.6, textColor=CODE_FG)


def rule(c=LINE, w=0.8, sb=8, sa=8):
    return HRFlowable(width="100%", thickness=w, color=c, spaceBefore=sb, spaceAfter=sa)

def bullets(items, style=BUL):
    return ListFlowable([ListItem(Paragraph(t, style), leftIndent=10, value="•") for t in items],
                        bulletType="bullet", bulletColor=ACCENT, bulletFontSize=8, leftIndent=12, spaceBefore=2, spaceAfter=6)

def panel(flow, bg=PANEL, border=LINE, pad=10):
    t = Table([[flow]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0.8,border),
        ("LEFTPADDING",(0,0),(-1,-1),pad),("RIGHTPADDING",(0,0),(-1,-1),pad),
        ("TOPPADDING",(0,0),(-1,-1),pad),("BOTTOMPADDING",(0,0),(-1,-1),pad),("VALIGN",(0,0),(-1,-1),"TOP")]))
    return t

def code_block(lines):
    paras=[Paragraph((ln.replace("&","&amp;").replace("<","&lt;").replace(" ","&nbsp;")) or "&nbsp;", CODE) for ln in lines]
    t=Table([[p] for p in paras], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CODE_BG),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,0),9),("BOTTOMPADDING",(0,-1),(-1,-1),9),
        ("TOPPADDING",(0,1),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-2),0)]))
    return t

def htable(header, rows, widths, head_bg=ACCENT2, zebra=(colors.white, PANEL)):
    data=[[Paragraph(h, TH) for h in header]]
    for r in rows:
        data.append([Paragraph(c, TD) for c in r])
    t=Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),head_bg),("GRID",(0,0),(-1,-1),0.5,LINE),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),list(zebra))]))
    return t


# ============================================================ diagrams ======
def _box(c,x,y,w,h,fill,stroke,label,sub=None,lc=colors.white,fs=9,r=5,lw=1.2,sub_fs=6.6):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.roundRect(x,y,w,h,r,fill=1,stroke=1)
    c.setFillColor(lc); c.setFont("Helvetica-Bold",fs); cx=x+w/2.0
    if sub:
        c.drawCentredString(cx,y+h/2.0+2,label); c.setFont("Helvetica",sub_fs); c.drawCentredString(cx,y+h/2.0-9,sub)
    else:
        c.drawCentredString(cx,y+h/2.0-fs/2.0+1,label)

def _arrow(c,x1,y1,x2,y2,color=INK,lw=1.2,head=5,dash=None):
    import math
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash,0)
    c.line(x1,y1,x2,y2); c.setDash()
    ang=math.atan2(y2-y1,x2-x1)
    for da in (math.radians(150),math.radians(-150)):
        c.line(x2,y2,x2+head*math.cos(ang+da),y2+head*math.sin(ang+da))


class ArchDiagram(Flowable):
    """Three-tier local dashboard architecture."""
    def __init__(self,w=CW,h=4.1*inch): super().__init__(); self.width=w; self.height=h
    def draw(self):
        c=self.canv; W,H=self.width,self.height
        # user
        _box(c,W/2-0.8*inch,H-0.42*inch,1.6*inch,0.34*inch,SOFT,SOFT,"USER",fs=8.5,r=5)
        def tier(y,th,fill,stroke,title):
            c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1)
            c.roundRect(0.05*inch,y,W-0.1*inch,th,7,fill=1,stroke=1)
            c.setFillColor(stroke); c.setFont("Helvetica-Bold",7.5)
            c.saveState(); c.translate(0.2*inch,y+th-0.16*inch)
            c.drawString(0,0,title); c.restoreState()
        # Tier 1 frontend
        t1y=H-1.62*inch
        tier(t1y,1.05*inch,colors.HexColor("#F4F0FC"),ACCENT2,"TIER 1 · FRONTEND  —  Tauri 2 shell (Rust core, ~12 MB)")
        for i,(lab,sub) in enumerate([("Konva canvas","drag-to-draw bbox"),("JSON panel","live, validated"),("Inspector","per-region prompt"),("Gallery","remixable assets")]):
            _box(c,0.28*inch+i*1.58*inch,t1y+0.32*inch,1.42*inch,0.46*inch,colors.white,ACCENT2,lab,sub,lc=INK,fs=8,sub_fs=6.3)
        # Zustand store badge (below the four views)
        _box(c,W/2-1.5*inch,t1y+0.04*inch,3.0*inch,0.22*inch,ACCENT2,ACCENT2,"↑ all four are controlled views over ONE Zustand store",fs=7,r=4)
        # Tier 2 orchestration
        t2y=H-2.78*inch
        tier(t2y,1.0*inch,PANEL2,ACCENT,"TIER 2 · LOCAL ORCHESTRATION  (no cloud)")
        for i,(lab,sub) in enumerate([("Prompt compiler","schema → CUI graph"),("Magic-Prompt","local LLM (llama.cpp)"),("Queue manager","non-blocking"),("WS client","progress + preview")]):
            _box(c,0.28*inch+i*1.58*inch,t2y+0.22*inch,1.42*inch,0.5*inch,colors.white,ACCENT,lab,sub,lc=INK,fs=8,sub_fs=6.3)
        # Tier 3 backend
        t3y=H-3.95*inch
        tier(t3y,1.0*inch,PANEL2,GREEN,"TIER 3 · BACKEND ENGINE  —  ComfyUI (local, day-0 Ideogram-4 support)")
        for i,(lab,sub,col) in enumerate([("Ideogram-4","NF4 / GGUF Q4_K",GREEN),("+ Realism LoRA","native IG-4 adapter",WARM),("Upscaler","4x / SUPIR (tiled)",BLUE),("Detailer","ADetailer face/hands",ROSE)]):
            _box(c,0.28*inch+i*1.58*inch,t3y+0.22*inch,1.42*inch,0.5*inch,col,col,lab,sub,fs=8,sub_fs=6.3)
        # arrows between tiers
        _arrow(c,W/2,H-0.42*inch,W/2,t1y+1.05*inch,color=SOFT)
        _arrow(c,W/2-0.3*inch,t1y,W/2-0.3*inch,t2y+1.0*inch,color=ACCENT,lw=1.3)
        c.setFillColor(ACCENT); c.setFont("Helvetica",6.3); c.drawString(W/2-1.7*inch,t2y+1.04*inch,"POST /prompt")
        _arrow(c,W/2+0.3*inch,t2y+1.0*inch,W/2+0.3*inch,t1y,color=BLUE,lw=1.3,dash=(2,2))
        c.drawString(W/2+0.4*inch,t2y+1.04*inch,"WS preview ↑")
        _arrow(c,W/2,t2y,W/2,t3y+1.0*inch,color=GREEN,lw=1.3)


class SyncDiagram(Flowable):
    """Two-way bbox <-> JSON sync via a single store."""
    def __init__(self,w=CW,h=2.7*inch): super().__init__(); self.width=w; self.height=h
    def draw(self):
        c=self.canv; W,H=self.width,self.height
        cx,cy=W/2,H/2
        _box(c,cx-1.15*inch,cy-0.42*inch,2.3*inch,0.84*inch,ACCENT2,ACCENT2,"STATE STORE",
             "regions[] + global prompt + style",fs=10.5,sub_fs=7,r=8)
        nodes=[(cx,H-0.55*inch,ACCENT,"CANVAS (Konva)","draggable / resizable boxes"),
               (0.95*inch,cy,GREEN,"INSPECTOR","per-region desc / text / palette"),
               (W-0.95*inch,cy,WARM,"RAW JSON","editable, schema-validated")]
        for x,y,col,lab,sub in nodes:
            _box(c,x-1.05*inch,y-0.32*inch,2.1*inch,0.64*inch,col,col,lab,sub,fs=8.8,sub_fs=6.4)
        # bidirectional arrows
        _arrow(c,cx,H-0.87*inch,cx,cy+0.42*inch,color=ACCENT,lw=1.2)
        _arrow(c,cx-0.18*inch,cy+0.42*inch,cx-0.18*inch,H-0.87*inch,color=GREY,lw=1,head=4)
        _arrow(c,1.7*inch,cy+0.18*inch,cx-1.15*inch,cy+0.18*inch,color=GREEN,lw=1.1)
        _arrow(c,cx-1.15*inch,cy-0.05*inch,1.7*inch,cy-0.05*inch,color=GREY,lw=1,head=4)
        _arrow(c,W-1.7*inch,cy+0.18*inch,cx+1.15*inch,cy+0.18*inch,color=WARM,lw=1.1)
        _arrow(c,cx+1.15*inch,cy-0.05*inch,W-1.7*inch,cy-0.05*inch,color=GREY,lw=1,head=4)
        c.setFillColor(SOFT); c.setFont("Helvetica-Oblique",6.8)
        c.drawCentredString(cx,H-0.12*inch,"controlled views — last valid edit wins; invalid JSON keeps last good boxes")


class VramDiagram(Flowable):
    """24GB budget: with vs without text-encoder offload."""
    def __init__(self,w=CW,h=2.7*inch): super().__init__(); self.width=w; self.height=h
    def draw(self):
        c=self.canv; W,H=self.width,self.height
        cap=24.0
        bar_x=1.55*inch; bar_w=W-2.5*inch; bh=0.6*inch
        def bar(y,segs,title,overflow=False):
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawRightString(bar_x-0.12*inch,y+bh/2-3,title)
            x=bar_x
            for val,col,lab in segs:
                w=bar_w*(val/cap)
                c.setFillColor(col); c.setStrokeColor(colors.white); c.setLineWidth(0.8)
                c.rect(x,y,w,bh,fill=1,stroke=1)
                if w>0.5*inch:
                    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",6.6)
                    c.drawCentredString(x+w/2,y+bh/2-2,lab)
                x+=w
            # 24GB ceiling line
            c.setStrokeColor(ROSE if overflow else INK); c.setLineWidth(1.1); c.setDash((3,2),0)
            c.line(bar_x+bar_w,y-3,bar_x+bar_w,y+bh+3); c.setDash()
            if overflow:
                c.setFillColor(ROSE); c.setFont("Helvetica-Bold",6.4)
                c.drawRightString(bar_x+bar_w-3,y+bh+5,"x  overflows 24 GB -> spills to slow system RAM")
        # without offload: weights 16 + text enc 14 + act 7 = 37 (overflow)
        bar(H-1.0*inch,[(13,ROSE,"DiT NF4 ~13–16G"),(14,colors.HexColor("#C0607A"),"Qwen3-VL text enc ~14G")],"WITHOUT offload",overflow=True)
        # with offload: weights ~13 + act ~7 + vae ~1 + headroom
        bar(H-2.1*inch,[(13,GREEN,"DiT 4-bit ~13G"),(7,BLUE,"activations ~7G"),(1.5,ACCENT,"VAE"),(2.5,GREY,"headroom")],"WITH offload")
        c.setFillColor(INK); c.setFont("Helvetica-Bold",7.5)
        c.drawString(bar_x,H-2.5*inch,"RTX 4090 = 24 GB ceiling (dashed).  CPU-offloading the Qwen3-VL-8B text encoder is what brings 2K under 24 GB.")


class PipelineDiagram(Flowable):
    """Generation -> refine -> upscale -> detail flow."""
    def __init__(self,w=CW,h=2.0*inch): super().__init__(); self.width=w; self.height=h
    def draw(self):
        c=self.canv; W,H=self.width,self.height
        y=H-1.15*inch; bw=1.12*inch; bh=0.7*inch; gap=(W-5*bw)/4.0
        stages=[("1 · JSON+bbox","prompt compiled\nfrom canvas",ACCENT2),
                ("2 · IDEOGRAM-4","generate 1K\n12-step turbo\n+ realism LoRA",GREEN),
                ("3 · REFINE","img2img\ndenoise ~0.25",WARM),
                ("4 · UPSCALE","tiled 4x /\nSUPIR → 2K",BLUE),
                ("5 · DETAIL","ADetailer\nface · eyes · hands",ROSE)]
        xs=[]
        for i,(lab,sub,col) in enumerate(stages):
            x=gap*0+i*(bw+gap)
            c.setFillColor(col); c.setStrokeColor(col); c.setLineWidth(1)
            c.roundRect(x,y,bw,bh,5,fill=1,stroke=1)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold",7.4)
            c.drawCentredString(x+bw/2,y+bh-12,lab)
            c.setFont("Helvetica",6.0)
            for j,line in enumerate(sub.split("\n")):
                c.drawCentredString(x+bw/2,y+bh-23-j*7.5,line)
            xs.append((x,x+bw))
        for i in range(4):
            _arrow(c,xs[i][1]+1,y+bh/2,xs[i+1][0]-1,y+bh/2,color=SOFT,lw=1.2,head=4)
        _box(c,W/2-0.9*inch,y-0.6*inch,1.8*inch,0.32*inch,INK,INK,"hyper-real 2K output",fs=7.6,r=4)
        _arrow(c,xs[4][1]-bw/2,y,W/2+0.5*inch,y-0.28*inch,color=SOFT,lw=1)


# ----------------------------------------------------------- page furniture --
def hf(canvas, doc):
    canvas.saveState(); w,h=letter
    canvas.setFillColor(ACCENT2); canvas.rect(0,h-0.16*inch,w,0.16*inch,fill=1,stroke=0)
    canvas.setFillColor(ACCENT); canvas.rect(0,h-0.16*inch,w*0.45,0.16*inch,fill=1,stroke=0)
    if doc.page>1:
        canvas.setFont("Helvetica",8); canvas.setFillColor(SOFT)
        canvas.drawString(0.9*inch,0.55*inch,"Local Ideogram-4 Dashboard — Research & Strategy")
        canvas.drawRightString(w-0.9*inch,0.55*inch,"Page %d"%doc.page)
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5); canvas.line(0.9*inch,0.72*inch,w-0.9*inch,0.72*inch)
    canvas.restoreState()


# =================================================================== STORY ===
S=[]

# Cover
S.append(Spacer(1,0.3*inch))
S.append(Paragraph("Research &amp; Strategy Report", SUB))
S.append(Paragraph("A Premium Local Dashboard for Ideogram&nbsp;4", H1))
S.append(Spacer(1,2))
S.append(Paragraph("Smoothing the JSON-prompting &amp; bounding-box pain — and driving hyper-realistic "
                   "generation entirely on a local RTX&nbsp;4090, no cloud.", SUB))
S.append(Spacer(1,12))
S.append(panel([
    Paragraph("THE THESIS", LABEL),
    Paragraph("Ideogram&nbsp;4's biggest frustrations — mandatory JSON, fiddly hand-typed bounding "
              "boxes, whole-image regen on every edit, expiring credits, queues, and a censorship gate — "
              "are <b>mostly UX and delivery problems, not model problems</b>. Ideogram&nbsp;4 shipped as "
              "<b>open weights</b> that run on a 24&nbsp;GB 4090. So we can keep the model's strengths "
              "(best-in-class text + native layout control) and wrap them in a <b>visual, local, "
              "no-credits dashboard</b> that fixes the delivery layer. This report covers the top&nbsp;10 "
              "pain points, the local engine feasibility, a realism pipeline, and a build plan.", PB),
], bg=PANEL2, border=ACCENT))
S.append(Spacer(1,10))
S.append(panel([
    Paragraph("READ FIRST  —  LICENSING", ParagraphStyle("w",parent=LABEL,textColor=WARM)),
    Paragraph("The public Ideogram&nbsp;4 weights are released under a <b>non-commercial</b> model "
              "agreement. Personal/research/local use is fine; any client-facing, internal-business, or "
              "revenue-linked use needs Ideogram's <b>paid commercial license</b> (which also unlocks "
              "full-precision weights). Verify <font face='Courier'>LICENSE.md</font> on the HuggingFace "
              "repo before building anything commercial on these weights.", PB),
], bg=WARNBG, border=WARM))
S.append(Spacer(1,10))
S.append(Paragraph("Prepared June 2026. Findings from Reddit/X, GitHub, HuggingFace, ComfyUI &amp; Civitai "
                   "research; sources on the final pages. Post-release figures are directional — flagged in text.", SMALL))
S.append(PageBreak())

# 1. Executive summary
S.append(Paragraph("1 · Executive summary", H2))
S.append(bullets([
    "<b>The opportunity.</b> No existing local tool offers a clean <b>visual bbox → structured-JSON</b> "
    "editor. Ideogram&nbsp;4 is the first model where that editor is genuinely valuable — and it's now "
    "self-hostable. That's the gap to own.",
    "<b>Feasibility: yes, on a 4090.</b> Ideogram&nbsp;4 is a 9.3B diffusion transformer. A 4-bit build "
    "(NF4, or GGUF&nbsp;Q4_K for better text) fits 24&nbsp;GB when the Qwen3-VL text encoder is "
    "CPU-offloaded. Expect ~20–70&nbsp;s at 1K, ~60&nbsp;s at 2K.",
    "<b>Engine: ComfyUI as a local backend</b> (day-0 Ideogram-4 support) behind a custom premium UI "
    "— don't reinvent diffusion; reinvent the experience.",
    "<b>Realism path.</b> Ideogram&nbsp;4 supports its own LoRAs, but Civitai realism LoRAs (Flux/SDXL) "
    "<b>do not load on it</b> — use Ideogram-4-native LoRAs, or route a refine/detail pass through a "
    "second engine. Pair with upscalers + face/hand detailers.",
    "<b>What local fixes:</b> credits, queues, privacy, the censorship gate, and — via the visual editor "
    "— the JSON/bbox pain. What it can't fix: the non-commercial license and the model's photoreal ceiling.",
]))
S.append(rule())
S.append(Paragraph("At-a-glance verdict", H3))
S.append(htable(
    ["Question","Verdict"],
    [["Run Ideogram&nbsp;4 locally on a 4090?","<b>Yes</b> — 4-bit only; offload the text encoder; batch size 1 at 2K."],
     ["Best checkpoint?","<b>NF4</b> for compatibility; <b>GGUF Q4_K</b> for better text fidelity at the same VRAM."],
     ["Fix JSON/bbox pain?","<b>Yes</b> — a visual canvas that emits correct <font face='Courier'>[y,x,y,x]</font> JSON."],
     ["Hyper-realism?","<b>Partly</b> — IG-4 LoRA + refine/upscale/detail chain; may borrow a Flux/SDXL refiner."],
     ["Ship commercially on open weights?","<b>No</b> — non-commercial license; needs paid tier."]],
    [2.3*inch,4.3*inch], head_bg=ACCENT)
)
S.append(PageBreak())

# 2. Top 10 pain points
S.append(Paragraph("2 · The top&nbsp;10 Ideogram&nbsp;4 pain points (Reddit / X / forums)", H2))
S.append(Paragraph("Ranked by how often and how loudly users raise them, with the segment each hurts most.", BODY))
pains=[
 ["1","JSON prompting feels mandatory &amp; brittle","Docs admit plain text underperforms and trips the safety filter more — users feel forced into authoring/maintaining JSON 'design briefs.'","Hobbyists"],
 ["2","Bounding-box placement is fiddly","Coordinates are hand-tuned on a 0–1000 grid; overlapping boxes melt typography. No live visual feedback in the base product — guess, generate, inspect, repeat.","Designers"],
 ["3","Coordinate order confusion","bbox is y-first <font face='Courier'>[y_min,x_min,y_max,x_max]</font> — reverse of the x-first convention; swaps silently misplace elements.","Developers"],
 ["4","JSON edits regenerate everything","Changing one field re-runs full inference; the whole composition shifts. Localized fixes need a separate Magic-Fill/inpaint detour.","Designers"],
 ["5","Expiring credits &amp; surprise pricing","Free tier repeatedly cut; priority credits don't roll over; some changes shipped unannounced (incl. to paid users).","Hobbyists"],
 ["6","Slow / unpredictable queue","Slow-queue waits ballooned (reports up to ~20 min); throughput as low as a few images/hour at peak.","Marketers"],
 ["7","Aggressive safety filter","Benign prompts blocked inconsistently (documented GitHub examples); false-positive rate higher for non-JSON prompts.","All"],
 ["8","'Open-weight' is non-commercial","Weights are downloadable but non-commercial; widely mis-read as open source. Commercial use needs the paid tier.","Developers"],
 ["9","Photoreal / consistency / weak seeds","Strong on type, weaker on photoreal &amp; character consistency; seeds give poor reproducibility.","Designers"],
 ["10","Flat output — no layers","Single flat PNG; logos arrive with artifacts, no vector/layers — assets get rebuilt in a real editor.","Designers"],
]
S.append(htable(["#","Pain point","What users say","Hurts"],
    [[p[0],("<b>"+p[1]+"</b>"),p[2],p[3]] for p in pains],
    [0.22*inch,1.65*inch,3.85*inch,0.88*inch], head_bg=ACCENT2))
S.append(Spacer(1,6))
S.append(panel([Paragraph("WHAT USERS WISH EXISTED", LABEL),
    Paragraph("A drag-and-drop bbox canvas that writes the JSON for them · true localized edits (change one "
              "element, freeze the rest) · no credits/queues/surprise pricing · transparent, tunable safety · "
              "layered/editable output. <b>A local dashboard delivers four of these five.</b>", PB)], bg=PANEL2, border=ACCENT))
S.append(PageBreak())

# 3. Pain -> local fix matrix
S.append(Paragraph("3 · What a local dashboard actually fixes", H2))
S.append(Paragraph("Honest mapping of each pain point to whether self-hosting on your own GPU solves it.", BODY))
def chip(v):
    col={"Yes":GREEN,"Partly":WARM,"No":ROSE}[v]
    return ("<font color='#%s'><b>%s</b></font>"%(col.hexval()[2:], v))
fix=[
 ["JSON mandatory/brittle","Partly","UI auto-builds &amp; lints JSON from plain text; model's JSON reliance remains."],
 ["Bbox fiddliness","Yes","Drag-to-draw canvas emits coordinates — pure UX layer, fully solvable."],
 ["Coordinate-order confusion","Yes","Visual editor never exposes raw [y,x,y,x]; the app writes it correctly."],
 ["Edit regenerates all","Partly","Wire in mask/inpaint + seed-lock for region edits; not a true layered edit."],
 ["Expiring credits / pricing","Yes","Own-GPU inference removes credits, billing, and surprise changes."],
 ["Slow queue / speed","Yes","No shared queue; bounded only by your hardware."],
 ["Safety-filter false positives","Partly","Self-hosted weights skip the hosted gate; you own compliance + license risk."],
 ["Non-commercial license","No","A dashboard can't change the license; commercial use needs the paid tier."],
 ["Photoreal / consistency / seed","Partly","True deterministic seeds + easy A/B; photoreal ceiling is model-bound."],
 ["Flat / no layers","Partly","Chain bg-removal / segmentation / vectorize; native layers await next model."],
]
S.append(htable(["Pain point","Local fix?","Why"],
    [[f[0],chip(f[1]),f[2]] for f in fix],
    [1.85*inch,0.8*inch,3.95*inch], head_bg=ACCENT))
S.append(Spacer(1,6))
S.append(Paragraph("Scorecard: <b>4 fully solved</b> (bbox, coordinate order, credits, queue), "
                   "<b>5 smoothed</b>, <b>1 out of scope</b> (license). The fully-solved set is exactly the "
                   "set people complain about most — which is what makes this product compelling.", BODY))
S.append(PageBreak())

# 4. System architecture
S.append(Paragraph("4 · Proposed system architecture", H2))
S.append(Paragraph("A thin, premium native shell over a local ComfyUI engine. The UI owns the experience; "
                   "ComfyUI owns the compute. Everything runs on the one machine — no network calls leave it.", BODY))
S.append(ArchDiagram())
S.append(Paragraph("Fig.&nbsp;1 — Three tiers: a Tauri/React frontend with a Konva bbox canvas, a local "
                   "orchestration layer that compiles the structured prompt into a ComfyUI graph, and "
                   "ComfyUI running Ideogram-4 + realism add-ons.", CAP))
S.append(Paragraph("Stack rationale", H3))
S.append(bullets([
    "<b>Shell — Tauri&nbsp;2</b> over Electron: ~12&nbsp;MB vs ~180&nbsp;MB, 30–50&nbsp;MB idle RAM, faster "
    "start, sandboxed FS access — it matters next to a GPU-hungry backend. (Electron is the fallback if you "
    "want zero WebView quirks.)",
    "<b>Frontend — React + TypeScript + Konva.js</b> (the stack InvokeAI ships): official React bindings, a "
    "built-in Transformer for resize handles, multi-layer canvas, snapping/bounded drag.",
    "<b>State — Zustand</b>: one normalized store is the single source of truth for the canvas, inspector, "
    "and JSON views.",
    "<b>Backend — ComfyUI</b> via <font face='Courier'>POST /prompt</font> + a "
    "<font face='Courier'>ws://</font> connection for live progress and latent previews.",
]))
S.append(PageBreak())

# 5. The visual editor (the killer feature)
S.append(Paragraph("5 · The killer feature — a visual bbox <-> JSON editor", H2))
S.append(Paragraph("This is the heart of the product and the direct antidote to pain points&nbsp;1–4. One store, "
                   "three synchronized views, with two-way binding so the canvas and the JSON never drift.", BODY))
S.append(SyncDiagram())
S.append(Paragraph("Fig.&nbsp;2 — Two-way sync. Dragging a box normalizes to 0–1000 and writes the store; "
                   "editing JSON parses/validates and updates boxes. The store is authoritative.", CAP))
S.append(Paragraph("The structured-prompt model it edits (Ideogram-4 schema)", H3))
S.append(code_block([
 "{",
 '  "high_level_description": "...",',
 '  "style_description": {',
 '    "photo" | "art_style": "...",   // exactly one',
 '    "aesthetics": "...", "lighting": "...", "medium": "...",',
 '    "color_palette": ["#RRGGBB", ...]      // <= 16, UPPERCASE',
 '  },',
 '  "compositional_deconstruction": {',
 '    "background": "...",',
 '    "elements": [',
 '      { "type":"text", "bbox":[y_min,x_min,y_max,x_max],  // 0-1000, y-first',
 '        "text":"GRAND OPENING", "desc":"bold serif, gold" },',
 '      { "type":"obj",  "bbox":[450,550,880,950], "desc":"glass juice bottle" }',
 '    ]',
 '  }',
 "}",
]))
S.append(Paragraph("Implementation notes: serialize with fixed key order and compact separators (the model is "
                   "order-sensitive); enforce schema live (one of <font face='Courier'>photo</font>/"
                   "<font face='Courier'>art_style</font>, uppercase hex, &lt;=16 colors); warn when a box covers "
                   "&lt;2% of canvas (spatial conditioning is low-res). The <b>benjiyaya/ComfyUI-Ideogram4-Toolkit</b> "
                   "already provides a drag-to-draw 1000×1000 canvas node you can learn from or wrap.", SMALL))
S.append(PageBreak())

# 6. Running on the 4090
S.append(Paragraph("6 · Running Ideogram&nbsp;4 on the RTX&nbsp;4090", H2))
S.append(Paragraph("Ideogram&nbsp;4 is a 9.3B single-stream diffusion transformer (34 layers, flow-matching) "
                   "with a frozen <b>Qwen3-VL-8B</b> text encoder and an 8× VAE, native 256–2048&nbsp;px. The "
                   "text encoder is the VRAM pressure point — and the key to fitting 24&nbsp;GB.", BODY))
S.append(VramDiagram())
S.append(Paragraph("Fig.&nbsp;3 — VRAM budget. Resident, the DiT + text encoder overflow 24&nbsp;GB; "
                   "CPU-offloading the Qwen3-VL encoder brings a 2K generation under the ceiling.", CAP))
S.append(htable(["Spec","Value"],
    [["Params / arch","9.3B DiT, 34 layers, flow-matching, Euler ODE sampler"],
     ["Text encoder","Qwen3-VL-8B-Instruct (frozen; ~14&nbsp;GB if resident → offload it)"],
     ["Checkpoints","<font face='Courier'>ideogram-4-nf4</font>, <font face='Courier'>-fp8</font>; Comfy-Org mirror; GGUF Q4_K community builds"],
     ["Fits 24&nbsp;GB?","NF4 / Q4_K <b>yes</b> (tight, batch 1 at 2K). FP8 needs 32&nbsp;GB+ — not on a 4090."],
     ["Speed (4090, 4-bit)","~21&nbsp;s 1K turbo · ~32&nbsp;s default · ~72&nbsp;s quality · ~60&nbsp;s at 2K (directional)"],
     ["Layout interface","Structured JSON is the <b>native</b> conditioning — no ControlNet needed for bbox"]],
    [1.7*inch,4.9*inch], head_bg=ACCENT2))
S.append(Spacer(1,6))
S.append(panel([Paragraph("CHECKPOINT PICK", LABEL),
    Paragraph("Start on <b>NF4</b> (guaranteed Diffusers/ComfyUI support). If text fidelity matters — and it's "
              "Ideogram's whole point — switch to a <b>GGUF&nbsp;Q4_K</b> build via <font face='Courier'>city96/"
              "ComfyUI-GGUF</font>: research reports it beats NF4 quality at the same size, and NF4 specifically "
              "degrades lettering. Benchmark both on your card.", PB)], bg=PANEL3, border=ACCENT2))
S.append(PageBreak())

# 7. Hyper-realism pipeline
S.append(Paragraph("7 · The hyper-realism pipeline", H2))
S.append(Paragraph("Ideogram&nbsp;4 stays the generator; realism is layered on with a LoRA plus a standard "
                   "local refine/upscale/detail chain — the single biggest portrait-realism win is auto face/hand "
                   "detailing before upscaling.", BODY))
S.append(PipelineDiagram())
S.append(Paragraph("Fig.&nbsp;4 — Generate small with a realism LoRA, refine at low denoise, tiled-upscale to 2K, "
                   "then auto-detail faces/eyes/hands. (Time grows super-linearly with pixels, so small→upscale "
                   "beats native 2K.)", CAP))
S.append(panel([Paragraph("THE LoRA COMPATIBILITY CATCH", ParagraphStyle("w",parent=LABEL,textColor=WARM)),
    Paragraph("LoRAs are architecture-specific. The Civitai realism LoRAs everyone knows are trained on "
              "<b>Flux / SDXL / Pony / Z-Image</b> — <b>none load on Ideogram&nbsp;4's transformer.</b> Two real "
              "paths: <b>(a)</b> use/train <b>Ideogram-4-native LoRAs</b> (fal.ai V4 trainer or ai-toolkit; "
              "early HF collections exist), or <b>(b)</b> keep IG-4 for layout+text, then route a low-denoise "
              "<b>refine pass through Flux/SDXL</b> where the realism LoRA ecosystem lives.", PB)],
    bg=WARNBG, border=WARM))
S.append(PageBreak())

# 8. Realism LoRA research
S.append(Paragraph("8 · Realism LoRA &amp; add-on research", H2))
S.append(Paragraph("Your 'Realism v5' must-have didn't map to a Civitai creator named 'red' — flagging it as "
                   "<b>to-confirm</b>. Closest matches, then a curated stack (grouped by base model, since they "
                   "don't cross over).", BODY))
S.append(Paragraph("Your 'Realism v5' — best candidates (confirm the link)", H3))
S.append(bullets([
    "<b>RealVisXL V5.0</b> (SDXL) — the dominant 'V5' realism model; it's a <i>checkpoint</i>, not a LoRA. Most "
    "people saying 'Realism v5' mean this.",
    "<b>Realistic Snapshot (Z-Image-Turbo) – v5 'Real Life'</b> by MonkeyForever — the only headline 'v5' realism "
    "<i>LoRA</i> found by that name.",
    "<b>UltraRealistic LoRA Project v2</b> / <b>Improved Amateur Snapshot</b> (Flux) — top Flux realism LoRAs if "
    "you're on a Flux refiner.",
]))
S.append(Paragraph("Curated realism stack (grouped by base model)", H3))
S.append(htable(["Resource","Base","Improves","Weight"],
    [["Improved Amateur Snapshot (AI_Characters)","Flux","Phone-photo realism, natural light","0.7–1.0"],
     ["UltraRealistic LoRA Project v2","Flux","Overall realism, anatomy","0.6–0.9"],
     ["Flux Skin Texture v2 / Skin Detailer DoRA","Flux","Pores, anti-plastic skin","0.4–0.8"],
     ["RealVisXL V5.0 (checkpoint)","SDXL","Photoreal base model","—"],
     ["Detail Tweaker XL","SDXL","Universal detail slider","1.0–1.5"],
     ["Skin Realism (Acne/Imperfections)","SDXL","Real pores, blemishes","0.4–0.8"],
     ["Realistic Snapshot v5 (MonkeyForever)","Z-Image","'Real life' candid texture","0.6–0.9"],
     ["Ideogram-4 native LoRAs (fal.ai / HF)","Ideogram-4","The only ones that load on IG-4","~0.6"]],
    [2.55*inch,0.95*inch,2.35*inch,0.75*inch], head_bg=ACCENT)
)
S.append(Spacer(1,5))
S.append(Paragraph("Non-LoRA realism boosters", H3))
S.append(bullets([
    "<b>Detailers:</b> ADetailer / FaceDetailer (Impact Pack) — auto-inpaint face → eyes → hands. Biggest single "
    "portrait win.",
    "<b>Upscalers:</b> 4x-UltraSharp (fast) or SUPIR (best quality, use FP8 UNet + tiled VAE for 24&nbsp;GB); "
    "ControlNet Tile for detail injection.",
    "<b>Settings:</b> stack 2–3 realism LoRAs at 0.4–0.8 each (over-stacking burns); add a film-grain/amateur LoRA "
    "last at low weight to break the 'too clean' look.",
]))
S.append(PageBreak())

# 9. Performance tuning
S.append(Paragraph("9 · 4090 performance tuning checklist", H2))
S.append(htable(["Lever","Action","Payoff"],
    [["Quantization","4-bit NF4 (compat) or GGUF Q4_K (text); never FP8 on 24&nbsp;GB","Fits the card"],
     ["Text-encoder offload","CPU-offload Qwen3-VL-8B (~14&nbsp;GB)","Brings 2K under ceiling"],
     ["Tiled VAE decode","Tile the 2K decode stage","Avoids decode spike"],
     ["Attention","Flash / SageAttention (8-bit attn)","'Significant' speedup"],
     ["Step caching","TeaCache-style; Sage+TeaCache ≈ ~2&nbsp;min, Flash+TeaCache ≈ ~1&nbsp;min/img","Fewer effective steps"],
     ["torch.compile","Enable","Modest (~6%)"],
     ["Sampler presets","12-step turbo for previews; 48-step for finals","Draft fast, finalize sharp"],
     ["Resolution strategy","Generate 1K → upscale (4× area ≈ 6.3× time)","Beats native 2K"],
     ["Batch / hygiene","Batch 1 at 2K; restart backend to clear VRAM before big runs","Stability"]],
    [1.3*inch,3.65*inch,1.65*inch], head_bg=ACCENT2))
S.append(PageBreak())

# 10. Premium feel + roadmap
S.append(Paragraph("10 · 'Premium feel' &amp; build roadmap", H2))
S.append(Paragraph("Premium-feel feature set", H3))
S.append(bullets([
    "<b>Live latent previews</b> streamed over the ComfyUI WebSocket (TAESD), throttled ~2–4&nbsp;fps; per-step "
    "progress on the canvas.",
    "<b>Non-blocking queue</b> — enqueue many jobs, keep editing; cancel/reorder.",
    "<b>Two-way undo/redo</b> over the store (canvas <i>and</i> JSON), keyboard shortcuts for everything, nudge "
    "boxes with arrow keys.",
    "<b>Gallery with full provenance</b> — store the exact JSON + seed + graph with each image; 'remix' loads it "
    "back into the editor; drag a result onto a region as a reference.",
    "<b>Magic-Prompt (local)</b> — a local LLM expands a one-line idea into schema-valid JSON with sensible boxes.",
    "<b>Dark-first UI</b> — 4+ surface levels, separation by luminance/borders not shadows (Linear/Raycast feel), "
    "smooth GPU canvas pan/zoom, subtle micro-interactions.",
]))
S.append(rule())
S.append(Paragraph("Phased roadmap", H3))
S.append(htable(["Phase","Scope","Outcome"],
    [["0 · Spike","ComfyUI + Ideogram-4 NF4 on the 4090; confirm speeds + offload","De-risk the engine"],
     ["1 · MVP","Tauri+React shell, Konva bbox canvas, JSON two-way sync, single generate","The core 'aha' editor"],
     ["2 · Realism","Refine→upscale→detail graph; IG-4 LoRA loader; preset library","Hyper-real output"],
     ["3 · Premium","Live previews, queue, gallery/provenance, undo, shortcuts, dark UI","'Premium feel'"],
     ["4 · Edit","Mask/inpaint region edits + seed-lock to approximate localized edits","Smooths pain #4"]],
    [0.95*inch,3.6*inch,2.05*inch], head_bg=ACCENT)
)
S.append(Spacer(1,6))
S.append(panel([Paragraph("BOTTOM LINE", LABEL),
    Paragraph("The fastest credible build is <b>ComfyUI (engine) + a Tauri/React/Konva front-end</b> whose star is "
              "the <b>visual bbox-to-JSON editor</b>. That single feature neutralizes Ideogram&nbsp;4's four loudest "
              "complaints, and self-hosting removes credits, queues, and the censorship gate. Mind the "
              "non-commercial license and the photoreal ceiling — plan a Flux/SDXL refiner if IG-4-native realism "
              "LoRAs fall short.", PB)], bg=PANEL3, border=ACCENT2))
S.append(PageBreak())

# Sources
S.append(Paragraph("Appendix · Key sources", H2))
S.append(Paragraph("Model &amp; local engine", H3))
S.append(bullets([
    "HuggingFace: <font face='Courier'>ideogram-ai/ideogram-4-nf4</font> · <font face='Courier'>-fp8</font> · "
    "<font face='Courier'>Comfy-Org/Ideogram-4</font> · <font face='Courier'>transformerlab/ideogram-4-gguf-q4_k</font>",
    "GitHub: <font face='Courier'>ideogram-oss/ideogram4</font> (docs/pipeline.md, docs/prompting.md) · "
    "<font face='Courier'>ideogram-oss/ComfyUI-Ideogram4</font> · <font face='Courier'>benjiyaya/ComfyUI-Ideogram4-Toolkit</font> · "
    "<font face='Courier'>city96/ComfyUI-GGUF</font>",
    "ComfyUI day-0 support &amp; tutorial (comfyui.org, docs.comfy.org) · Diffusers Ideogram4 pipeline docs · "
    "Transformer Lab quantization study (lab.cloud) · omkamal '4090 structured JSON' benchmark.",
], style=SMALL))
S.append(Paragraph("Pain points &amp; UX", H3))
S.append(bullets([
    "Ideogram 4 reviews (goenhance 'messy open-weight story', seaart) · safety-filter GitHub issue "
    "<font face='Courier'>ideogram-oss/ideogram4#5</font> · pricing/queue threads (eesel, Aiville, Trustpilot) · "
    "Ideogram on X re: queue scheduling.",
    "Local UI landscape: ComfyUI / InvokeAI (Konva canvas, regional guidance) / Krita AI Diffusion / SwarmUI / "
    "Fooocus / Forge. Tauri-vs-Electron &amp; Konva-vs-Fabric write-ups.",
], style=SMALL))
S.append(Paragraph("Realism", H3))
S.append(bullets([
    "Civitai: RealVisXL V5.0 · Realistic Snapshot Z-Image v5 (MonkeyForever, #2268008) · UltraRealistic LoRA "
    "Project (#796382) · Improved Amateur Snapshot (#970862) · Detail Tweaker XL (#122359) · Skin/Eye/Hand "
    "detailer LoRAs.",
    "Ideogram-4 LoRA: fal.ai V4 trainer · <font face='Courier'>DeverStyle/Ideogram-4.0-Loras</font> (HF) · "
    "ai-toolkit training guide. SUPIR &amp; ADetailer realism add-ons.",
], style=SMALL))
S.append(Spacer(1,8))
S.append(panel([Paragraph("RELIABILITY NOTE", LABEL),
    Paragraph("Ideogram&nbsp;4 released after the assistant's training cutoff, so all model facts come from June 2026 "
              "web research. Speed figures and the 'GGUF beats NF4' quality claim lean on one or two detailed sources "
              "— treat as directional and benchmark on your hardware. Several sites (Civitai, some blogs) block direct "
              "fetch; their URLs are real but verify specifics on-page. The non-commercial license is well-corroborated "
              "and is the most important item to confirm firsthand.", PB)], bg=PANEL, border=LINE))

# ----------------------------------------------------------------------------
doc=SimpleDocTemplate(OUTPUT, pagesize=letter, leftMargin=0.9*inch, rightMargin=0.9*inch,
                      topMargin=0.85*inch, bottomMargin=0.85*inch,
                      title="A Premium Local Dashboard for Ideogram 4 — Research & Strategy",
                      author="TradesmanPass")
doc.build(S, onFirstPage=hf, onLaterPages=hf)
print("Wrote", OUTPUT)
