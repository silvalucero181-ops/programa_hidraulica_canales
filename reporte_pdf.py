"""Reporte en PDF de LYCANAL PRO: primero la tabla de resultados y después el procedimiento."""
import io
import os
import unicodedata
from datetime import date
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, PolyLine, Polygon, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Tipografía: Barlow Condensed (títulos) y Lato (texto), incluidas en la carpeta "fuentes"
AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes")
try:
    for nombre, arch in (("Lato", "Lato-Regular.ttf"), ("Lato-Bold", "Lato-Bold.ttf"), ("Barlow", "BarlowCondensed-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(nombre, os.path.join(AQUI, arch)))
    F_REG, F_BOLD, F_TIT, UNI = "Lato", "Lato-Bold", "Barlow", True
except Exception:
    F_REG, F_BOLD, F_TIT, UNI = "Helvetica", "Helvetica-Bold", "Helvetica-Bold", False

MAR, ORO, TUR = colors.HexColor("#0a1a3a"), colors.HexColor("#e3b341"), colors.HexColor("#4fb3a9")
CREMA, LINEA = colors.HexColor("#f4f1ea"), colors.HexColor("#d9d3c4")
SUST = {"√": "raiz", "≤": "<=", "≥": ">=", "→": "->", "γ": "gamma", "Σ": "suma", "≈": "~", "−": "-", "–": "-", "₁": "1", "₂": "2", "ᵢ": "i", "ₑ": "e", "²": "^2", "³": "^3", "ȳ": "y medio"}


def limpiar(t):
    t = str(t).replace("✓ ", "").replace("✓", "")
    if UNI: return t
    t = "".join(SUST.get(ch, ch) for ch in t)
    return "".join(ch if ord(ch) < 256 else (unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode() or "?") for ch in t)


def P(texto, estilo): return Paragraph(escape(limpiar(texto)), estilo)


E_TIT = ParagraphStyle("t", fontName=F_TIT, fontSize=30, textColor=ORO, leading=32)
E_SUB = ParagraphStyle("s", fontName=F_REG, fontSize=10, textColor=colors.HexColor("#b5c6dc"), leading=14)
E_H = ParagraphStyle("h", fontName=F_TIT, fontSize=18, textColor=MAR, spaceBefore=12, spaceAfter=3, leading=20)
E_TX = ParagraphStyle("x", fontName=F_REG, fontSize=10, leading=14.5, textColor=colors.HexColor("#16233b"))
E_PASO = ParagraphStyle("p", fontName=F_TIT, fontSize=14.5, textColor=MAR, spaceBefore=9, spaceAfter=2, leading=17)
E_RES = ParagraphStyle("r", fontName=F_BOLD, fontSize=10, textColor=MAR, leading=14)


def dibujo(c, w=440, h=230):
    d = c["dibujo"]
    xs = [p[0] for p in d["linea"]]; zs = [p[1] for p in d["linea"]] + [d["top"]]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    esc = min((w - 70) / ((x1 - x0) or 1), (h - 60) / ((z1 - z0) or 1))
    tx, tz = (lambda x: 35 + (x - x0) * esc), (lambda z: 25 + (z - z0) * esc)
    D = Drawing(w, h); D.hAlign = "CENTER"
    for poly in d["agua"]:
        D.add(Polygon([v for p in poly for v in (tx(p[0]), tz(p[1]))], fillColor=colors.HexColor("#a9dcd6"), strokeColor=None))
    D.add(PolyLine([v for p in d["linea"] for v in (tx(p[0]), tz(p[1]))], strokeColor=MAR, strokeWidth=3))
    ln = Line(tx(x0), tz(d["top"]), tx(x1), tz(d["top"]), strokeColor=ORO, strokeWidth=1.5); ln.strokeDashArray = [5, 3]; D.add(ln)
    xm = (tx(x0) + tx(x1)) / 2
    D.add(String(xm, (tz(z0) + tz(d["nivel"])) / 2, f"y = {c['y']:.3f} m", textAnchor="middle", fontSize=10, fontName=F_BOLD, fillColor=MAR))
    D.add(String(xm, tz(d["top"]) + 5, f"H = y + BL = {c['H']:.3f} m", textAnchor="middle", fontSize=9, fontName=F_REG, fillColor=colors.HexColor("#9a7410")))
    return D


def pasos(c):
    f = lambda v, d=3: f"{v:.{d}f}"
    out = []
    if c["diseno"] and c["diseno"].get("circ"):
        d = c["diseno"]
        out.append(("Dimensionamiento de la sección", ["Máxima eficiencia hidráulica: semicírculo, y = D/2", "A = πD²/8   P = πD/2   R = D/4", "Se halla D tal que Q(D, y = D/2) = Q (bisección)"], f"D = {f(d['D'])} m  |  y = {f(d['y'])} m"))
    elif c["diseno"]:
        d = c["diseno"]
        out.append(("Dimensionamiento de la sección", [f"Criterio: {d['crit']}", f"b/y = {d['f']}·(√(1+z²) − z) = {f(d['m'])}",
                    "y = [Q·n/√S · (m + 2√(1+z²))^(2/3) / (m + z)^(5/3)]^(3/8)"], f"y = {f(d['y'])} m  |  b = {f(d['b'])} m"))
    out.append(("Datos del problema", [f"Sección: {c['tipo']}{c['dims']}", f"Q = {f(c['Q'])} m³/s (convertido a SI)", f"S = {c['S']:.4f} m/m", f"Incógnita: {c['inc']}"], None))
    r = []
    if c["horton"]:
        r.append("nₑ = [Σ(Pᵢ·nᵢ^1.5) / P]^(2/3)")
        r += [f"{nm}: P = {f(p)} m, n = {f(nn)}, P·n^1.5 = {p * nn ** 1.5:.4f}" for nm, p, nn in c["horton"]]
        r.append(f"nₑ = {f(c['n_base'])}")
    elif not c["cowan"]:
        r.append(f"Material: {c['material']}, con n tomado directamente.")
    if c["cowan"]:
        k = c["cowan"]
        r += ["n = (n0 + n1 + n2 + n3 + n4)·m5", f"n = ({f(k[0])} + {f(k[1])} + {f(k[2])} + {f(k[3])} + {f(k[4])}) × {f(k[5])}"]
    if c.get("sub"):
        r = ["Cada subárea se calcula con su propio n (Horton dentro de la subárea)."] + [f"{d['nombre']} ({d['tramos']}): A = {f(d['A'])} m², P = {f(d['P'])} m, n = {f(d['n'])}, R = {f(d['R'])} m" for d in c["sub"]]
    out.append(("Rugosidad", r, f"n = {f(c['n'])} ({c['origen']})"))
    FORM = {"Chezy": "C = dato", "Bazin": "C = 87 / (1 + γ/√R)", "Ganguillet-Kutter": "C = (23 + 0.00155/S + 1/n) / (1 + (23 + 0.00155/S)·n/√R)"}
    if c["metodo"] == "Manning":
        l3 = ["Q = (1/n)·A·R^(2/3)·S^(1/2)", f"{f(c['Q'])} = (1/{f(c['n'])}) × {f(c['A'])} × {f(c['R'])}^(2/3) × {c['S']:.4f}^(1/2)"]
    else:
        l3 = [FORM[c["metodo"]], "Q = C·A·√(R·S)", f"C = {f(c['C'])}", f"{f(c['Q'])} = {f(c['C'])} × {f(c['A'])} × √({f(c['R'])} × {c['S']:.4f})"]
    if c.get("sub"):
        l3 = ["Q = ΣQi", "Qi = (1/ni)·Ai·Ri^(2/3)·S^(1/2)" if c["metodo"] == "Manning" else "Qi = Ci·Ai·√(Ri·S)"] + [f"{d['nombre']}: Q = {f(d['Q'])} m³/s" for d in c["sub"]] + [f"ΣQi = {f(sum(d['Q'] for d in c['sub']))} m³/s"]
    res3 = {"pendiente": f"S = {c['S']:.4f} m/m", "caudal": f"Q = {f(c['Q'])} m³/s", "tirante crítico": f"yc = {f(c['y'])} m  |  Sc = {c['S']:.4f} m/m"}.get(c["inc"], f"y = {f(c['y'])} m ({c['iter']} iteraciones de bisección)")
    out.append((f"Ecuación de {c['metodo']}", l3, res3))
    g = {"Rectangular": ["A = b·y", "P = b + 2y", "T = b"], "Trapezoidal": ["A = (b + z·y)·y", "P = b + 2y·√(1+z²)", "T = b + 2·z·y"],
         "Triangular": ["A = z·y²", "P = 2y·√(1+z²)", "T = 2·z·y"],
         "Circular": ["θ = 2·acos(1 − 2y/D)", "A = D²/8·(θ − senθ)", "P = D·θ/2", "T = D·sen(θ/2)"],
         "Parabólica": ["T = T0·√(y/H)", "A = (2/3)·T·y", "P = 2·[x/2·√(1+4a²x²) + asenh(2ax)/(4a)],  con x = T/2 y a = H/(T0/2)²"]}.get(c["tipo"], ["A = ΣAᵢ", "P = ΣPᵢ", "T = ΣTᵢ"])
    out.append(("Elementos geométricos", g + [f"A = {f(c['A'])} m²   P = {f(c['P'])} m   T = {f(c['T'])} m",
                f"R = A/P = {f(c['A'])}/{f(c['P'])} = {f(c['R'])} m", f"ȳ = A/T = {f(c['A'] / c['T'])} m"], None))
    out.append(("Velocidad y número de Froude", [f"V = Q/A = {f(c['Q'])}/{f(c['A'])} = {f(c['V'])} m/s", "F = V / √(g·A/T)", f"F = {f(c['F'])}"],
                f"Régimen {c['reg'].lower()}: {c['msg_reg']}"))
    if c["energia"]:
        out.append(("Tirante crítico y energía específica", ["Q²/g = Ac³/Tc", f"E = y + V²/2g = {f(c['y'])} + {f(c['V'])}²/(2·9.81) = {f(c['E'])} m",
                    f"Energía mínima = {f(c['Ec'])} m", f"Tirante alterno y₂ = {c.get('y2t', '')}"],
                    f"Tirante crítico yc = {f(c['yc'])} m  |  Energía E = {f(c['E'])} m"))
    else:
        out.append(("Tirante crítico", ["Q²/g = Ac³/Tc"], f"Tirante crítico yc = {f(c['yc'])} m"))
    out.append(("Verificación de velocidad", [f"{c['vmin']:.2f} ≤ V = {f(c['V'])} ≤ {c['vmax']:.2f} m/s"], c["msg_v"]))
    if c.get("altura") is not None:
        bld = c["altura"] - c["y"]
        out.append(("Borde libre", [f"Método: {c['metodo_bl']}", c["bl_formula"], f"Criterio: {c['crit']}", f"BL disponible = altura − y = {f(c['altura'])} − {f(c['y'])} = {f(bld)} m", f"Altura mínima necesaria = y + BL = {f(c['y'] + c['BL'])} m"],
                    f"BL requerido = {f(c['BL'])} m  |  BL disponible = {f(bld)} m  |  " + ("Cumple" if bld >= c["BL"] - 1e-9 else "No cumple")))
    else:
        out.append(("Borde libre", [f"Método: {c['metodo_bl']}", c["bl_formula"], f"Criterio: {c['crit']}"], f"BL = {f(c['BL'])} m  |  H = y + BL = {f(c['H'])} m"))
    return out


def generar(c):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm, bottomMargin=1.8 * cm, title="Reporte LYCANAL PRO")
    pr = c.get("proyecto") or {}
    filas_b = [[P("LYCANAL PRO", E_TIT)], [P(f"Reporte de cálculo  |  {c['titulo']}", E_SUB)]]
    l1 = "   |   ".join(f"{k}: {pr[v]}" for k, v in (("Proyecto", "nombre"), ("Lugar", "lugar"), ("Tramo", "tramo")) if pr.get(v))
    if l1: filas_b.append([P(l1, E_SUB)])
    filas_b.append([P((f"Elaborado por: {pr['autor']}   |   " if pr.get("autor") else "") + f"Fecha: {date.today():%d/%m/%Y}", E_SUB)])
    band = Table(filas_b, colWidths=[17 * cm])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), MAR), ("LINEBELOW", (0, -1), (-1, -1), 3, ORO), ("LEFTPADDING", (0, 0), (-1, -1), 14),
                              ("TOPPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 10)]))
    S = [band, P("1. Resultados", E_H), HRFlowable(width="100%", color=ORO, thickness=1.2), Spacer(1, 5)]
    rows, est = [], [("FONTNAME", (0, 0), (-1, -1), F_REG), ("FONTSIZE", (0, 0), (-1, -1), 10), ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
                     ("LEFTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    for g, items in c["grupos"]:
        k = len(rows)
        est += [("SPAN", (0, k), (1, k)), ("BACKGROUND", (0, k), (1, k), MAR), ("TEXTCOLOR", (0, k), (1, k), ORO), ("FONTNAME", (0, k), (1, k), F_TIT), ("FONTSIZE", (0, k), (1, k), 12.5)]
        rows.append([limpiar(g), ""])
        for i, (a, b) in enumerate(items):
            k = len(rows)
            if i % 2 == 0: est.append(("BACKGROUND", (0, k), (1, k), CREMA))
            est.append(("FONTNAME", (1, k), (1, k), F_BOLD))
            rows.append([limpiar(a), limpiar(b)])
    t = Table(rows, colWidths=[9 * cm, 8 * cm]); t.setStyle(TableStyle(est)); S.append(t)
    S += [Spacer(1, 6), P(c["msg_v"], E_TX), P(c["msg_reg"], E_TX)] + ([P(c["aviso"], E_TX)] if c["aviso"] else [])
    comp = [["Método", "BL (m)", "H = y + BL (m)"]]
    est2 = [("FONTNAME", (0, 0), (-1, -1), F_REG), ("FONTSIZE", (0, 0), (-1, -1), 9.5), ("GRID", (0, 0), (-1, -1), 0.4, LINEA), ("BACKGROUND", (0, 0), (-1, 0), MAR),
            ("TEXTCOLOR", (0, 0), (-1, 0), ORO), ("FONTNAME", (0, 0), (-1, 0), F_BOLD), ("ALIGN", (1, 0), (-1, -1), "CENTER")]
    for mt, bl, _ in c["comp_bl"]:
        sel = mt == c["metodo_bl"]
        if sel: est2 += [("BACKGROUND", (0, len(comp)), (-1, len(comp)), colors.HexColor("#fbf5e0")), ("FONTNAME", (0, len(comp)), (-1, len(comp)), F_BOLD)]
        comp.append([limpiar(mt + ("  (elegido)" if sel else "")), "No aplica" if bl is None else f"{bl:.3f}", "-" if bl is None else f"{c['y'] + bl:.3f}"])
    tc = Table(comp, colWidths=[9 * cm, 3.5 * cm, 4.5 * cm]); tc.setStyle(TableStyle(est2))
    S += [KeepTogether([P("Comparación de métodos de borde libre", E_PASO), tc])]
    S.append(KeepTogether([P("2. Sección", E_H), HRFlowable(width="100%", color=ORO, thickness=1.2), dibujo(c)]))
    S += [P("3. Procedimiento", E_H), HRFlowable(width="100%", color=ORO, thickness=1.2)]
    for i, (tit, lineas, res) in enumerate(pasos(c), 1):
        bloque = [P(f"{i}. {tit}", E_PASO)] + [P(l, E_TX) for l in lineas]
        if res:
            r = Table([[P(res, E_RES)]], colWidths=[17 * cm]); r.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbf5e0")), ("LINEBEFORE", (0, 0), (0, -1), 3, ORO), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
            bloque += [Spacer(1, 3), r]
        S.append(KeepTogether(bloque))
    def pie(cv, d):
        cv.saveState(); cv.setFont(F_REG, 8.5); cv.setFillColor(colors.grey)
        cv.drawString(2 * cm, 1 * cm, limpiar("LYCANAL PRO  |  Desarrollado por Lucero Yamile Silva de la Cruz")); cv.drawRightString(19 * cm, 1 * cm, f"Página {d.page}"); cv.restoreState()
    doc.build(S, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()



    
    
