"""Motor de cálculo de LYCANAL PRO: geometría, rugosidad, flujo uniforme y borde libre (SI)."""
import math

G = 9.81

# ---------- Geometría ----------
class Seccion:
    def __init__(self, tipo, b, z):
        self.tipo = tipo
        self.b = 0.0 if tipo == "Triangular" else b
        self.z = 0.0 if tipo == "Rectangular" else z
        self.k = math.sqrt(1 + self.z ** 2)
    def A(self, y): return y * (self.b + self.z * y)
    def P(self, y): return self.b + 2 * y * self.k
    def T(self, y): return self.b + 2 * self.z * y
    def paredes(self, y): return 2 * y * self.k
    def lado(self, y): return y * self.k

# ---------- Materiales: n típico (referencial), color de fondo, color de trama, trama ----------
MATERIALES = {
    "Concreto (acabado con llana)": (0.013, "#c9c9c3", "#7d7d77", "."),
    "Concreto (sin acabado)": (0.017, "#b5b5af", "#6b6b65", "."),
    "Mampostería de piedra": (0.025, "#d2c4a6", "#8c7c5a", "+"),
    "Tierra": (0.018, "#bd966b", "#7b5a37", "."),
    "Tierra con vegetación": (0.027, "#a3ad72", "#5f6e36", "."),
    "Roca excavada": (0.040, "#968b7e", "#4f483f", "x"),
    "Otro material": (0.015, "#b4c0cc", "#6a7b8c", "/"),
}

class Circular:
    """Sección circular de diámetro D, parcialmente llena (y ≤ D)."""
    b = 0.0
    z = 0.0
    def __init__(self, D):
        self.D, self.altura = D, D
        self.ymax, self.y_pico = D * (1 - 1e-9), 0.938 * D       # Q(y) es creciente hasta ≈ 0.938·D
    def _th(self, y): return 2 * math.acos(max(-1.0, min(1.0, 1 - 2 * y / self.D)))
    def A(self, y): th = self._th(y); return self.D ** 2 / 8 * (th - math.sin(th))
    def P(self, y): return self.D * self._th(y) / 2
    def T(self, y): return self.D * math.sin(self._th(y) / 2)


class Parabolica:
    """Parábola que pasa por (±T/2, H): espejo de agua T a la altura H. Foco k = T²/(16·H)."""
    b = 0.0
    z = 0.0
    def __init__(self, T, H):
        self.T0, self.H, self.altura, self.ymax, self.y_pico = T, H, H, H, H
        self.a, self.foco = H / (T / 2) ** 2, T * T / (16 * H)
    def T(self, y): return self.T0 * math.sqrt(y / self.H)
    def A(self, y): return 2 / 3 * self.T(y) * y
    def P(self, y):
        x, a = self.T(y) / 2, self.a
        return 2 * (x / 2 * math.sqrt(1 + 4 * a * a * x * x) + math.asinh(2 * a * x) / (4 * a))


class Poligonal:
    """Sección definida por puntos (x, z), de izquierda a derecha. ns[i] y mats[i] son del tramo i."""
    b = 0.0
    z = 0.0
    def __init__(self, pts, ns, mats):
        self.pts, self.ns, self.mats = pts, ns, mats
        self.zmin = min(q[1] for q in pts)
        self.altura = min(pts[0][1], pts[-1][1]) - self.zmin
    def _tramos(self, y):
        L = self.zmin + y; out = []
        for i in range(len(self.pts) - 1):
            (x1, z1), (x2, z2) = self.pts[i], self.pts[i + 1]
            dx, dz = x2 - x1, z2 - z1
            if min(z1, z2) >= L: out.append((i, 0.0, 0.0, 0.0)); continue
            if max(z1, z2) <= L: f0, f1 = 0.0, 1.0
            else:
                t = (L - z1) / dz
                f0, f1 = (0.0, t) if z1 < L else (t, 1.0)
            xw = abs(dx) * (f1 - f0)
            za, zb = z1 + dz * f0, z1 + dz * f1
            out.append((i, math.hypot(dx, dz) * (f1 - f0), xw, xw * (L - (za + zb) / 2)))
        return out
    def A(self, y): return sum(t[3] for t in self._tramos(y))
    def P(self, y): return sum(t[1] for t in self._tramos(y))
    def T(self, y): return sum(t[2] for t in self._tramos(y))
    def detalle(self, y): return [(f"Tramo {t[0] + 1}", t[1], self.ns[t[0]]) for t in self._tramos(y) if t[1] > 0]
    def partes(self, y): return [(d[1], d[2]) for d in self.detalle(y)]

