"""
Intercambiador de Calor Industrial - Tipo Carcasa y Tubos (3D)
Deploy en Streamlit
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import streamlit as st

# ---- Configuración de la página ----
st.set_page_config(
    page_title="Intercambiador de Calor 3D",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Intercambiador de Calor Industrial — Tipo Carcasa y Tubos (3D)")
st.markdown("Modelo 3D de un intercambiador de calor shell & tube con carcasa translúcida.")

# ---- Barra lateral: parámetros ajustables ----
st.sidebar.header("⚙️ Parámetros del diseño")
L_shell = st.sidebar.slider("Longitud carcasa (m)", 4.0, 10.0, 6.0, 0.5)
R_shell = st.sidebar.slider("Radio carcasa (m)", 0.6, 1.5, 1.0, 0.1)
pitch = st.sidebar.slider("Paso entre tubos (m)", 0.20, 0.45, 0.30, 0.05)
rings = st.sidebar.slider("Anillos de tubos", 2, 5, 3)
elev = st.sidebar.slider("Elevación vista (°)", 0, 60, 16)
azim = st.sidebar.slider("Azimut vista (°)", -180, 180, -60)
r_tube = 0.055

# ---- Funciones de geometría ----
def cylinder_x(ax, x0, x1, r, color, alpha=1.0, n=60, shade=True):
    th = np.linspace(0, 2*np.pi, n)
    x = np.linspace(x0, x1, 2)
    TH, X = np.meshgrid(th, x)
    ax.plot_surface(X, r*np.cos(TH), r*np.sin(TH), color=color, alpha=alpha,
                    linewidth=0.2, antialiased=True, shade=shade)

def ellipsoid_head(ax, x_c, r, depth, sign, color):
    u = np.linspace(0, np.pi/2, 30)
    v = np.linspace(0, 2*np.pi, 60)
    U, V = np.meshgrid(u, v)
    ax.plot_surface(x_c + sign*depth*np.cos(U), r*np.sin(U)*np.cos(V),
                    r*np.sin(U)*np.sin(V), color=color, linewidth=0, shade=True)

def ring(ax, x, w, r_out, r_in, color):
    th = np.linspace(0, 2*np.pi, 80)
    xg = np.linspace(x, x+w, 2)
    TH, X = np.meshgrid(th, xg)
    for rr in np.linspace(r_in, r_out, 6):
        ax.plot_surface(X, rr*np.cos(TH), rr*np.sin(TH), color=color, linewidth=0, shade=True)

def nozzle_z(ax, x_c, z0, z1, r, color):
    th = np.linspace(0, 2*np.pi, 50)
    z = np.linspace(z0, z1, 2)
    TH, Z = np.meshgrid(th, z)
    ax.plot_surface(x_c + r*np.cos(TH), r*np.sin(TH), Z, color=color, linewidth=0, shade=True)

# ---- Colores ----
C_SHELL = '#2E86AB'
C_HEAD = '#A23B72'
C_FLANGE = '#6B7280'
C_TUBE = '#F6BD60'
C_NOZZLE = '#C0392B'
C_SADDLE = '#3B4252'

# ---- Generar la figura ----
fig = plt.figure(figsize=(14, 8), dpi=120)
ax = fig.add_subplot(111, projection='3d')

# Tubos (arreglo triangular)
positions = [(0.0, 0.0)]
for k in range(1, rings + 1):
    for i in range(6 * k):
        a = i * (2 * np.pi / (6 * k))
        positions.append((k * pitch * np.cos(a), k * pitch * np.sin(a)))
positions = [p for p in positions if np.hypot(*p) < R_shell - 0.18]
n_tubes = len(positions)
for (yy, zz) in positions:
    cylinder_x(ax, -0.14, L_shell + 0.14, r_tube, C_TUBE, alpha=0.95)

# Placas tubulares
ring(ax, -0.16, 0.05, R_shell - 0.02, 0.16, '#D9D9D9')
ring(ax, L_shell + 0.11, 0.05, R_shell - 0.02, 0.16, '#D9D9D9')

# Carcasa translúcida
cylinder_x(ax, 0, L_shell, R_shell, C_SHELL, alpha=0.32, shade=False)
ring(ax, -0.045, 0.045, R_shell, R_shell - 0.02, '#1b5e7a')
ring(ax, L_shell - 0.045, 0.045, R_shell, R_shell - 0.02, '#1b5e7a')

# Bridas
cylinder_x(ax, -0.24, -0.02, R_shell + 0.10, C_FLANGE)
cylinder_x(ax, L_shell + 0.02, L_shell + 0.24, R_shell + 0.10, C_FLANGE)

# Cabezales semielipsoides
ellipsoid_head(ax, -0.24, R_shell, 0.85, -1, C_HEAD)
ellipsoid_head(ax, L_shell + 0.24, R_shell, 0.85, +1, C_HEAD)

# Boquillas lado carcasa
nozzle_z(ax, L_shell * 0.5, R_shell - 0.05, R_shell + 0.55, 0.22, C_NOZZLE)
nozzle_z(ax, L_shell * 0.5, -R_shell - 0.55, -R_shell + 0.05, 0.22, C_NOZZLE)

# Boquillas lado tubos (eje Y)
th2 = np.linspace(0, 2 * np.pi, 50)
for sgn, xc in [(-1, -1.09), (1, L_shell + 1.09)]:
    yy = np.linspace(sgn * (R_shell - 0.05), sgn * (R_shell + 0.5), 2)
    TH, Y = np.meshgrid(th2, yy)
    ax.plot_surface(xc + 0.22 * np.cos(TH), Y, 0.22 * np.sin(TH),
                    color=C_NOZZLE, linewidth=0, shade=True)

# Soportes (saddles)
def saddle(ax, x_c):
    th = np.linspace(np.pi * 1.05, np.pi * 1.95, 30)
    x = np.linspace(x_c - 0.18, x_c + 0.18, 2)
    TH, X = np.meshgrid(th, x)
    ax.plot_surface(X, (R_shell + 0.06) * np.cos(TH), (R_shell + 0.06) * np.sin(TH),
                    color=C_SADDLE, linewidth=0, shade=True)
    verts = [[(x_c - 0.18, -R_shell - 0.35, -R_shell - 0.4),
              (x_c + 0.18, -R_shell - 0.35, -R_shell - 0.4),
              (x_c + 0.18, R_shell + 0.35, -R_shell - 0.4),
              (x_c - 0.18, R_shell + 0.35, -R_shell - 0.4)]]
    ax.add_collection3d(Poly3DCollection(verts, color=C_SADDLE, alpha=0.9))

saddle(ax, L_shell * 0.25)
saddle(ax, L_shell * 0.75)

# Etiquetas
def tag(text, xyz, txz, color):
    ax.text(*txz, text, color=color, fontsize=10, fontweight='bold')
    ax.plot([xyz[0], txz[0]], [xyz[1], txz[1]], [xyz[2], txz[2]],
            color=color, lw=0.8, ls='--', alpha=0.8)

tag('Carcasa', (L_shell * 0.55, 0, R_shell), (L_shell * 0.75, 2.1, 1.7), '#1b5e7a')
tag('Cabezal (2 pasos)', (-0.95, 0, 0.5), (-2.9, 1.4, 2.0), '#7a2452')
tag(f'Haz de tubos (n={n_tubes})', (L_shell * 0.5, 0.3, 0.3), (L_shell * 0.55, 2.3, -0.7), '#8a5a13')
tag('Boquilla\nentrada/salida', (L_shell * 0.5, 0, R_shell + 0.55), (L_shell * 0.15, 0.4, 2.9), '#8e2a20')
tag('Placa tubular', (0, 0.25, 0.3), (-1.7, -1.5, 1.7), '#555555')
tag('Brida', (L_shell, R_shell + 0.05, 0.4), (L_shell + 1.1, 1.5, 1.9), '#374151')
tag('Soporte (saddle)', (L_shell * 0.75, -0.5, -1.1), (L_shell * 0.85, -2.2, -2.0), '#232a36')

# Flechas de flujo
ax.quiver(-1.6, 0.45, 0.45, 0.9, 0, 0, color=C_TUBE, linewidth=3, arrow_length_ratio=0.3)
ax.text(-2.35, 0.45, 0.55, 'Fluido lado tubos', color='#8a5a13', fontsize=9)
ax.quiver(L_shell + 1.7, -0.45, 0.55, -0.9, 0, 0, color=C_SHELL, linewidth=3, arrow_length_ratio=0.3)
ax.text(L_shell + 1.0, -0.45, 0.75, 'Fluido lado carcasa', color='#1b5e7a', fontsize=9)

# Ajustes de vista
ax.set_xlim(-3.2, L_shell + 3.2)
ax.set_ylim(-3.0, 3.0)
ax.set_zlim(-2.7, 3.1)
ax.set_box_aspect((L_shell + 6.4, 6.0, 5.8))
ax.view_init(elev=elev, azim=azim)
ax.set_axis_off()

st.pyplot(fig)
plt.close(fig)

# ---- Métricas debajo del modelo ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tubos", n_tubes)
col2.metric("Longitud carcasa", f"{L_shell:.1f} m")
col3.metric("Diámetro carcasa", f"{2*R_shell:.1f} m")
col4.metric("Paso triangular", f"{pitch:.2f} m")

st.markdown("---")
st.markdown("**Componentes:** Carcasa · Haz de tubos · Cabezales (2 pasos) · Placas tubulares · Bridas · Boquillas · Soportes")
st.markdown("Repo: GitHub | Deploy: Streamlit Cloud 🚀")
