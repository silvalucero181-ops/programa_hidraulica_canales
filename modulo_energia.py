import plotly.graph_objects as go
import streamlit as st
import motor_hidraulico as mh

MAR, ORO, TUR = "#0a1a3a", "#e3b341", "#4fb3a9"
CONFIG = {"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["zoom2d", "select2d", "lasso2d"]}


def curva(s, Q, y1, yc, y2):
    top = max(3 * yc, 1.5 * (y1 or 0), 1.2 * (y2 or 0))
    ys = [top * i / 300 for i in range(1, 301)]
    Ec = mh.energia(s, Q, yc)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[mh.energia(s, Q, t) for t in ys], y=ys, mode="lines", line=dict(color=MAR, width=3), name="E(y)"))
    fig.add_trace(go.Scatter(x=[0, 3 * Ec], y=[0, 3 * Ec], mode="lines", line=dict(color=ORO, width=2, dash="dash"), name="E = y"))
    pts = [(Ec, yc, f"yc = {yc:.3f} m", TUR)]
    if y1: pts += [(mh.energia(s, Q, y1), y1, f"y₁ = {y1:.3f} m", MAR), (mh.energia(s, Q, y2), y2, f"y₂ = {y2:.3f} m", "#a3203f")]
    for x, yy, t, c in pts:
        fig.add_trace(go.Scatter(x=[x], y=[yy], mode="markers+text", text=[t], textposition="middle right", marker=dict(size=11, color=c), showlegend=False))
    fig.update_layout(title="Curva de energía específica", height=500, plot_bgcolor="#faf8f3", paper_bgcolor="rgba(0,0,0,0)", dragmode="pan",
                      legend=dict(orientation="h", y=1.08), margin=dict(l=40, r=40, t=70, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Energía específica E (m)", range=[0, 3 * Ec], gridcolor="#e8e5dc"),
                      yaxis=dict(title="Tirante y (m)", range=[0, top], gridcolor="#e8e5dc"))
    return fig


def datos_proyecto():
    """Datos generales del proyecto (se conservan al cambiar de cálculo)."""
    g = st.session_state.get("_proy", {})
    with st.expander("Datos del proyecto"):
        c1, c2 = st.columns(2); c3, c4 = st.columns(2)
        d = dict(nombre=c1.text_input("Proyecto", value=g.get("nombre", ""), key="w_proy_nombre"),
                 lugar=c2.text_input("Lugar", value=g.get("lugar", ""), key="w_proy_lugar"),
                 tramo=c3.text_input("Tramo", value=g.get("tramo", ""), key="w_proy_tramo"),
                 autor=c4.text_input("Elaborado por", value=g.get("autor", ""), key="w_proy_autor"))
    st.session_state["_proy"] = d
    return d


def render(modulo, dib=None):
    ss = st.session_state
    energia = modulo == "energia"
    st.markdown(f'<div class="barra-sup"><span class="titulo">LYCANAL PRO</span><small>{"Energía específica" if energia else "Tirante crítico"}</small></div>', unsafe_allow_html=True)
    datos_proyecto()
    izq, der = st.columns([1, 1.9], gap="large")
    with izq:
        st.markdown("### Sección")
        tipo = st.selectbox("Tipo", ["Rectangular", "Trapezoidal", "Triangular"])
        b = st.number_input("Ancho de solera b (m)", 0.0, value=0.3, step=0.1, format="%.3f") if tipo != "Triangular" else 0.0
        z = st.number_input("Talud z (H:V)", 0.0, value=1.0, step=0.25, format="%.3f") if tipo != "Rectangular" else 0.0
        st.markdown("### Datos hidráulicos")
        q1, q2 = st.columns([2, 1])
        Q = q1.number_input("Caudal Q", 0.0, value=0.3, format="%.3f") * (0.001 if q2.selectbox("Unidad Q", ["m³/s", "L/s"]) == "L/s" else 1)
        y = st.number_input("Tirante y (m)", 0.0, value=0.5, format="%.3f") if energia else None
        if st.button("← Menú de cálculos"):
            ss.pag = "menu"; st.rerun()
    errs = ([] if tipo == "Triangular" or b > 0 else ["El ancho de solera debe ser mayor que 0."]) + ([] if Q > 0 else ["El caudal debe ser mayor que 0."]) \
        + ([] if not energia or y > 0 else ["El tirante debe ser mayor que 0."])
    if errs:
        for e in errs: der.error(e)
        st.stop()
    s = mh.Seccion(tipo, b, z)
    yc = mh.tirante_critico(s, Q)
    Ac, Tc = s.A(yc), s.T(yc)
    Vc = Q / Ac; Ec = yc + Vc ** 2 / (2 * mh.G)
    y2 = mh.y_alterno(s, Q, y) if energia else None
    tab_sec, tab_curva, tab_res, tab_proc = der.tabs(["Sección", "Curva E–y", "Resultados", "Procedimiento"])
    with tab_sec:
        st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
        st.plotly_chart(dib(s, yc, yc * 1.3, ("Concreto (acabado con llana)",) * 3, None), theme=None, config=CONFIG)
    with tab_curva:
        st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
        st.plotly_chart(curva(s, Q, y, yc, y2), theme=None, config=CONFIG)
    def tarjetas(items):
        for i in range(0, len(items), 3):
            for col, (t, v) in zip(st.columns(3), items[i:i + 3]): col.metric(t, v)
    with tab_res:
        st.markdown('<div class="grupo" style="margin-top:6px">Estado crítico</div>', unsafe_allow_html=True)
        tarjetas([("Tirante crítico yc", f"{yc:.3f} m"), ("Área crítica Ac", f"{Ac:.3f} m²"), ("Espejo crítico Tc", f"{Tc:.3f} m"),
                  ("Velocidad crítica Vc", f"{Vc:.3f} m/s"), ("Energía mínima Emín", f"{Ec:.3f} m"), ("Froude", "1.000")])
        if energia:
            A, V = s.A(y), Q / s.A(y); F = mh.froude(s, Q, y); reg, msg = mh.regimen(F)
            st.markdown('<div class="grupo">Tirante dado y tirante alterno</div>', unsafe_allow_html=True)
            tarjetas([("Energía específica E", f"{mh.energia(s, Q, y):.3f} m"), ("Tirante alterno y₂", f"{y2:.3f} m"), ("Régimen", reg),
                      ("Velocidad V", f"{V:.3f} m/s"), ("Froude F", f"{F:.3f}")])
            st.write(""); st.info(msg)
    with tab_proc:
        st.latex(r"\frac{Q^2}{g}=\frac{A_c^3}{T_c}")
        st.latex(rf"\frac{{{Q:.3f}^2}}{{9.81}}=\frac{{{Ac:.3f}^3}}{{{Tc:.3f}}}\ \Rightarrow\ y_c={yc:.3f}\ \mathrm{{m}}")
        st.latex(rf"E_{{min}}=y_c+\frac{{V_c^2}}{{2g}}={yc:.3f}+\frac{{{Vc:.3f}^2}}{{2(9.81)}}={Ec:.3f}\ \mathrm{{m}}")
        if energia:
            st.latex(rf"E=y+\frac{{V^2}}{{2g}}={mh.energia(s, Q, y):.3f}\ \mathrm{{m}}\qquad E(y_1)=E(y_2)\Rightarrow y_2={y2:.3f}\ \mathrm{{m}}")

            