class Subarea:
    """Celda de una sección compuesta: tramos a..b-1 (columna vertical) y banda de cotas [za, zb) (corte horizontal)."""
    def __init__(self, padre, a, b, za=-math.inf, zb=math.inf):
        self.p, self.a, self.b, self.za, self.zb = padre, a, b, za, zb

    def _calc(self, y):
        p = self.p; L = p.zmin + y; top = min(L, self.zb)
        A = P = T = 0.0; partes = []
        for i in range(self.a, self.b):
            (x1, z1), (x2, z2) = p.pts[i], p.pts[i + 1]
            dx, dz = x2 - x1, z2 - z1; l = math.hypot(dx, dz)
            if l == 0: continue
            ts = {0.0, 1.0}
            if dz != 0:
                for zl in (self.za, top, L):
                    t = (zl - z1) / dz
                    if 0 < t < 1: ts.add(t)
            ts = sorted(ts)
            h = lambda t: max(0.0, top - max(z1 + dz * t, self.za))
            for t0, t1 in zip(ts, ts[1:]):
                zm = z1 + dz * (t0 + t1) / 2
                A += dx * (t1 - t0) * (h(t0) + h(t1)) / 2
                if self.za <= zm < top:
                    P += l * (t1 - t0); partes.append((l * (t1 - t0), p.ns[i]))
                if self.za <= L < self.zb and zm < L: T += dx * (t1 - t0)
        if p.incluir:                                       # los cortes cuentan como perímetro mojado
            for k in (self.a, self.b):
                if 0 < k < len(p.pts) - 1: P += max(0.0, top - max(p.pts[k][1], self.za))
            for zc in (self.za, self.zb):
                if math.isfinite(zc) and p.zmin < zc < L: P += self._ancho_bajo(zc)
        return A, P, T, partes

    def _ancho_bajo(self, zc):
        w = 0.0
        for i in range(self.a, self.b):
            (x1, z1), (x2, z2) = self.p.pts[i], self.p.pts[i + 1]
            dx, dz = x2 - x1, z2 - z1
            if min(z1, z2) >= zc: continue                  # tramo sobre la cota (o plano justo en ella): sin agua por debajo
            if max(z1, z2) <= zc: w += dx
            else:
                tc = (zc - z1) / dz
                w += dx * (tc if z1 < zc else 1 - tc)
        return w

    def A(self, y): return self._calc(y)[0]
    def P(self, y): return self._calc(y)[1]
    def T(self, y): return self._calc(y)[2]
    def partes(self, y): return self._calc(y)[3]


class Compuesta(Poligonal):
    """Sección por puntos dividida en subáreas: cortes verticales en vértices y cortes horizontales a ciertas cotas."""
    def __init__(self, pts, ns, mats, cortes, incluir=False, post=None, seg_tramo=None, cortes_h=()):
        super().__init__(pts, ns, mats)
        self.seg_tramo, self.incluir, self.post = seg_tramo, incluir, post
        idx = [0] + sorted(set(cortes)) + [len(pts) - 1]
        self.columnas = [(idx[j], idx[j + 1]) for j in range(len(idx) - 1)]
        self.cortes_h = sorted({round(z, 9) for z in cortes_h if self.zmin < z < max(q[1] for q in pts)})
        bandas = list(zip([-math.inf] + self.cortes_h, self.cortes_h + [math.inf]))
        self.subareas = [Subarea(self, a, b, za, zb) for a, b in self.columnas for za, zb in bandas]
    def A(self, y): return sum(sa.A(y) for sa in self.subareas)
    def P(self, y): return sum(sa.P(y) for sa in self.subareas)
    def T(self, y): return sum(sa.T(y) for sa in self.subareas)

# ---------- Rugosidad ----------
def horton(partes):
    """partes: lista de (P_i, n_i). ne = (sum(P_i*n_i^1.5)/P)^(2/3)"""
    P = sum(p for p, _ in partes)
    return (sum(p * n ** 1.5 for p, n in partes) / P) ** (2 / 3)

