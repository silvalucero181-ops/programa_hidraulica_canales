import math
import pandas as pd
import plotly.graph_objects as go
import modulo_energia
import reporte_pdf
import streamlit as st
import motor_hidraulico as mh

st.set_page_config(page_title="LYCANAL PRO", page_icon="💧", layout="wide")
MAR, ORO, TUR = "#0a1a3a", "#e3b341", "#4fb3a9"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&display=swap');
.stApp{background:#f4f1ea}
.tarjeta{padding:44px 24px 40px;border-radius:28px;text-align:center;color:#9fb4cf;margin:2vh auto 14px;max-width:900px;
 background:radial-gradient(ellipse at 25% 20%,#14396b 0%,#0a1a3a 70%);box-shadow:0 14px 40px rgba(10,26,58,.35)}
.tarjeta .sup{color:#e3b341;font-size:13px;letter-spacing:.35em}
.tarjeta svg{display:block;width:min(320px,80%);margin:24px auto 8px}
.tarjeta .titulo{font-family:'Barlow Condensed','Arial Narrow',sans-serif;color:#e3b341;font-size:clamp(52px,9vw,92px);line-height:1.05;font-weight:700;letter-spacing:.02em}
.tarjeta .barra{width:176px;height:4px;margin:18px auto;border-radius:2px;background:linear-gradient(90deg,#e3b341,#4fb3a9)}
.tarjeta .desc{max-width:560px;margin:0 auto;font-size:19px;line-height:1.5}
.tarjeta .autor{margin-top:24px;font-size:14px}.tarjeta .autor b{color:#4fb3a9}
.barra-sup{background:#0a1a3a;border-bottom:3px solid #e3b341;padding:10px 24px;border-radius:8px;margin-bottom:14px}
.barra-sup .titulo{font-family:'Barlow Condensed',sans-serif;font-size:32px;color:#e3b341;font-weight:700}.barra-sup small{color:#9fb4cf;margin-left:12px}
h3{font-family:'Barlow Condensed',sans-serif;color:#0a1a3a;border-bottom:1px solid #d9d3c4;padding-bottom:2px}
.stButton>button{background:#0a1a3a;border:1px solid #e3b341;border-radius:10px;font-weight:600}
.stButton>button p{color:#e3b341!important}.stButton>button:hover{background:#12305a;border-color:#e3b341}
.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:2px solid #d9d3c4}
.stTabs [data-baseweb="tab"]{padding:8px 18px;color:#0a1a3a}
.stTabs [aria-selected="true"]{background:#0a1a3a;color:#e3b341!important;border-bottom:3px solid #e3b341}
.stTabs [aria-selected="true"] p{color:#e3b341!important}
.stTabs [data-baseweb="tab-highlight"]{display:none}
[data-testid="stMetric"]{background:#fff;border:1px solid #d9d3c4;border-left:5px solid #e3b341;padding:12px 16px;border-radius:10px}
[data-testid="stMetricLabel"] p{color:#4a5a78;font-size:14px}
[data-testid="stMetricValue"]{color:#0a1a3a;font-family:'Barlow Condensed',sans-serif;font-size:34px;font-weight:700}
.grupo{font-family:'Barlow Condensed',sans-serif;font-size:22px;color:#0a1a3a;margin:22px 0 8px;padding-bottom:3px;border-bottom:2px solid #e3b341}
.paso{display:flex;align-items:center;gap:10px;font-family:'Barlow Condensed',sans-serif;font-size:23px;font-weight:600;color:#0a1a3a;margin-bottom:6px}
.paso .num{background:#0a1a3a;color:#e3b341;width:30px;height:30px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:18px}
.res{background:#fbf5e0;border-left:4px solid #e3b341;padding:7px 14px;border-radius:4px;color:#0a1a3a;font-weight:600;margin:8px 0 2px}
.res.ok{background:#e8f4f2;border-left-color:#4fb3a9}.res.mal{background:#fbebee;border-left-color:#a3203f}
[data-testid="stVerticalBlockBorderWrapper"]:has(.paso){background:#fff;border:1px solid #d9d3c4;border-left:5px solid #0a1a3a;border-radius:10px}
.mod{background:#fff;border:1px solid #d9d3c4;border-top:4px solid #e3b341;border-radius:10px;padding:14px 16px;min-height:112px}
.mod h4{font-family:'Barlow Condensed',sans-serif;font-size:24px;color:#0a1a3a;margin:0 0 4px}.mod p{margin:0;color:#4a5a78;font-size:14px}
.mod.off{opacity:.55;border-top-color:#9aa6b8}
@media (min-width: 900px){
    [data-testid="stHorizontalBlock"]:has(.ancla-der){align-items:flex-start}
    [data-testid="stColumn"]:has(.ancla-der){position:sticky;top:4rem;max-height:calc(100vh - 5rem);overflow-y:auto;padding-right:6px}
}
table.cw{width:100%;border-collapse:collapse;font-size:14px;background:#fff}
table.cw th{background:#0a1a3a;color:#e3b341;padding:7px 8px;border:1px solid #0a1a3a;text-align:center}
table.cw td{border:1px solid #d9d3c4;padding:5px 8px;color:#16233b}
table.cw td.g{font-weight:600;color:#0a1a3a;background:#f4f1ea}table.cw td.f{text-align:center;font-style:italic;font-weight:600}
table.cw td.v{text-align:center;font-weight:600;color:#0a1a3a}
table.cw tr.sel td{background:#fbf5e0;font-weight:700;border-color:#e3b341}
table.cw td.na{color:#8a93a3;text-align:center}
</style>""", unsafe_allow_html=True)


def tabla_cowan():
    filas = ""
    for grupo, factor, items in mh.TABLA_COWAN:
        for i, (cond, val) in enumerate(items):
            ini = f"<td rowspan='{len(items)}' class='g'>{grupo}</td><td rowspan='{len(items)}' class='f'>{factor}</td>" if i == 0 else ""
            filas += f"<tr>{ini}<td>{cond}</td><td class='v'>{val}</td></tr>"
    return ("<table class='cw'><tr><th>Condiciones de flujo</th><th>Factor</th><th>Condición</th><th>Valor</th></tr>"
            + filas + "</table>")


CONFIG = {"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["zoom2d", "select2d", "lasso2d"]}


def formato_pendiente(S):
    """Muestra pendientes pequeñas en por mil para evitar que parezcan cero."""
    if abs(S) < 0.01:
        return f"{S:.6f} m/m | {1000*S:.4f} ‰"
    return formato_pendiente(S)


def dibujar(s, y, H, mats, ns=None):
    """Sección con revestimiento por material (color y trama), agua y borde libre."""
    hb, k, z = s.b / 2, s.k, s.z
    e = 0.06 * max(H, hb + z * H)
    xl, hw = hb + z * H, hb + z * y
    hbo, xlo = hb + e * k - z * e, hb + e * k + z * H
    fig = go.Figure()

    def poli(pts, mat, nombre):
        _, bg, fg, forma = mh.MATERIALES[mat]
        fig.add_trace(go.Scatter(x=[q[0] for q in pts] + [pts[0][0]], y=[q[1] for q in pts] + [pts[0][1]], mode="lines",
                                 fill="toself", line=dict(color=MAR, width=1.2), fillcolor=bg, name=nombre, hoveron="fills", text=f"{nombre}: {mat}",
                                 hoverinfo="text", fillpattern=dict(shape=forma, bgcolor=bg, fgcolor=fg, size=5, solidity=0.4)))
    poli([(-xl, H), (-hb, 0), (-hbo, -e), (-xlo, H)], mats[1], "Pared izquierda")
    poli([(xl, H), (hb, 0), (hbo, -e), (xlo, H)], mats[2], "Pared derecha")
    poli([(-hb, 0), (hb, 0), (hbo, -e), (-hbo, -e)], mats[0] if s.b > 0 else mats[1], "Fondo")
    fig.add_trace(go.Scatter(x=[-hb, hb, hw, -hw, -hb], y=[0, 0, y, y, 0], fill="toself", mode="lines", fillcolor="rgba(79,179,169,.40)",
                             line=dict(color=TUR, width=2), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[-xl, -hb, hb, xl], y=[H, 0, 0, H], mode="lines", line=dict(color=MAR, width=2.5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[-xlo, xlo], y=[H, H], mode="lines", line=dict(color=ORO, width=2, dash="dash"), hoverinfo="skip"))
    def nota(x, yy, t, size=12, **kw): fig.add_annotation(x=x, y=yy, text=t, showarrow=False, font=dict(color=MAR, size=size), **kw)
    if s.b > 0:
        nota(0, -e, f"b = {s.b:.4f} m" + (f"<br>{mats[0]}, n = {ns[0]:.4f}" if ns else ""), yshift=-22)
    nota(0, y / 2, f"y = {y:.4f} m", size=14)
    nota(0, y, f"T = {s.T(y):.4f} m", yshift=12)
    nota(xlo, H, f"H = {H:.4f} m", xanchor="left", xshift=6)
    if ns:
        nota(-(hb + e * k + z * H / 2), H / 2, f"{mats[1]}<br>n = {ns[1]:.4f}", xanchor="right", xshift=-8)
        nota((hb + e * k + z * H / 2), H / 2, f"{mats[2]}<br>n = {ns[2]:.4f}", xanchor="left", xshift=8)
    fig.update_layout(title="Visualización dinámica de la sección", height=500, plot_bgcolor="#faf8f3", paper_bgcolor="rgba(0,0,0,0)",
                      showlegend=False, dragmode="pan", margin=dict(l=40, r=40, t=60, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal / Ancho (m)", gridcolor="#e8e5dc", zerolinecolor="#c9ced6"),
                      yaxis=dict(title="Elevación / Altura (m)", gridcolor="#e8e5dc", zerolinecolor="#c9ced6", scaleanchor="x"))
    return fig


if "pag" not in st.session_state:
    st.session_state.pag = "portada"
    st.session_state.modulo = None

# ---------------- Portada ----------------
def _recortar_banda(poly, za, zb):
    """Parte de un polígono convexo con za <= z <= zb."""
    if math.isfinite(zb): poly = _recortar(poly, zb)
    if math.isfinite(za) and len(poly) >= 3:
        poly = [(x, -z) for x, z in _recortar([(x, -z) for x, z in poly], -za)]
    return poly


def _tira(s, i, L):
    (x1, z1), (x2, z2) = s.pts[i], s.pts[i + 1]
    if min(z1, z2) >= L: return None
    a, b_ = (x1, z1), (x2, z2)
    if z1 > L: a = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
    if z2 > L: b_ = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
    return [a, b_, (b_[0], L), (a[0], L)]


def dibujar_poli(s, y, H, ns=None):
    """Sección por puntos: tramos coloreados por material, agua y borde libre."""
    L, top = s.zmin + y, s.zmin + H
    COL = ["rgba(79,179,169,.45)", "rgba(227,179,65,.45)", "rgba(122,163,217,.45)"]
    fig = go.Figure()
    celdas = getattr(s, "subareas", None)
    if celdas:
        for j, sa in enumerate(celdas):
            for i in range(sa.a, sa.b):
                tira = _tira(s, i, L)
                poly = _recortar_banda(tira, sa.za, sa.zb) if tira else []
                if len(poly) >= 3:
                    fig.add_trace(go.Scatter(x=[q[0] for q in poly] + [poly[0][0]], y=[q[1] for q in poly] + [poly[0][1]], fill="toself", mode="lines",
                                             fillcolor=COL[j % 3], line=dict(width=0), hoverinfo="skip"))
    else:
        for i in range(len(s.pts) - 1):
            tira = _tira(s, i, L)
            if tira:
                fig.add_trace(go.Scatter(x=[q[0] for q in tira] + [tira[0][0]], y=[q[1] for q in tira] + [tira[0][1]], fill="toself", mode="lines",
                                         fillcolor=COL[0], line=dict(width=0), hoverinfo="skip"))
    nseg = len(s.pts) - 1
    if nseg <= 30: grupos_ = [(i, i) for i in range(nseg)]
    else:                                                  # muchos segmentos (arcos): se agrupan los del mismo material
        grupos_, ini = [], 0
        for i in range(1, nseg + 1):
            if i == nseg or (s.mats[i], s.ns[i]) != (s.mats[ini], s.ns[ini]): grupos_.append((ini, i - 1)); ini = i
    for g_, (i0, i1) in enumerate(grupos_):
        xs, zs = [s.pts[k][0] for k in range(i0, i1 + 2)], [s.pts[k][1] for k in range(i0, i1 + 2)]
        fig.add_trace(go.Scatter(x=xs, y=zs, mode="lines", line=dict(color=MAR, width=12), hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=xs, y=zs, mode="lines", line=dict(color=mh.MATERIALES[s.mats[i0]][1], width=8),
                                 hoverinfo="text", text=f"{s.mats[i0]}, n = {s.ns[i0]:.4f}"))
        if nseg <= 30:
            fig.add_annotation(x=sum(xs) / 2, y=sum(zs) / 2, text=f"T{i0 + 1}", showarrow=False, font=dict(color=MAR, size=11), bgcolor="#fff")
    if celdas and len(celdas) > 1:
        for a_, b_ in sorted({(sa.a, sa.b) for sa in celdas}):
            if a_ > 0:
                xk, zk = s.pts[a_]
                fig.add_trace(go.Scatter(x=[xk, xk], y=[zk, max(zk, L)], mode="lines", line=dict(color=MAR, width=1.5, dash="dash"), hoverinfo="skip"))
        for zc in s.cortes_h:
            if s.zmin < zc < L:
                xb = []
                for i in range(len(s.pts) - 1):
                    (x1, z1), (x2, z2) = s.pts[i], s.pts[i + 1]
                    if z1 < zc: xb.append(x1)
                    if z2 < zc: xb.append(x2)
                    if (z1 < zc) != (z2 < zc): xb.append(x1 + (zc - z1) / (z2 - z1) * (x2 - x1))
                fig.add_trace(go.Scatter(x=[min(xb), max(xb)], y=[zc, zc], mode="lines", line=dict(color=MAR, width=1.5, dash="dash"), hoverinfo="skip"))
        for j, sa in enumerate(celdas):
            if sa.A(y) > 1e-9:
                fig.add_annotation(x=(s.pts[sa.a][0] + s.pts[sa.b][0]) / 2, y=(max(sa.za, s.zmin) + min(sa.zb, L)) / 2, text=f"Subárea {j + 1}", showarrow=False, font=dict(color=MAR, size=11))
    x0, x1 = s.pts[0][0], s.pts[-1][0]
    fig.add_trace(go.Scatter(x=[x0, x1], y=[top, top], mode="lines", line=dict(color=ORO, width=2, dash="dash"), hoverinfo="skip"))
    xm = (x0 + x1) / 2
    xd, zm_ = x1 + 0.05 * (x1 - x0), s.zmin + y / 2
    fig.add_shape(type="line", x0=xd, x1=xd, y0=s.zmin, y1=L, line=dict(color=MAR, width=1.5))
    for zp in (L, s.zmin):
        fig.add_annotation(x=xd, y=zp, ax=xd, ay=zm_, axref="x", ayref="y", text="", showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor=MAR)
    fig.add_annotation(x=xd, y=zm_, text=f"y = {y:.4f} m", showarrow=False, xanchor="left", xshift=6, font=dict(color=MAR, size=13))
    fig.add_annotation(x=xm, y=L, text=f"T = {s.T(y):.4f} m", showarrow=False, yshift=12, font=dict(color=MAR, size=12))
    fig.add_annotation(x=x1, y=top, text=f"y + BL = {H:.4f} m", showarrow=False, xanchor="left", xshift=6, font=dict(color="#9a7410", size=12))
    ztop = min(s.pts[0][1], s.pts[-1][1])
    fig.add_trace(go.Scatter(x=[x0, x1], y=[ztop, ztop], mode="lines", line=dict(color=MAR, width=1.5, dash="dot"), hoverinfo="skip"))
    fig.add_annotation(x=x0, y=ztop, text=f"Altura de la sección = {s.altura:.4f} m", showarrow=False, xanchor="left", yshift=12, font=dict(color=MAR, size=11))
    fig.update_layout(title="Visualización dinámica de la sección", height=500, plot_bgcolor="#faf8f3", paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      dragmode="pan", margin=dict(l=40, r=60, t=60, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal (m)", gridcolor="#e8e5dc"),
                      yaxis=dict(title="Elevación (m)", gridcolor="#e8e5dc", scaleanchor="x"))
    return fig


TABLA_BL = [
    ("Máximo Villón (por tirante)", [("Canal sin revestir", "y/3"), ("Canal revestido", "y/5")]),
    ("USBR (Bureau of Reclamation)", [("Q ≤ 0.6 m³/s", "√(0.46·y)"), ("Q ≤ 85 m³/s", "√(0.76·y)")]),
    ("Villón por caudal", [("Q ≤ 0.5 m³/s", "0.30 m"), ("Q > 0.5 m³/s", "0.40 m")]),
    ("Villón por ancho de solera", [("b ≤ 0.8 m", "0.40 m"), ("0.8 < b ≤ 1.5 m", "0.50 m"), ("1.5 < b ≤ 3.0 m", "0.60 m"), ("3.0 < b ≤ 20 m", "1.00 m")]),
    ("ANA, Tabla 11 (por caudal)", [("Q ≤ 0.05 m³/s", "Revestido 0.075 m  /  Sin revestir 0.10 m"), ("0.05 < Q ≤ 0.25", "Revestido 0.10 m  /  Sin revestir 0.20 m"),
                                    ("0.25 < Q ≤ 0.50", "Revestido 0.20 m  /  Sin revestir 0.40 m"), ("0.50 < Q ≤ 1.00", "Revestido 0.25 m  /  Sin revestir 0.50 m"),
                                    ("Q > 1.00 m³/s", "Revestido 0.30 m  /  Sin revestir 0.60 m")]),
]


def tabla_bl():
    filas = ""
    for grupo, items in TABLA_BL:
        for i, (cond, val) in enumerate(items):
            ini = f"<td rowspan='{len(items)}' class='g'>{grupo}</td>" if i == 0 else ""
            filas += f"<tr>{ini}<td>{cond}</td><td class='v'>{val}</td></tr>"
    return "<table class='cw'><tr><th>Método</th><th>Condición</th><th>Borde libre</th></tr>" + filas + "</table>"


TIPOS_TRAMO = ["Vertical", "Talud", "Horizontal", "Arco circular", "Parábola (fondo)", "Recta (longitud y ángulo)"]
DEF_TRAMO = {"Vertical": (1.0, 0.0), "Talud": (1.0, 1.0), "Horizontal": (1.0, 0.0), "Arco circular": (0.5, 180.0), "Parábola (fondo)": (1.0, 0.3), "Recta (longitud y ángulo)": (1.0, 0.0)}


def construir_tramos(filas):
    """Convierte los tramos (vertical, talud, horizontal, arco, parábola o recta) en los puntos de una poligonal."""
    pts, ms, ns_, junc, seg_tr, errs = [(0.0, 0.0)], [], [], [], [], []
    for t, r in enumerate(filas, 1):
        x, y = pts[-1]; tp, a, b = r["tp"], r["a"], r["b"]; sg = -1 if r.get("sent", "Desciende") == "Desciende" else 1
        if tp == "Vertical": nuevos = [(x, y + sg * a)]
        elif tp == "Talud": nuevos = [(x + b * a, y + sg * a)]
        elif tp == "Horizontal": nuevos = [(x + a, y)]
        elif tp == "Recta (longitud y ángulo)": nuevos = [(x + a * math.cos(math.radians(b)), y + a * math.sin(math.radians(b)))]
        elif tp == "Arco circular":
            conc = r.get("forma", "Cóncavo (fondo)").startswith("Cónc")
            t0, ph = (-b / 2, b) if conc else (b / 2, -b)       # cóncavo: parte bajando y termina subiendo
            N, sgn = max(6, int(b / 6) + 1), (1 if ph >= 0 else -1)
            nuevos = []
            for k in range(1, N + 1):
                a_ = math.radians(t0 + ph * k / N)
                nuevos.append((x + sgn * a * (math.sin(a_) - math.sin(math.radians(t0))), y - sgn * a * (math.cos(a_) - math.cos(math.radians(t0)))))
        else:                                                    # parábola de fondo: ancho total a, profundidad b
            nuevos = [(x + a * k / 24, y - b + b * (2 * k / 24 - 1) ** 2) for k in range(1, 25)]
        for q in nuevos:
            pts.append(q); ms.append(r["mat"]); ns_.append(r["n"]); seg_tr.append(t)
        junc.append(len(pts) - 1)
    if any(pts[i + 1][0] < pts[i][0] - 1e-9 for i in range(len(pts) - 1)):
        errs.append("La sección debe avanzar de izquierda a derecha: revisa que ningún tramo vuelva hacia atrás.")
    return pts, ms, ns_, junc[:-1], seg_tr, errs


def tabla_compuesta():
    """Tramos editables, cada uno con su forma, su material y su n."""
    clave = "filas_cmp"
    MATL, CON = list(mh.MATERIALES), "Concreto (acabado con llana)"
    if clave not in st.session_state:
        base = [("Vertical", 1.0, 0.0, "Desciende"), ("Arco circular", 0.5, 180.0, "Desciende"), ("Vertical", 1.0, 0.0, "Asciende")]
        st.session_state[clave] = [dict(id=i, tp=b[0], tp_prev=b[0], a=b[1], b=b[2], sent=b[3], forma="Cóncavo (fondo)", mat=CON, n=0.013) for i, b in enumerate(base)]
    filas = st.session_state[clave]
    st.caption("Describe el contorno de izquierda a derecha, tramo por tramo, empezando arriba a la izquierda. Cada tramo continúa donde termina el anterior.")
    for i, r in enumerate(filas):
        with st.container(border=True):
            c1, c2 = st.columns([8, 2], vertical_alignment="bottom")
            r["tp"] = c1.selectbox(f"Tramo {i + 1}", TIPOS_TRAMO, index=TIPOS_TRAMO.index(r["tp"]), key=f"{clave}_tp_{r['id']}")
            if r.get("tp_prev") != r["tp"]:
                r["a"], r["b"] = DEF_TRAMO[r["tp"]]; r["tp_prev"] = r["tp"]
            c2.button("🗑", key=f"{clave}_del_{r['id']}", on_click=_eliminar, args=(clave, r["id"]), disabled=len(filas) <= 2, help="Eliminar este tramo")
            k = f"{clave}_{r['tp'][:4]}_%s_{r['id']}"
            u1, u2 = st.columns(2)
            nb = lambda col, etq, v, key, lo=0.01, hi=None, st_=0.1, fm="%.4f": col.number_input(etq, min_value=lo, max_value=hi, value=min(max(float(v), lo), hi if hi else 1e9), step=st_, format=fm, key=key)
            if r["tp"] == "Vertical":
                r["a"] = nb(u1, "Altura (m)", r["a"], k % "a")
                r["sent"] = u2.selectbox("Sentido", ["Desciende", "Asciende"], index=["Desciende", "Asciende"].index(r["sent"]), key=k % "s")
            elif r["tp"] == "Talud":
                r["a"] = nb(u1, "Desnivel vertical (m)", r["a"], k % "a"); r["b"] = nb(u2, "Talud z (H:V)", r["b"], k % "b", lo=0.0)
                r["sent"] = st.selectbox("Sentido", ["Desciende", "Asciende"], index=["Desciende", "Asciende"].index(r["sent"]), key=k % "s")
            elif r["tp"] == "Horizontal":
                r["a"] = nb(u1, "Ancho (m)", r["a"], k % "a")
            elif r["tp"] == "Arco circular":
                r["a"] = nb(u1, "Radio (m)", r["a"], k % "a"); r["b"] = nb(u2, "Ángulo del arco (°)", r["b"], k % "b", lo=10.0, hi=180.0, st_=5.0, fm="%.1f")
                r["forma"] = st.selectbox("Curvatura", ["Cóncavo (fondo)", "Convexo"], index=["Cóncavo (fondo)", "Convexo"].index(r["forma"]), key=k % "f")
                st.caption("Cóncavo: curva hacia abajo, como un fondo circular (180° es un semicírculo). Convexo: curva hacia arriba, como una joroba.")
            elif r["tp"] == "Parábola (fondo)":
                r["a"] = nb(u1, "Ancho total (m)", r["a"], k % "a"); r["b"] = nb(u2, "Profundidad (m)", r["b"], k % "b")
            else:
                r["a"] = nb(u1, "Longitud (m)", r["a"], k % "a"); r["b"] = nb(u2, "Ángulo (°)", r["b"], k % "b", lo=-90.0, hi=90.0, st_=5.0, fm="%.1f")
            m1, m2 = st.columns([3, 2])
            r["mat"] = m1.selectbox("Material del tramo", MATL, index=MATL.index(r["mat"]), key=f"{clave}_m_{r['id']}", on_change=_cambio_material, args=(clave, r["id"]))
            kn = f"{clave}_n_{r['id']}"
            r["n"] = m2.number_input("n", min_value=0.001, step=0.001, format="%.4f", key=kn, **({} if kn in st.session_state else {"value": float(r["n"])}))
    b1, b2 = st.columns(2)
    b1.button("➕ Agregar tramo", key=clave + "_add", on_click=_agregar, args=(clave,), width="stretch")
    b2.button("↺ Restablecer ejemplo", key=clave + "_reset", on_click=_restablecer, args=(clave,), width="stretch")
    pts_, _, _, junc_, _, _ = construir_tramos(filas)
    st.caption("Puntos finales de cada tramo (x, y): " + "  →  ".join(f"T{i + 1} ({pts_[j][0]:.2f}, {pts_[j][1]:.2f})" for i, j in enumerate(junc_ + [len(pts_) - 1])))
    return _salida_cmp(filas)


def _salida_cmp(filas):
    pts, ms, ns_, junc, seg_tr, errs = construir_tramos(filas)
    return pts, ms, ns_, errs, junc, seg_tr


def _recortar(poly, L):
    """Parte del polígono (convexo) que queda por debajo de la cota L."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        if p[1] <= L: out.append(p)
        if (p[1] <= L) != (q[1] <= L):
            t = (L - p[1]) / (q[1] - p[1]); out.append((p[0] + t * (q[0] - p[0]), L))
    return out


def perfil_cerrado(s, n=160):
    if isinstance(s, mh.Circular):
        R = s.D / 2
        return [(R * math.sin(-math.pi + 2 * math.pi * k / n), R - R * math.cos(-math.pi + 2 * math.pi * k / n)) for k in range(n + 1)]
    return [(-s.T0 / 2 + s.T0 * k / n, s.a * (-s.T0 / 2 + s.T0 * k / n) ** 2) for k in range(n + 1)]


def dibujar_cerrada(s, y, H, mats):
    """Sección circular o parabólica con su material, el agua y el borde libre."""
    per, circ = perfil_cerrado(s), isinstance(s, mh.Circular)
    ancho = s.D / 2 if circ else s.T0 / 2
    agua = _recortar(per, y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[p[0] for p in agua] + [agua[0][0]], y=[p[1] for p in agua] + [agua[0][1]], fill="toself", mode="lines",
                             fillcolor="rgba(79,179,169,.40)", line=dict(color=TUR, width=2), hoverinfo="skip"))
    xs, zs = [p[0] for p in per], [p[1] for p in per]
    fig.add_trace(go.Scatter(x=xs, y=zs, mode="lines", line=dict(color=MAR, width=12), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=zs, mode="lines", line=dict(color=mh.MATERIALES[mats[0]][1], width=8), hoverinfo="text", text=mats[0]))
    fig.add_trace(go.Scatter(x=[-ancho, ancho], y=[H, H], mode="lines", line=dict(color=ORO, width=2, dash="dash"), hoverinfo="skip"))
    def nota(x, yy, t, size=12, **kw): fig.add_annotation(x=x, y=yy, text=t, showarrow=False, font=dict(color=MAR, size=size), **kw)
    nota(0, y / 2, f"y = {y:.4f} m", 14)
    nota(0, y, f"T = {s.T(y):.4f} m", yshift=12)
    nota(ancho, H, f"y + BL = {H:.4f} m", xanchor="left", xshift=6)
    fig.add_trace(go.Scatter(x=[-ancho, ancho], y=[s.altura, s.altura], mode="lines", line=dict(color=MAR, width=1.5, dash="dot"), hoverinfo="skip"))
    nota(0, s.altura if not circ else s.D, (f"D = {s.D:.4f} m" if circ else f"H sección = {s.altura:.4f} m"), yshift=14)
    fig.update_layout(title="Visualización dinámica de la sección", height=500, plot_bgcolor="#faf8f3", paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      dragmode="pan", margin=dict(l=40, r=60, t=60, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal (m)", gridcolor="#e8e5dc"), yaxis=dict(title="Elevación (m)", gridcolor="#e8e5dc", scaleanchor="x"))
    return fig


def vista_previa(pts):
    """Dibuja los puntos ingresados aunque la sección aún no se pueda calcular."""
    fig = go.Figure(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="lines+markers+text", text=[str(i + 1) for i in range(len(pts))],
                               textposition="top center", line=dict(color=MAR, width=3), marker=dict(size=9, color=ORO)))
    fig.update_layout(title="Vista previa de los puntos ingresados", height=420, plot_bgcolor="#faf8f3", paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      dragmode="pan", margin=dict(l=40, r=40, t=60, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal (m)", gridcolor="#e8e5dc"), yaxis=dict(title="Elevación (m)", gridcolor="#e8e5dc", scaleanchor="x"))
    return fig


def dib(s, y, H, mats, ns):
    if isinstance(s, (mh.Circular, mh.Parabolica)): return dibujar_cerrada(s, y, H, mats)
    return dibujar_poli(s, y, H) if isinstance(s, mh.Poligonal) else dibujar(s, y, H, mats, ns)


def _agregar(clave):
    f = st.session_state[clave]; u = dict(f[-1]); u["id"] = max(r["id"] for r in f) + 1
    if clave == "filas_xy": u["a"] = u["a"] + 0.5
    f.append(u)


def _eliminar(clave, ident):
    st.session_state[clave] = [r for r in st.session_state[clave] if r["id"] != ident]


def _restablecer(clave):
    st.session_state.pop(clave, None)


def _cambio_material(clave, ident):
    st.session_state[f"{clave}_n_{ident}"] = mh.MATERIALES[st.session_state[f"{clave}_m_{ident}"]][0]


def tabla_seccion(tipo):
    """Sección por filas editables (punto o tramo, con su material y n). Devuelve (puntos, materiales, n por tramo, errores)."""
    xy = tipo == "Por coordenadas (X, Y)"
    clave, minimo = ("filas_xy", 3) if xy else ("filas_ang", 2)
    MATL, CON = list(mh.MATERIALES), "Concreto (acabado con llana)"
    if clave not in st.session_state:
        base = [(0.0, 1.0), (0.5, 0.0), (1.5, 0.0), (2.0, 1.0)] if xy else [(1.414, -45.0), (1.0, 0.0), (1.414, 45.0)]
        st.session_state[clave] = [dict(id=i, a=p[0], b=p[1], mat=CON, n=0.013) for i, p in enumerate(base)]
    filas = st.session_state[clave]
    st.caption("Ingresa los puntos de izquierda a derecha. El material y el n de cada fila son los del tramo que sigue a ese punto." if xy else
               "Ingresa los tramos de izquierda a derecha, desde el punto (0, 0). El ángulo va de −90° a 90°: positivo sube y negativo baja.")
    for i, r in enumerate(filas):
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 5, 2], vertical_alignment="bottom")
            k = f"{clave}_%s_{r['id']}"
            if xy:
                r["a"] = c1.number_input(f"X (m) | punto {i + 1}", value=float(r["a"]), step=0.1, format="%.2f", key=k % "a")
                r["b"] = c2.number_input("Y (m)", value=float(r["b"]), step=0.1, format="%.2f", key=k % "b")
            else:
                r["a"] = c1.number_input(f"Longitud (m) | tramo {i + 1}", min_value=0.01, value=max(float(r["a"]), 0.01), step=0.1, format="%.4f", key=k % "a")
                r["b"] = c2.number_input("Ángulo (°)", min_value=-90.0, max_value=90.0, value=float(r["b"]), step=5.0, format="%.1f", key=k % "b")
            c3.button("🗑", key=k % "del", on_click=_eliminar, args=(clave, r["id"]), disabled=len(filas) <= minimo, help="Eliminar esta fila")
            if xy and i == len(filas) - 1:
                st.caption("Último punto: no inicia ningún tramo.")
            else:
                m1, m2 = st.columns([3, 2])
                r["mat"] = m1.selectbox("Material del tramo", MATL, index=MATL.index(r["mat"]), key=k % "m", on_change=_cambio_material, args=(clave, r["id"]))
                r["n"] = m2.number_input("n", min_value=0.001, step=0.001, format="%.4f", key=k % "n", **({} if (k % "n") in st.session_state else {"value": float(r["n"])}))
    b1, b2 = st.columns(2)
    b1.button("➕ Agregar punto" if xy else "➕ Agregar tramo", key=clave + "_add", on_click=_agregar, args=(clave,), width="stretch")
    b2.button("↺ Restablecer ejemplo", key=clave + "_reset", on_click=_restablecer, args=(clave,), width="stretch")
    errs = []
    if xy:
        orden = sorted(filas, key=lambda r: r["a"])          # estable: conserva el orden de los puntos con la misma X
        if [r["id"] for r in orden] != [r["id"] for r in filas]:
            st.caption("Los puntos se ordenaron automáticamente de izquierda a derecha (por X) para el cálculo.")
        pts = [(r["a"], r["b"]) for r in orden]; ms = [r["mat"] for r in orden[:-1]]; ns_ = [r["n"] for r in orden[:-1]]
    else:
        x = yy = 0.0; pts = [(0.0, 0.0)]
        for r in filas:
            x += r["a"] * math.cos(math.radians(r["b"])); yy += r["a"] * math.sin(math.radians(r["b"])); pts.append((x, yy))
        ms = [r["mat"] for r in filas]; ns_ = [r["n"] for r in filas]
    if any(pts[i + 1][0] < pts[i][0] - 1e-9 for i in range(len(pts) - 1)):
        errs.append("Los puntos deben ir de izquierda a derecha (X creciente).")
    return pts, ms, ns_, errs


if st.session_state.pag == "portada":
    st.markdown("""<div class="tarjeta"><div class="sup">ANÁLISIS Y DISEÑO DE CANALES ABIERTOS</div>
<svg viewBox="0 0 340 130"><path d="M60 18 H280 L238 100 H102 Z" fill="rgba(227,179,65,.12)" stroke="#e3b341" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M80 58 q13-9 26 0 t26 0 t26 0 t26 0 t26 0 t26 0 t26 0" fill="none" stroke="#4fb3a9" stroke-width="2.5"/>
<path d="M92 76 q13-8 26 0 t26 0 t26 0 t26 0 t26 0 t26 0" fill="none" stroke="#4fb3a9" stroke-width="2" opacity=".6"/>
<rect x="20" y="104" width="300" height="9" fill="#b08a34"/></svg>
<div class="titulo">LYCANAL PRO</div><div class="barra"></div>
<div class="desc">Flujo uniforme, rugosidad compuesta, verificación de velocidad y borde libre para el diseño de canales abiertos.</div>
<div class="autor">Desarrollado por <b>Lucero Yamile Silva de la Cruz</b></div></div>""", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1, 1])
    if c.button("Ingresar al sistema", width="stretch"):
        st.session_state.pag = "menu"
        st.rerun()
    st.stop()

# ---------------- Menú de cálculos ----------------
TITULOS = {"uniforme_y": "Tirante normal", "uniforme_Q": "Caudal", "uniforme_S": "Pendiente", "critico": "Tirante crítico",
           "energia": "Energía específica", "diseno": "Diseño de sección", "compuesta": "Sección compuesta"}
MODS = [("uniforme_y", "Tirante normal", "Halla y a partir de Q, S, n y la sección."), ("uniforme_Q", "Caudal", "Halla Q a partir de y, S, n y la sección."),
        ("uniforme_S", "Pendiente", "Halla S a partir de Q, y, n y la sección."), ("critico", "Tirante crítico", "Halla yc y la pendiente crítica, con energía, borde libre y reporte."),
        ("diseno", "Diseño de sección", "Máxima eficiencia, mínima infiltración o intermedia."),
        ("compuesta", "Sección compuesta", "Rectas, arcos y parábolas, o coordenadas, divididas en subáreas.")]
if st.session_state.pag == "menu":
    st.markdown('<div class="barra-sup"><span class="titulo">LYCANAL PRO</span><small>Menú de cálculos</small></div>', unsafe_allow_html=True)
    st.markdown("### ¿Qué deseas calcular?")
    for i in range(0, len(MODS), 3):
        for col, (clave, tit, desc) in zip(st.columns(3), MODS[i:i + 3]):
            col.markdown(f'<div class="mod{"" if clave else " off"}"><h4>{tit}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
            if col.button("Abrir", key="mod_" + (clave or tit), disabled=not clave, width="stretch"):
                st.session_state.modulo = clave; st.session_state.pag = "app"; st.rerun()
    if st.button("← Portada"):
        st.session_state.pag = "portada"; st.rerun()
    st.stop()

modulo = st.session_state.modulo

# ---------------- Sistema ----------------
st.markdown(f'<div class="barra-sup"><span class="titulo">LYCANAL PRO</span><small>{TITULOS[modulo]}</small></div>', unsafe_allow_html=True)
proyecto = modulo_energia.datos_proyecto()
izq, der = st.columns([1, 1.9], gap="large")
der.markdown('<div class="ancla-der"></div>', unsafe_allow_html=True)
seg_tr_ = None
Dc, Tpar, Hpar = 1.0, 1.0, 0.6
pts_ = ms_ = ns_ = None
err_poly = []
POLI = False
SUBAREAS = False
cortes_ = []
cortes_h_ = []
corte_pm = False
n_u = nf = nw = nwi = nwd = 0.013
k1 = k2 = k3 = k4 = 0.0
k5 = 1.0

with izq:
    if modulo == "compuesta":
        _op = {"Tirante normal": "Tirante normal (y)", "Caudal": "Caudal (Q)", "Pendiente": "Pendiente (S)", "Tirante crítico": "Tirante crítico (yc)"}
        inc = _op[st.selectbox("¿Qué calcular?", list(_op))]
    else:
        inc = {"uniforme_Q": "Caudal (Q)", "uniforme_S": "Pendiente (S)", "critico": "Tirante crítico (yc)"}.get(modulo, "Tirante normal (y)")

    st.markdown("### 🌊 Sección del canal")
    if modulo == "compuesta":
        tipo = "Sección compuesta"
        modo_ing = st.radio("Cómo ingresar la sección", ["Por tramos (rectas, arcos y parábolas)", "Por coordenadas (X, Y)"])
    else:
        tipo = st.selectbox("Tipo", ["Rectangular", "Trapezoidal", "Triangular", "Circular"] if modulo == "diseno" else
                            ["Rectangular", "Trapezoidal", "Triangular", "Circular", "Parabólica", "Por coordenadas (X, Y)", "Por ángulos y tramos"])
    POLI = tipo in ("Por coordenadas (X, Y)", "Por ángulos y tramos", "Sección compuesta")
    FORMA = tipo in ("Circular", "Parabólica")
    b = st.number_input("Ancho de solera b (m)", 0.0, value=0.8, step=0.1, format="%.4f") if (tipo != "Triangular" and modulo != "diseno" and not POLI and not FORMA) else 0.0
    z = st.number_input("Talud z (H:V)", 0.0, value=1.0, step=0.25, format="%.4f") if (tipo != "Rectangular" and not POLI and not FORMA) else 0.0
    if tipo == "Circular" and modulo != "diseno":
        Dc = st.number_input("Diámetro D (m)", 0.0, value=1.0, step=0.1, format="%.4f")
    if tipo == "Parabólica":
        Tpar = st.number_input("Espejo de agua T (m), a la altura H", 0.0, value=1.0, step=0.1, format="%.4f")
        Hpar = st.number_input("Altura de la sección H (m)", 0.0, value=0.6, step=0.1, format="%.4f")
        if Tpar > 0 and Hpar > 0: st.caption(f"Foco de la parábola: k = T²/(16·H) = {Tpar ** 2 / (16 * Hpar):.4f} m")
    if POLI:
        junc = None
        if modulo == "compuesta" and modo_ing.startswith("Por tramos"):
            pts_, ms_, ns_, err_poly, junc, seg_tr_ = tabla_compuesta()
        else:
            pts_, ms_, ns_, err_poly = tabla_seccion("Por coordenadas (X, Y)" if modulo == "compuesta" else tipo)
        if modulo == "compuesta":
            cand = junc if junc is not None else list(range(1, len(pts_) - 1))
            st.markdown("### Método de cálculo")
            SUBAREAS = st.radio("Método de cálculo", ["Horton-Einstein (un solo n equivalente)", "División en subáreas (cada una con su n, Q = ΣQᵢ)"]).startswith("División")
            if SUBAREAS and not err_poly:
                forma = st.radio("Forma de dividir", ["Automática", "Manual"], horizontal=True)
                if forma == "Automática":
                    crit_c = st.selectbox("Criterio de corte", ["Cambio de material (n)", "Cambio de pendiente de las paredes", "En cada unión de tramos (o punto)"])
                    cortes_ = mh.cortes_auto(pts_, ns_, ms_, crit_c, cand if junc is not None else None)
                else:
                    etq = {k: (f"Unión de los tramos {j + 1} y {j + 2} (x = {pts_[k][0]:.2f} m)" if junc is not None else f"Punto {k + 1} (x = {pts_[k][0]:.2f} m)") for j, k in enumerate(cand)}
                    cortes_ = st.multiselect("Cortes verticales: puntos donde se corta", cand, format_func=lambda k: etq[k])
                    zs_ = [q[1] for q in pts_]
                    st.caption(f"Cortes horizontales: la cota (Y) de la sección va de {min(zs_):.2f} a {max(zs_):.2f} m.")
                    sel_h = st.multiselect("Cortes horizontales: a la cota de estos puntos", cand, format_func=lambda k: f"Punto {k + 1} (cota = {pts_[k][1]:.2f} m)")
                    extra_h = st.text_input("Otras cotas de corte horizontal (m), separadas por coma", value="")
                    otras = []
                    for tk in extra_h.replace(";", ",").split(","):
                        try: otras.append(float(tk))
                        except ValueError: pass
                    cortes_h_ = sorted({pts_[k][1] for k in sel_h} | set(otras))
                corte_pm = st.checkbox("Contar los cortes como perímetro mojado", value=False)
                st.caption(f"Se forman hasta {(len(cortes_) + 1) * (len(cortes_h_) + 1)} subárea(s). Los cortes verticales pasan por los puntos indicados y los horizontales siguen la cota indicada.")
    crit_d = None
    if modulo == "diseno":
        if tipo == "Triangular": st.caption("En sección triangular la máxima eficiencia se logra con z = 1 (θ = 45°); no hay ancho de solera que dimensionar.")
        elif tipo == "Circular": st.caption("En la sección circular la máxima eficiencia hidráulica es el semicírculo (y = D/2). La mínima infiltración y la intermedia solo se definen para secciones rectangulares y trapezoidales.")
        else: crit_d = st.selectbox("Criterio de diseño", list(mh.FACTORES))

    st.markdown("### Rugosidad")
    MAT = list(mh.MATERIALES)

    def material(etq, defecto, clave):
        mt = st.selectbox(etq, MAT, index=MAT.index(defecto), key="m_" + clave)
        return mt, st.number_input(f"n de {etq.lower().replace('material de ', '')}", 0.0, value=mh.MATERIALES[mt][0], step=0.001,
                                   format="%.4f", key=f"n_{clave}_{mt}")
    op = ["Un solo material", "Fondo y paredes distintos", "Fondo y cada pared distintos"] if tipo != "Triangular" \
        else ["Un solo material", "Cada pared distinta"]
    modo_txt = st.radio("Materiales del canal", op) if not (POLI or FORMA) else op[0]
    modo = 0 if modo_txt == op[0] else (1 if modo_txt == "Fondo y paredes distintos" else 2)
    if tipo == "Triangular" and modo == 1: modo = 2
    CON = "Concreto (acabado con llana)"
    mf = mi = md = CON
    if POLI:
        modo = 3
        st.caption("Los materiales y los n de cada tramo se toman de la tabla de la sección.")
    elif modo == 0:
        mf, n_u = material("Material del canal", CON, "u"); mi = md = mf
    else:
        if tipo != "Triangular":
            mf, nf = material("Material del fondo", CON, "f")
        if modo == 1:
            mi, nw = material("Material de las paredes", "Mampostería de piedra", "w"); md = mi; nwi = nwd = nw
        else:
            mi, nwi = material("Material de la pared izquierda", "Mampostería de piedra", "i")
            md, nwd = material("Material de la pared derecha", "Tierra", "d")
        if tipo == "Triangular": mf = mi
        st.caption("Se combinan con Horton-Einstein, ponderando por perímetro mojado.")
    st.caption("Los n sugeridos son valores típicos referenciales; puedes escribir el que necesites.")
    cow_on = st.checkbox("Hay irregularidades (Cowan)")
    if cow_on:
        st.markdown(tabla_cowan(), unsafe_allow_html=True)
        st.caption("Tabla de guía: puedes escribir cualquier valor, aunque esté fuera del rango.")
        a, c_, d = st.columns(3)
        k1 = a.number_input("n1", value=0.0, step=0.001, format="%.4f"); k2 = c_.number_input("n2", value=0.0, step=0.001, format="%.4f")
        k3 = d.number_input("n3", value=0.0, step=0.001, format="%.4f")
        e, f_ = st.columns(2)
        k4 = e.number_input("n4", value=0.0, step=0.001, format="%.4f"); k5 = f_.number_input("m5", value=1.0, step=0.01, format="%.4f")

    st.markdown("### 💧 Datos hidráulicos")
    Q = S = y = None
    if inc != "Caudal (Q)":
        q1, q2 = st.columns([2, 1])
        Qv = q1.number_input("Caudal Q", 0.0, value=300.0, format="%.4f")
        unidad_q = q2.selectbox("Unidad Q", ["L/s", "m³/s", "ft³/s"], key="unidad_caudal_principal")
        factores_q = {"L/s": 0.001, "m³/s": 1.0, "ft³/s": 0.028316846592}
        Q = Qv * factores_q[unidad_q]
        st.caption(f"Caudal convertido internamente: {Q:.4f} m³/s")
    if inc not in ("Pendiente (S)", "Tirante crítico (yc)"):
        s1, s2 = st.columns([2, 1])
        Sv = s1.number_input("Pendiente S", 0.0, value=1.5, format="%.4f")
        S = Sv / {"%": 100, "m/m": 1, "‰": 1000}[s2.selectbox("Unidad S", ["%", "m/m", "‰"])]
    if inc not in ("Tirante normal (y)", "Tirante crítico (yc)"):
        y = st.number_input("Tirante y (m)", 0.0, value=0.2, format="%.4f")

    metodo_sol, p_met = "Manning", 0.0
    if True:
        st.markdown("### Método de solución")
        metodo_sol = st.selectbox("Fórmula", ["Manning", "Chezy", "Bazin", "Ganguillet-Kutter"], key="msol")
        if metodo_sol == "Chezy": p_met = st.number_input("Coeficiente C de Chezy", 0.0, value=50.0, format="%.2f")
        if metodo_sol == "Bazin": p_met = st.number_input("Coeficiente γ de Bazin", 0.0, value=0.16, format="%.4f")
        if metodo_sol.startswith("Gang"): st.caption("Fórmula de Kutter válida para S ≥ 0.0005 (Villón).")
    st.markdown("### Verificación de velocidad")
    v1, v2 = st.columns(2)
    vmin = v1.number_input("Vmín (m/s)", 0.0, value=0.6, format="%.2f")
    vmax = v2.number_input("Vmáx (m/s)", 0.0, value=3.0, format="%.2f")

    st.markdown("### Energía específica")
    en_on = st.checkbox("Calcular la energía específica", value=True)
    st.markdown("### Borde libre")
    bl_man = 0.3
    if tipo == "Circular":
        metodo = "Borde libre geométrico (D − y)"
        st.info("En una sección circular no se aplica el borde libre empírico de canales abiertos: se calcula como la altura libre interior, BL = D − y.")
    else:
        with st.expander("Tabla guía de métodos de borde libre", expanded=True):
            st.markdown(tabla_bl(), unsafe_allow_html=True)
            st.caption("Valores en metros. Las tablas por caudal y por ancho de solera son referenciales.")
        ops_bl = mh.METODOS_BL if tipo in ("Rectangular", "Trapezoidal") else [m_ for m_ in mh.METODOS_BL if m_ != "Villón por ancho de solera"]
        metodo = st.selectbox("Método de borde libre", ops_bl)
        if metodo == "Valor manual":
            bl_man = st.number_input("Borde libre BL (m)", 0.0, value=0.3, step=0.05, format="%.4f")
        st.caption("Elijas el método que elijas, los resultados muestran la comparación entre todos.")
    if st.button("← Menú de cálculos"):
        st.session_state.pag = "menu"
        st.rerun()

# ---------------- Cálculo ----------------
if modulo == "diseno":
    b = 0.5   # provisional: el ancho se dimensiona más abajo
if POLI and not err_poly and SUBAREAS:
    s = mh.Compuesta(pts_, ns_, ms_, cortes_, corte_pm, (lambda n0: mh.cowan(n0, k1, k2, k3, k4, k5)) if cow_on else None, seg_tr_, cortes_h_)
elif POLI and not err_poly:
    s = mh.Poligonal(pts_, ns_, ms_)
elif tipo == "Circular":
    s = mh.Circular(max(Dc, 1e-6))
elif tipo == "Parabólica":
    s = mh.Parabolica(max(Tpar, 1e-6), max(Hpar, 1e-6))
else:
    s = mh.Seccion("Rectangular" if POLI else tipo, b, z)
errs = list(err_poly)
if tipo == "Circular" and Dc <= 0: errs.append("El diámetro debe ser mayor que 0.")
if tipo == "Parabólica" and (Tpar <= 0 or Hpar <= 0): errs.append("El espejo de agua T y la altura H deben ser mayores que 0.")
if tipo != "Triangular" and not POLI and not FORMA and b <= 0: errs.append("El ancho de solera debe ser mayor que 0.")
if inc != "Caudal (Q)" and Q <= 0: errs.append("El caudal debe ser mayor que 0.")
if inc not in ("Pendiente (S)", "Tirante crítico (yc)") and S <= 0: errs.append("La pendiente debe ser mayor que 0.")
if inc not in ("Tirante normal (y)", "Tirante crítico (yc)") and y <= 0: errs.append("El tirante debe ser mayor que 0.")


def partes(yy):
    if POLI: return s.partes(yy)
    p = [(s.b, nf)] if s.b > 0 else []
    return p + ([(s.paredes(yy), nw)] if modo == 1 else [(s.lado(yy), nwi), (s.lado(yy), nwd)])


n_base = (lambda yy: n_u) if modo == 0 else (lambda yy: mh.horton(partes(yy)))
nfun = (lambda yy: mh.cowan(n_base(yy), k1, k2, k3, k4, k5)) if cow_on else n_base
mats = (mf, mi, md)
ns = None if modo in (0, 3) else (nf, nwi, nwd)

_tabs = der.tabs(["Sección", "Resultados"] + (["Energía"] if en_on else []) + ["Procedimiento"])
tab_sec, tab_res, tab_proc = _tabs[0], _tabs[1], _tabs[-1]
tab_en = _tabs[2] if en_on else None

if errs:
    with tab_sec:
        for e in errs: st.error(e)
        if POLI and pts_ and len(pts_) >= 2:
            st.plotly_chart(vista_previa(pts_), theme=None, config=CONFIG)
        yp = y if y else 0.5
        if s.b > 0 or s.z > 0:
            st.plotly_chart(dib(s, yp, yp * 1.3, mats, ns), theme=None, config=CONFIG)
    st.stop()

it = None
if modulo == "diseno" and tipo == "Circular":
    def _q_dis(D):
        global s
        s = mh.Circular(D)
        return mh.q_flujo(s, nfun, S, D / 2, metodo_sol, p_met) - Q
    hi_ = 1.0
    while _q_dis(hi_) < 0 and hi_ < 1e4: hi_ *= 2
    Dc, _ = mh.biseccion(_q_dis, 1e-6, hi_)
    s = mh.Circular(Dc)
if modulo == "diseno" and tipo not in ("Triangular", "Circular"):
    m_d = mh.FACTORES[crit_d] * (math.sqrt(1 + z * z) - z)

    def _q_dis(yy):
        global s
        s = mh.Seccion(tipo, m_d * yy, z)
        return mh.q_flujo(s, nfun, S, yy, metodo_sol, p_met) - Q
    hi_ = 1.0
    while _q_dis(hi_) < 0 and hi_ < 1e4: hi_ *= 2
    y_d, _ = mh.biseccion(_q_dis, 1e-6, hi_)
    b = m_d * y_d
    s = mh.Seccion(tipo, b, z)
if inc == "Tirante normal (y)": y, it = mh.tirante_normal(s, nfun, S, Q, metodo_sol, p_met)
elif inc == "Caudal (Q)": Q = mh.q_flujo(s, nfun, S, y, metodo_sol, p_met)
elif inc == "Tirante crítico (yc)":
    y = mh.tirante_critico(s, Q)
    S = mh.pendiente(s, nfun, Q, y, metodo_sol, p_met)
else: S = mh.pendiente(s, nfun, Q, y, metodo_sol, p_met)

if (inc == "Tirante normal (y)" and Q > mh.q_flujo(s, nfun, S, y, metodo_sol, p_met) * (1 + 1e-4)) or \
        (inc == "Tirante crítico (yc)" and getattr(s, "ymax", None) and s.A(y) ** 3 / s.T(y) < Q ** 2 / mh.G * (1 - 1e-4)):
    with tab_sec:
        st.error("El caudal supera la capacidad de la sección: no existe un tirante dentro de su altura que lo conduzca.")
        st.plotly_chart(dib(s, y, y, mats, ns), theme=None, config=CONFIG)
    st.stop()
if getattr(s, "altura", None) is not None and y > s.altura + 1e-9:
    with tab_sec:
        st.error(f"El tirante ({y:.4f} m) supera la altura de la sección ({s.altura:.4f} m): el agua se desbordaría.")
        st.plotly_chart(dib(s, y, y, mats, ns), theme=None, config=CONFIG)
    st.stop()
A, P, T = s.A(y), s.P(y), s.T(y)
R, V, n = A / P, Q / A, nfun(y)
if SUBAREAS:
    n = A * R ** (2 / 3) * math.sqrt(S) / Q                 # n equivalente (Manning) de toda la sección
ORIGEN = "Subáreas: n equivalente global (referencial)" if SUBAREAS else ("Valor directo" if modo == 0 else "Horton-Einstein") + (" + Cowan" if cow_on else "")
F, yc = mh.froude(s, Q, y), mh.tirante_critico(s, Q)
reg, msg_reg = mh.regimen(F)
est, msg_v = mh.verificar_velocidad(V, vmin, vmax)
rev = all(mt in ("Concreto (acabado con llana)", "Concreto (sin acabado)", "Mampostería de piedra") for mt in (s.mats if POLI else mats))
C = mh.c_usbr(Q)
bt = s.b if tipo in ("Rectangular", "Trapezoidal") else 0.0
if isinstance(s, mh.Circular):
    BL = max(0.0, s.D - y)
    f_bl = f"BL = D − y = {s.D:.4f} − {y:.4f}"
    crit = "Borde libre geométrico interior de la sección circular: diámetro menos tirante."
    comp = []
else:
    BL, f_bl, crit = mh.borde_libre(metodo, y, Q, rev, bl_man, bt)
    comp = mh.comparar_bl(y, Q, rev, bt)
E = y + V ** 2 / (2 * mh.G)
Ec = mh.energia(s, Q, yc)
y2 = mh.y_alterno(s, Q, y)
y2t = f"{y2:.4f} m" if y2 is not None else "No existe"
FIJA = getattr(s, "altura", None) is not None          # sección con altura propia: el borde libre disponible es altura − y
BLd = (s.altura - y) if FIJA else None
origen = ("" if modo == 0 else " (Horton)") + (" (Cowan)" if cow_on else "")

with tab_sec:
    st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
    st.plotly_chart(dib(s, y, y + BL, mats, ns), theme=None, config=CONFIG)
    if FIJA: st.caption("Línea azul punteada: borde superior de la sección. Línea dorada: nivel y + borde libre requerido.")

def tarjetas(items):
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (t, v) in zip(cols, items[i:i + 3]):
            col.metric(t, v)


with tab_res:
    pdf_slot = st.container()
    st.markdown('<div class="grupo" style="margin-top:6px">Resultado principal</div>', unsafe_allow_html=True)
    tarjetas([("Tirante crítico yc" if inc == "Tirante crítico (yc)" else "Tirante normal y", f"{y:.4f} m"), ("Caudal Q", f"{Q:.4f} m³/s"), ("Pendiente crítica Sc" if inc == "Tirante crítico (yc)" else "Pendiente S", formato_pendiente(S))] + ([("Ancho de solera b", f"{s.b:.4f} m")] if (modulo == "diseno" and tipo not in ("Triangular", "Circular")) else [("Diámetro D", f"{s.D:.4f} m")] if (modulo == "diseno" and tipo == "Circular") else []))
    st.markdown('<div class="grupo">Geometría del flujo</div>', unsafe_allow_html=True)
    tarjetas([("Área A", f"{A:.4f} m²"), ("Perímetro mojado P", f"{P:.4f} m"), ("Espejo de agua T", f"{T:.4f} m"),
              ("Radio hidráulico R", f"{R:.4f} m"), ("Profundidad hidráulica A/T", f"{A / T:.4f} m")])
    st.markdown('<div class="grupo">Rugosidad</div>', unsafe_allow_html=True)
    tarjetas([("n usada", f"{n:.4f}"), ("Origen", ORIGEN)])
    st.markdown('<div class="grupo">Velocidad y régimen</div>', unsafe_allow_html=True)
    tarjetas([("Velocidad V", f"{V:.4f} m/s"), ("Número de Froude F", f"{F:.4f}"), ("Régimen", reg),
              ("Tirante crítico yc", f"{yc:.4f} m")])
    st.write("")
    (st.success if est == "ok" else st.warning)(msg_v)
    av = mh.validar_pendiente(S)
    if av: st.warning(av)
    st.info(msg_reg)
    if en_on:
        st.markdown('<div class="grupo">Energía específica</div>', unsafe_allow_html=True)
        tarjetas([("Energía específica E", f"{E:.4f} m"), ("Energía mínima Emín", f"{Ec:.4f} m"), ("Tirante alterno y₂", y2t)])
    st.markdown('<div class="grupo">Borde libre</div>', unsafe_allow_html=True)
    if isinstance(s, mh.Circular):
        tarjetas([("Diámetro interior D", f"{s.D:.4f} m"), ("Tirante y", f"{y:.4f} m"), ("Borde libre geométrico D − y", f"{BL:.4f} m")])
        st.latex(rf"BL=D-y={s.D:.4f}-{y:.4f}={BL:.4f}\ \mathrm{{m}}")
        st.caption(crit)
    elif FIJA:
        tarjetas([("BL requerido (método elegido)", f"{BL:.4f} m"), ("BL disponible = altura − y", f"{BLd:.4f} m"), ("Altura de la sección", f"{s.altura:.4f} m"), ("Altura mínima necesaria = y + BL", f"{y + BL:.4f} m")])
        (st.success if BLd >= BL - 1e-9 else st.warning)(
            f"Cumple: el borde libre disponible ({BLd:.4f} m) es mayor o igual al requerido ({BL:.4f} m)." if BLd >= BL - 1e-9 else
            f"No cumple: el borde libre disponible ({BLd:.4f} m) es menor que el requerido ({BL:.4f} m). Conviene aumentar la altura de la sección o reducir el tirante.")
        if BLd > 1.25 * BL:
            st.info(f"Hay altura de más: la sección es {s.altura - (y + BL):.4f} m más alta de lo necesario.")
        st.caption("Criterio aplicado: " + crit)
    else:
        tarjetas([("Borde libre BL", f"{BL:.4f} m"), ("Altura total H = y + BL", f"{y + BL:.4f} m"), ("BL como % de y", f"{100 * BL / y:.1f} %")])
        st.caption("Criterio aplicado: " + crit)
    if not isinstance(s, mh.Circular):
        if metodo.startswith("USBR") and Q > 85: st.warning("El caudal supera los 85 m³/s: el USBR queda fuera de su rango.")
        st.markdown("##### Comparación de métodos de borde libre")
        filas_c = ""
        for m_, b_, c_ in comp:
            sel = m_ == metodo
            celdas = "<td class='na'>No aplica</td><td class='na'>-</td>" if b_ is None else f"<td class='v'>{b_:.4f}</td><td class='v'>{y + b_:.4f}</td>"
            filas_c += f"<tr class='{'sel' if sel else ''}'><td>{'✓ ' if sel else ''}{m_}</td>{celdas}<td>{c_}</td></tr>"
        st.markdown("<table class='cw'><tr><th>Método</th><th>BL (m)</th><th>H = y + BL (m)</th><th>Criterio</th></tr>" + filas_c + "</table>", unsafe_allow_html=True)
        st.caption("✓ marca el método elegido.")


if en_on:
    with tab_en:
        st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
        st.plotly_chart(modulo_energia.curva(s, Q, y, yc, y2), theme=None, config=CONFIG)
        if y2 is None:
            st.info(f"Para E = {E:.4f} m no existe un tirante alterno dentro de la altura de la sección (la energía supera la que tiene con la sección llena). El mínimo de energía ocurre en el tirante crítico yc = {yc:.4f} m.")
        else:
            st.info(f"Para E = {E:.4f} m existen dos tirantes: y = {y:.4f} m ({reg.lower()}) y y₂ = {y2:.4f} m "
                    f"({'supercrítico' if y2 < yc else 'subcrítico'}). El mínimo de energía ocurre en el tirante crítico yc = {yc:.4f} m.")


def _paso(num, titulo):
    st.markdown(f'<div class="paso"><span class="num">{num}</span>{titulo}</div>', unsafe_allow_html=True)


def _res(txt, tono=""):
    st.markdown(f'<div class="res {tono}">{txt}</div>', unsafe_allow_html=True)


with tab_proc:
    st.markdown('<div class="grupo" style="margin-top:6px">Memoria de cálculo</div>', unsafe_allow_html=True)

    if modulo == "diseno" and tipo == "Circular":
        with st.container(border=True):
            _paso("D", "Dimensionamiento de la sección")
            st.latex(r"y=\frac{D}{2}\qquad A=\frac{\pi D^2}{8}\qquad P=\frac{\pi D}{2}\qquad R=\frac{D}{4}")
            st.caption("La sección circular de máxima eficiencia hidráulica es el semicírculo. Se busca el diámetro D para el que Q(D, y = D/2) iguale al caudal de diseño, por bisección.")
            _res(f"D = {s.D:.4f} m | y = {y:.4f} m (semicírculo)")
    if modulo == "diseno" and tipo not in ("Triangular", "Circular"):
        with st.container(border=True):
            _paso("D", "Dimensionamiento de la sección")
            st.latex(r"\frac{b}{y}=f\,(\sqrt{1+z^2}-z)\qquad f=2\ (\mathrm{MEH}),\ 4\ (\mathrm{MI}),\ 3\ (\text{intermedia})")
            st.latex(rf"\frac{{b}}{{y}}={mh.FACTORES[crit_d]}\,(\sqrt{{1+{z:.4f}^2}}-{z:.4f})={m_d:.4f}")
            st.caption("Se busca el tirante y para el que Q(y, b = m·y) iguale al caudal de diseño, por bisección, con el método y la rugosidad elegidos.")
            _res(f"y = {y_d:.4f} m | b = {s.b:.4f} m ({crit_d})")
    with st.container(border=True):
        _paso(1, "Datos del problema")
        st.markdown(f"- Sección **{tipo.lower()}**" + (f", b = {s.b:.4f} m" if s.b > 0 else "") + (f", z = {s.z:.4f}" if s.z > 0 else "") + (f", D = {Dc:.4f} m" if tipo == "Circular" else "") + (f", T = {Tpar:.4f} m, H = {Hpar:.4f} m" if tipo == "Parabólica" else "")
                    + f"\n- Caudal Q = {Q:.4f} m³/s (en SI) | Pendiente S = {formato_pendiente(S)}\n- Incógnita: {inc.split(' (')[0].lower()}")

    with st.container(border=True):
        _paso(2, "Rugosidad")
        if SUBAREAS:
            st.markdown("Cada subárea tiene su propio n (Horton dentro de la subárea" + (", corregido con Cowan" if cow_on else "") + "). Los cortes " + ("sí" if corte_pm else "no") + " cuentan como perímetro mojado.")
            _d = mh.detalle_subareas(s, y, S, metodo_sol, p_met)
            st.table(pd.DataFrame([(d["nombre"], d["tramos"], f"{d['A']:.4f}", f"{d['P']:.4f}", f"{d['n']:.4f}", f"{d['R']:.4f}") for d in _d],
                                  columns=["Subárea", "Tramos", "A (m²)", "P (m)", "n", "R (m)"]).set_index("Subárea"))
        if modo == 0 and not cow_on:
            st.markdown(f"Material: **{mats[0]}**, con n tomado directamente.")
        if modo and not SUBAREAS:
            if POLI:
                det = s.detalle(y); nombres = [d[0] for d in det]; pts = [(d[1], d[2]) for d in det]
            else:
                nombres = (["Fondo"] if s.b > 0 else []) + (["Paredes"] if modo == 1 else ["Pared izquierda", "Pared derecha"])
                pts = partes(y)
            suma, Pt = sum(p * nn ** 1.5 for p, nn in pts), sum(p for p, _ in pts)
            st.latex(r"n_e=\left(\frac{\sum P_i\,n_i^{3/2}}{P}\right)^{2/3}")
            st.table(pd.DataFrame([(nm, f"{p:.4f}", f"{nn:.4f}", f"{p * nn ** 1.5:.4f}") for nm, (p, nn) in zip(nombres, pts)],
                                  columns=["Parte", "Pᵢ (m)", "nᵢ", "Pᵢ·nᵢ^1.5"]).set_index("Parte"))
            st.latex(rf"n_e=\left(\frac{{{suma:.4f}}}{{{Pt:.4f}}}\right)^{{2/3}}={n_base(y):.4f}")
        if cow_on and not SUBAREAS:
            st.latex(r"n=(n_0+n_1+n_2+n_3+n_4)\,m_5")
            st.latex(rf"n=({n_base(y):.4f}+{k1:.4f}+{k2:.4f}+{k3:.4f}+{k4:.4f})\times{k5:.4f}={n:.4f}")
        _res(f"n equivalente global (Manning) = {n:.4f}" if SUBAREAS else f"n = {n:.4f}" + ("" if modo == 0 and not cow_on else (" (Horton-Einstein)" if modo and not cow_on else (" (Horton + Cowan)" if modo else " (Cowan)"))))

    with st.container(border=True):
        _paso(3, f"Ecuación de {metodo_sol}")
        Cc_ = mh.coef(metodo_sol, R, S, n, p_met)
        if SUBAREAS:
            st.latex(r"Q=\sum_i Q_i\qquad " + (r"Q_i=\frac{1}{n_i}\,A_i\,R_i^{2/3}\,S^{1/2}" if metodo_sol == "Manning" else r"Q_i=C_i\,A_i\,\sqrt{R_i\,S}"))
            st.table(pd.DataFrame([(d["nombre"], f"{d['Q']:.4f}", f"{100 * d['Q'] / Q:.1f} %") for d in _d], columns=["Subárea", "Qᵢ (m³/s)", "% del caudal"]).set_index("Subárea"))
            st.latex(rf"\sum Q_i={sum(d['Q'] for d in _d):.4f}\ \mathrm{{m^3/s}}")
        else:
            FORM = {"Manning": r"C=\frac{R^{1/6}}{n}", "Chezy": r"C=\text{dato}", "Bazin": r"C=\frac{87}{1+\gamma/\sqrt{R}}",
                    "Ganguillet-Kutter": r"C=\frac{23+\frac{0.00155}{S}+\frac{1}{n}}{1+\left(23+\frac{0.00155}{S}\right)\frac{n}{\sqrt{R}}}"}
            if metodo_sol == "Manning":
                st.latex(r"Q=\frac{1}{n}\,A\,R^{2/3}\,S^{1/2}")
                st.latex(rf"{Q:.4f}=\frac{{1}}{{{n:.4f}}}\,({A:.4f})\,({R:.4f})^{{2/3}}\,({S:.6f})^{{1/2}}")
            else:
                st.latex(FORM[metodo_sol] + r"\qquad Q=C\,A\,\sqrt{R\,S}")
                st.latex(rf"C={Cc_:.4f}\qquad {Q:.4f}={Cc_:.4f}\,({A:.4f})\sqrt{{({R:.4f})({S:.6f})}}")
        if inc == "Tirante crítico (yc)":
            st.caption("Primero se halla el tirante crítico con Q²/g = Ac³/Tc; luego la pendiente crítica con la ecuación anterior.")
            _res(f"Tirante crítico yc = {y:.4f} m  |  Pendiente crítica Sc = {formato_pendiente(S)}")
        elif inc == "Pendiente (S)": _res(f"S = {formato_pendiente(S)}")
        elif it:
            st.caption("El tirante se halla por bisección, hasta que el intervalo sea menor que 0.000001 m.")
            _res(f"y = {y:.4f} m | {len(it)} iteraciones")
        else: _res(f"Q = {Q:.4f} m³/s")
        if it:
            with st.expander("Ver tabla de iteraciones"):
                st.dataframe(pd.DataFrame(it).rename(columns={"i": "Iteración", "y": "y (m)", "error": "Error (m)"}).set_index("Iteración")
                             .style.format({"y (m)": "{:.6f}", "Error (m)": "{:.2e}"}), width="stretch")

    with st.container(border=True):
        _paso(4, "Elementos geométricos")
        if tipo == "Circular":
            th = 2 * math.acos(max(-1.0, min(1.0, 1 - 2 * y / Dc)))
            g = rf"\theta=2\arccos\left(1-\frac{{2y}}{{D}}\right)={th:.4f}\ \mathrm{{rad}}\\A=\frac{{D^2}}{{8}}(\theta-\sin\theta)={A:.4f}\ \mathrm{{m^2}}\\P=\frac{{D\,\theta}}{{2}}={P:.4f}\ \mathrm{{m}}\\T=D\sin\frac{{\theta}}{{2}}={T:.4f}\ \mathrm{{m}}"
        elif tipo == "Parabólica":
            g = rf"T=T_0\sqrt{{y/H}}={T:.4f}\ \mathrm{{m}}\\A=\frac{{2}}{{3}}\,T\,y={A:.4f}\ \mathrm{{m^2}}\\P=2\left[\frac{{x}}{{2}}\sqrt{{1+4a^2x^2}}+\frac{{\operatorname{{asinh}}(2ax)}}{{4a}}\right]={P:.4f}\ \mathrm{{m}}\qquad x=\frac{{T}}{{2}},\ a=\frac{{H}}{{(T_0/2)^2}}"
        elif POLI:
            g = rf"A=\sum A_i={A:.4f}\ \mathrm{{m^2}}\\P=\sum P_i={P:.4f}\ \mathrm{{m}}\\T=\sum T_i={T:.4f}\ \mathrm{{m}}"
        elif tipo == "Rectangular":
            g = rf"A=b\,y={b:.4f}\times{y:.4f}={A:.4f}\ \mathrm{{m^2}}\\P=b+2y={b:.4f}+2({y:.4f})={P:.4f}\ \mathrm{{m}}\\T=b={T:.4f}\ \mathrm{{m}}"
        elif tipo == "Trapezoidal":
            g = rf"A=(b+zy)\,y=({b:.4f}+{z:.4f}\times{y:.4f})\times{y:.4f}={A:.4f}\ \mathrm{{m^2}}\\P=b+2y\sqrt{{1+z^2}}={P:.4f}\ \mathrm{{m}}\\T=b+2zy={T:.4f}\ \mathrm{{m}}"
        else:
            g = rf"A=z\,y^2={z:.4f}\times{y:.4f}^2={A:.4f}\ \mathrm{{m^2}}\\P=2y\sqrt{{1+z^2}}={P:.4f}\ \mathrm{{m}}\\T=2zy={T:.4f}\ \mathrm{{m}}"
        g += rf"\\R=\frac{{A}}{{P}}=\frac{{{A:.4f}}}{{{P:.4f}}}={R:.4f}\ \mathrm{{m}}\\\bar y=\frac{{A}}{{T}}={A / T:.4f}\ \mathrm{{m}}"
        st.latex(r"\begin{gathered}" + g + r"\end{gathered}")

    with st.container(border=True):
        _paso(5, "Velocidad y número de Froude")
        st.latex(rf"V=\frac{{Q}}{{A}}=\frac{{{Q:.4f}}}{{{A:.4f}}}={V:.4f}\ \mathrm{{m/s}}")
        st.latex(rf"F=\frac{{V}}{{\sqrt{{g\,A/T}}}}=\frac{{{V:.4f}}}{{\sqrt{{9.81\times{A / T:.4f}}}}}={F:.4f}")
        _res(f"F = {F:.4f} → régimen {reg.lower()}", "ok")
        st.caption(msg_reg)

    with st.container(border=True):
        _paso(6, "Tirante crítico" + (" y energía específica" if en_on else ""))
        st.latex(r"\frac{Q^2}{g}=\frac{A_c^3}{T_c}")
        if en_on:
            st.latex(rf"E=y+\frac{{V^2}}{{2g}}={y:.4f}+\frac{{{V:.4f}^2}}{{2(9.81)}}={E:.4f}\ \mathrm{{m}}")
            _res(f"Tirante crítico yc = {yc:.4f} m  |  Energía E = {E:.4f} m  |  Tirante alterno y₂ = {y2t}")
        else:
            _res(f"Tirante crítico yc = {yc:.4f} m")

    with st.container(border=True):
        _paso(7, "Verificación de velocidad")
        st.latex(rf"{vmin:.2f}\ \le\ V={V:.4f}\ \le\ {vmax:.2f}\ \mathrm{{m/s}}")
        _res(msg_v, "ok" if est == "ok" else "mal")

    with st.container(border=True):
        _paso(8, "Borde libre")
        if isinstance(s, mh.Circular):
            st.latex(rf"BL=D-y={s.D:.4f}-{y:.4f}={BL:.4f}\ \mathrm{{m}}")
            _res(f"Borde libre geométrico = D − y = {BL:.4f} m")
        elif metodo.startswith("USBR"):
            st.latex(rf"BL=\sqrt{{C\,y}}=\sqrt{{{C}\times{y:.4f}}}={BL:.4f}\ \mathrm{{m}}")
        elif metodo.startswith("Máximo"):
            d = 5 if rev else 3
            st.latex(rf"BL=\frac{{y}}{{{d}}}=\frac{{{y:.4f}}}{{{d}}}={BL:.4f}\ \mathrm{{m}}")
        if not isinstance(s, mh.Circular):
            if not (metodo.startswith("USBR") or metodo.startswith("Máximo")):
                st.markdown(f"**{f_bl}**")
            st.caption(crit)
            _res(f"BL = {BL:.4f} m | H = y + BL = {y + BL:.4f} m")


# ---------------- Reporte PDF ----------------
def datos_dibujo(s, y, H):
    if isinstance(s, (mh.Circular, mh.Parabolica)):
        per = perfil_cerrado(s)
        return dict(linea=per, agua=[_recortar(per, y)], top=H, nivel=y)
    if isinstance(s, mh.Poligonal):
        L, agua = s.zmin + y, []
        for i in range(len(s.pts) - 1):
            (x1, z1), (x2, z2) = s.pts[i], s.pts[i + 1]
            if min(z1, z2) < L:
                a, b_ = (x1, z1), (x2, z2)
                if z1 > L: a = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
                if z2 > L: b_ = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
                agua.append([a, b_, (b_[0], L), (a[0], L)])
        return dict(linea=s.pts, agua=agua, top=s.zmin + H, nivel=L)
    hb = s.b / 2; xl = hb + s.z * H; hw = hb + s.z * y
    return dict(linea=[(-xl, H), (-hb, 0), (hb, 0), (xl, H)], agua=[[(-hb, 0), (hb, 0), (hw, y), (-hw, y)]], top=H, nivel=y)


if modo:
    if POLI: det = s.detalle(y)
    else: det = [(a_, p_, n_) for a_, (p_, n_) in zip((["Fondo"] if s.b > 0 else []) + (["Paredes"] if modo == 1 else ["Pared izquierda", "Pared derecha"]), partes(y))]
else: det = []
H = y + BL
grupos = [("Resultado principal", [("Tirante crítico yc" if inc == "Tirante crítico (yc)" else "Tirante normal y", f"{y:.4f} m"), ("Caudal Q", f"{Q:.4f} m³/s"), ("Pendiente crítica Sc" if inc == "Tirante crítico (yc)" else "Pendiente S", formato_pendiente(S))] + ([("Ancho de solera b", f"{s.b:.4f} m")] if (modulo == "diseno" and tipo not in ("Triangular", "Circular")) else [("Diámetro D", f"{s.D:.4f} m")] if (modulo == "diseno" and tipo == "Circular") else [])),
          ("Geometría del flujo", [("Área A", f"{A:.4f} m²"), ("Perímetro mojado P", f"{P:.4f} m"), ("Espejo de agua T", f"{T:.4f} m"), ("Radio hidráulico R", f"{R:.4f} m"), ("Profundidad hidráulica A/T", f"{A / T:.4f} m")]),
          ("Rugosidad", [("n usada", f"{n:.4f}"), ("Origen", ORIGEN)]),
          ("Velocidad y régimen", [("Velocidad V", f"{V:.4f} m/s"), ("Número de Froude F", f"{F:.4f}"), ("Régimen", reg), ("Tirante crítico yc", f"{yc:.4f} m")]),
          *([("Energía específica", [("Energía específica E", f"{E:.4f} m"), ("Energía mínima Emín", f"{Ec:.4f} m"), ("Tirante alterno y₂", y2t)])] if en_on else []),
          ("Borde libre", [("Diámetro interior D", f"{s.D:.4f} m"), ("Tirante y", f"{y:.4f} m"), ("Borde libre geométrico D − y", f"{BL:.4f} m")] if isinstance(s, mh.Circular) else [("BL requerido", f"{BL:.4f} m"), ("BL disponible = altura − y", f"{BLd:.4f} m"), ("Altura de la sección", f"{s.altura:.4f} m"), ("Altura mínima necesaria (y + BL)", f"{y + BL:.4f} m")] if FIJA else [("Borde libre BL", f"{BL:.4f} m"), ("Altura total H = y + BL", f"{H:.4f} m"), ("BL como % de y", f"{100 * BL / y:.1f} %")])]
ctx = dict(titulo=TITULOS[modulo], tipo=tipo, dims=(f", b = {s.b:.4f} m" if s.b > 0 else "") + (f", z = {s.z:.4f}" if s.z > 0 else "") + (f", D = {Dc:.4f} m" if tipo == "Circular" else "") + (f", T = {Tpar:.4f} m, H = {Hpar:.4f} m" if tipo == "Parabólica" else ""), Q=Q, S=S, inc=inc.split(" (")[0].lower(),
           horton=det, n_base=n_base(y), cowan=(n_base(y), k1, k2, k3, k4, k5) if cow_on else None, material=mats[0] if mats else "", n=n,
           origen=ORIGEN, metodo=metodo_sol, C=Cc_, iter=len(it) if it else 0,
           y=y, A=A, P=P, T=T, R=R, V=V, F=F, reg=reg, msg_reg=msg_reg, E=E, Ec=Ec, y2=y2, y2t=y2t, yc=yc, vmin=vmin, vmax=vmax, msg_v=msg_v, bl_formula=f_bl, crit=crit, BL=BL, H=H,
           altura=(s.altura if FIJA else None), aviso=mh.validar_pendiente(S), sub=(mh.detalle_subareas(s, y, S, metodo_sol, p_met) if SUBAREAS else None), proyecto=proyecto, energia=en_on, metodo_bl=metodo, comp_bl=comp, grupos=grupos, dibujo=datos_dibujo(s, y, H),
           dims_diametro=(s.D if isinstance(s, mh.Circular) else None),
           curva_energia=(lambda ymax_curve: ([(mh.energia(s, Q, max(1e-5, yy)), max(1e-5, yy)) for yy in [ymax_curve * i / 250 for i in range(1, 251)]], [(E, y, "y"), (Ec, yc, "yc")] + ([(mh.energia(s, Q, y2), y2, "y₂")] if y2 is not None else [])))(min(max(3*yc, 1.5*y, 1.2*(y2 or 0), 0.1), getattr(s, "ymax", float("inf"))*0.999)),
           diseno=(dict(circ=True, D=s.D, y=y) if (modulo == "diseno" and tipo == "Circular") else dict(crit=crit_d, f=mh.FACTORES[crit_d], m=m_d, y=y_d, b=s.b) if (modulo == "diseno" and tipo != "Triangular") else None))
with pdf_slot:
    st.download_button("📄 Descargar reporte en PDF", data=reporte_pdf.generar(ctx), file_name="reporte_lycanal_pro.pdf", mime="application/pdf")