def cowan(n0, n1, n2, n3, n4, m5):
    return (n0 + n1 + n2 + n3 + n4) * m5

# (condición de flujo, factor, [(condición, valor), ...])
TABLA_COWAN = [
    ("Tipos de materiales involucrados", "n0", [("Tierra", "0.021"), ("Corte en roca", "0.026"), ("Grava fina", "0.025"), ("Grava gruesa", "0.029")]),
    ("Irregularidad", "n1", [("Suave", "–"), ("Menor", "0.006"), ("Moderado", "0.011"), ("Severo", "0.021")]),
    ("Alteración en la sección transversal", "n2", [("Gradual", "–"), ("Ocasionalmente alternante", "0.006"), ("Frecuentemente alternante", "0.011–0.016")]),
    ("Efecto de las obstrucciones", "n3", [("Insignificante", "–"), ("Menor", "0.011–0.016"), ("Apreciable", "0.021–0.031"), ("Severo", "0.041–0.061")]),
    ("Cantidad de vegetación", "n4", [("Baja", "0.006–0.011"), ("Media", "0.011–0.026"), ("Alta", "0.026–0.051"), ("Muy alta", "0.051–0.100")]),
    ("Efecto generado por meandros", "m5", [("Menor", "1.000"), ("Apreciable", "1.160"), ("Severo", "1.350")]),
]

# ---------- Solución numérica ----------
def biseccion(fn, lo, hi, tol=1e-6):
    it, mid = [], (lo + hi) / 2
    for i in range(1, 201):
        mid = (lo + hi) / 2
        it.append({"i": i, "y": mid, "error": abs(hi - lo)})
        if fn(mid) > 0: hi = mid
        else: lo = mid
        if abs(hi - lo) < tol: break
    return mid, it

# ---------- Flujo uniforme: Q = C·A·√(R·S) ----------
def coef(metodo, R, S, n, p=0.0):
    """C de Chezy según el método. p = C (Chezy) o γ (Bazin)."""
    if metodo == "Chezy": return p
    if metodo == "Bazin": return 87 / (1 + p / math.sqrt(R))
    if metodo.startswith("Ganguillet"):
        k = 23 + 0.00155 / S
        return (k + 1 / n) / (1 + k * n / math.sqrt(R))
    return R ** (1 / 6) / n          # Manning

def q_flujo(s, n, S, y, metodo="Manning", p=0.0):
    if getattr(s, "subareas", None):                      # sección compuesta: Q = ΣQi
        return sum(q_sub(sa, s.post, S, y, metodo, p) for sa in s.subareas)
    A = s.A(y); R = A / s.P(y)
    return coef(metodo, R, S, n(y), p) * A * math.sqrt(R * S)


def n_sub(sa, post, y):
    pt = sa.partes(y)
    if not pt: return 0.0
    n0 = horton(pt)                                        # Horton dentro de la subárea
    return post(n0) if post else n0


def q_sub(sa, post, S, y, metodo, p):
    A, P = sa.A(y), sa.P(y)
    if A <= 0 or P <= 0: return 0.0
    R = A / P
    return coef(metodo, R, S, n_sub(sa, post, y), p) * A * math.sqrt(R * S)


def _etq_tramos(s, sa):
    if getattr(s, "seg_tramo", None):
        t0, t1 = s.seg_tramo[sa.a], s.seg_tramo[sa.b - 1]
        return f"Tramo {t0}" if t0 == t1 else f"Tramos {t0}–{t1}"
    return f"T{sa.a + 1}" + (f"–T{sa.b}" if sa.b - sa.a > 1 else "")


def _etq_banda(sa):
    if math.isinf(sa.za) and math.isinf(sa.zb): return ""
    if math.isinf(sa.za): return f", cota ≤ {sa.zb:.2f}"
    if math.isinf(sa.zb): return f", cota ≥ {sa.za:.2f}"
    return f", cota {sa.za:.2f} a {sa.zb:.2f}"


def detalle_subareas(s, y, S, metodo, p):
    out = []
    for j, sa in enumerate(s.subareas, 1):
        A, P = sa.A(y), sa.P(y)
        if A <= 1e-9: continue                              # celda seca o sin sección
        out.append(dict(nombre=f"Subárea {j}", tramos=_etq_tramos(s, sa) + _etq_banda(sa), A=A, P=P, T=sa.T(y),
                        n=n_sub(sa, s.post, y), R=A / P if P > 0 else 0.0, Q=q_sub(sa, s.post, S, y, metodo, p)))
    return out


def cortes_auto(pts, ns, mats, criterio, candidatos=None):
    """Vértices interiores donde se corta: cambio de material (n), de pendiente de las paredes, o ambos."""
    out = []
    if criterio.startswith("En cada unión"):
        return list(candidatos) if candidatos is not None else list(range(1, len(pts) - 1))
    tol = 1e-6 if candidatos is None else 0.12
    for k in (range(1, len(pts) - 1) if candidatos is None else candidatos):
        mat = abs(ns[k - 1] - ns[k]) > 1e-9 or mats[k - 1] != mats[k]
        a0 = math.atan2(pts[k][1] - pts[k - 1][1], pts[k][0] - pts[k - 1][0])
        a1 = math.atan2(pts[k + 1][1] - pts[k][1], pts[k + 1][0] - pts[k][0])
        pen = abs(a1 - a0) > tol
        if (criterio.startswith("Cambio de material") and mat) or (criterio.startswith("Cambio de pendiente") and pen) or (criterio == "Ambos" and (mat or pen)):
            out.append(k)
    return out

def tirante_normal(s, n, S, Q, metodo="Manning", p=0.0):
    tope = getattr(s, "y_pico", None)
    if tope:                                               # sección con altura máxima (circular, parabólica)
        f = lambda y: q_flujo(s, n, S, y, metodo, p) - Q
        return (tope, []) if f(tope) < 0 else biseccion(f, 1e-6, tope)
    hi = 1.0
    while q_flujo(s, n, S, hi, metodo, p) < Q and hi < 1e4: hi *= 2
    return biseccion(lambda y: q_flujo(s, n, S, y, metodo, p) - Q, 1e-6, hi)

def pendiente(s, n, Q, y, metodo="Manning", p=0.0):
    return biseccion(lambda S_: q_flujo(s, n, S_, y, metodo, p) - Q, 1e-9, 10.0, 1e-12)[0]

def validar_pendiente(S):
    if S < 0.0005: return "Pendiente muy baja (menor a 0.0005 m/m): riesgo de sedimentación y flujo muy lento."
    if S > 0.05: return "Pendiente muy alta (mayor a 0.05 m/m): flujo muy rápido, revisar erosión y disipación de energía."
    return None

# ---------- Diseño de sección: b/y = f·(√(1+z²) − z) ----------
FACTORES = {"Máxima eficiencia hidráulica": 2, "Mínima infiltración": 4, "Intermedia": 3}

def disenar(Q, S, n, z, f):
    k = math.sqrt(1 + z * z); m = f * (k - z)
    y = ((Q * n / math.sqrt(S)) * (m + 2 * k) ** (2 / 3) / (m + z) ** (5 / 3)) ** (3 / 8)
    return y, m * y, m

# ---------- Energía específica ----------
def energia(s, Q, y): return y + (Q / s.A(y)) ** 2 / (2 * G)

def y_alterno(s, Q, y):
    yc = tirante_critico(s, Q); E = energia(s, Q, y)
    if abs(y - yc) < 1e-6: return yc
    if y > yc: return biseccion(lambda t: E - energia(s, Q, t), 1e-6, yc)[0]
    ymax = getattr(s, "ymax", None)
    hi = ymax if ymax else max(yc * 2, 1.0)
    if ymax and energia(s, Q, hi) < E: return None        # no existe un alterno dentro de la altura de la sección
    while not ymax and energia(s, Q, hi) < E: hi *= 2
    return biseccion(lambda t: energia(s, Q, t) - E, yc, hi)[0]

def tirante_critico(s, Q):
    ymax = getattr(s, "ymax", None)
    hi = ymax if ymax else 1.0
    while not ymax and s.A(hi) ** 3 / s.T(hi) < Q ** 2 / G and hi < 1e4: hi *= 2
    return biseccion(lambda y: s.A(y) ** 3 / s.T(y) - Q ** 2 / G, 1e-6, hi)[0]

def froude(s, Q, y):
    return (Q / s.A(y)) / math.sqrt(G * s.A(y) / s.T(y))

def regimen(F):
    if abs(F - 1) < 0.01:
        return "Crítico", "Régimen inestable: se recomienda evitar diseñar cerca de este valor."
    if F < 1:
        return "Subcrítico", "Flujo lento y tranquilo, controlado desde aguas abajo."
    return "Supercrítico", "Flujo rápido, controlado desde aguas arriba. Revisar erosión y posible resalto."

def verificar_velocidad(V, vmin, vmax):
    if V < vmin: return "aviso", "V < Vmín: si va muy lento genera sedimentación."
    if V > vmax: return "aviso", "V > Vmáx: riesgo de erosión."
    return "ok", "✓ Cumple: la velocidad está dentro del rango permitido."

# ---------- Borde libre ----------
def c_usbr(Q): return 0.46 if Q <= 0.6 else 0.76

METODOS_BL = ["Máximo Villón (y/3 o y/5)", "USBR (Bureau of Reclamation)", "Villón por caudal", "Villón por ancho de solera",
              "ANA Tabla 11 (por caudal)", "Valor manual"]
# Tabla 11 del ANA, en metros: (Q máximo, revestido, sin revestir)
TABLA_ANA = [(0.05, 0.075, 0.10), (0.25, 0.10, 0.20), (0.50, 0.20, 0.40), (1.00, 0.25, 0.50), (float("inf"), 0.30, 0.60)]
TABLA_ANCHO = [(0.8, 0.40), (1.5, 0.50), (3.0, 0.60), (20.0, 1.00)]


def borde_libre(metodo, y, Q, revestido=False, manual=0.3, b=0.0):
    """Devuelve (BL, fórmula con valores, criterio aplicado). BL es None si el método no aplica."""
    if metodo.startswith("USBR"):
        C = c_usbr(Q)
        crit = f"C = {C} porque Q {'≤ 0.6' if Q <= 0.6 else '≤ 85'} m³/s"
        if Q > 85: crit += " (Q mayor a 85 m³/s: fuera del rango del método)"
        return math.sqrt(C * y), f"BL = √(C·y) = √({C}·{y:.3f})", crit
    if metodo.startswith("Máximo"):
        d = 5 if revestido else 3
        return y / d, f"BL = y/{d} = {y:.3f}/{d}", f"Canal {'revestido' if revestido else 'sin revestir'} según los materiales elegidos: y/{d}"
    if metodo == "Villón por caudal":
        v = 0.30 if Q <= 0.5 else 0.40
        return v, f"BL = {v:.2f} m", f"Q = {Q:.3f} m³/s {'≤' if Q <= 0.5 else '>'} 0.5 m³/s"
    if metodo == "Villón por ancho de solera":
        if b <= 0: return None, "No aplica", "Requiere un ancho de solera (rectangular o trapezoidal)"
        for lim, v in TABLA_ANCHO:
            if b <= lim: return v, f"BL = {v:.2f} m", f"b = {b:.3f} m, dentro de la fila hasta {lim} m"
        return 1.00, "BL = 1.00 m", f"b = {b:.3f} m supera los 20 m (fuera de la tabla): se usa el último valor"
    if metodo.startswith("ANA"):
        for lim, rv, sr in TABLA_ANA:
            if Q <= lim:
                v = rv if revestido else sr
                return v, f"BL = {v:.3f} m", f"Q = {Q:.3f} m³/s, canal {'revestido' if revestido else 'sin revestir'}"
    return manual, "BL ingresado por el usuario", "Valor ingresado por el usuario"


def comparar_bl(y, Q, revestido, b):
    """Lista (método, BL o None, criterio) para todos los métodos, menos el manual."""
    return [(mt, *borde_libre(mt, y, Q, revestido, 0.0, b)[::2]) for mt in METODOS_BL if mt != "Valor manual"]


def sugerir_bl(revestido, Q):
    if revestido: return "Máximo Villón y/5, porque el canal es revestido"
    if Q <= 0.6: return "Máximo Villón y/3, canal sin revestir y caudal pequeño"
    return "USBR, canal sin revestir con caudal medio"



    


