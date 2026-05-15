# Regla de Simpson 3/8 para integración numérica
# Aproxima la integral definida ∫f(x)dx en [a, b] usando interpolación cúbica con 3 segmentos (4 puntos). 
# Fórmula:
#    ∫f(x)dx ≈ (3h/8)[f(x₀) + 3f(x₁) + 3f(x₂) + f(x₃)]

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# Configuración global de estilos, colores y fuentes

# Paleta de colores
ROSE = '#e75480'
ROSE_HOVER = '#d6336c'
ROSE_LIGHT = '#ffb3c6'
TEXT_DARK = '#1a1a2e'
BG_SOFT = '#f5f0f2'
WHITE = '#ffffff'
BORDER = '#e8e0e4'
GRAY_TEXT = '#8e8e93'
SUCCESS = '#27ae60'
ERROR = '#e74c3c'
CHART_LINE = '#2c3e50'

# Fonts
FONT_TITLE = ('Segoe UI', 15, 'bold')
FONT_SUBTITLE = ('Segoe UI', 11, 'bold')
FONT_NORMAL = ('Segoe UI', 10)
FONT_SMALL = ('Segoe UI', 9)
FONT_MONO = ('Consolas', 11, 'bold')

# Window dimensions
WIN_WIDTH = 1100
WIN_HEIGHT = 700
WIN_MIN_WIDTH = 1000
WIN_MIN_HEIGHT = 650

# Funciones matemáticas
def simpson_38(f_expr, a, b):
    # Aplica la regla de Simpson 3/8 con 4 puntos de evaluación.
    # h = (b - a) / 3
    # x₀ = a, x₁ = a + h, x₂ = a + 2h, x₃ = b
    # Aprox = (3h/8) · [f(x₀) + 3f(x₁) + 3f(x₂) + f(x₃)]
    x = sp.Symbol('x')
    f = sp.sympify(f_expr, locals={'e': sp.E})
    f_lambda = sp.lambdify(x, f, 'numpy')

    h = (b - a) / 3.0
    x0, x1, x2, x3 = a, a + h, a + 2 * h, b

    fx0 = float(f_lambda(x0))
    fx1 = float(f_lambda(x1))
    fx2 = float(f_lambda(x2))
    fx3 = float(f_lambda(x3))

    aprox = (3 * h / 8) * (fx0 + 3 * fx1 + 3 * fx2 + fx3)
    puntos = [(x0, fx0), (x1, fx1), (x2, fx2), (x3, fx3)]

    return aprox, puntos, h


def calcular_error(aprox, real):
    # Error porcentual: |(real - aprox) / real| × 100.
    if abs(real) < 1e-15:
        return 0.0
    return abs((real - aprox) / real) * 100

# Validar función y límites de integración

def validar_expresion(expr):
    # Verifica que la expresión matemática ingresada sea válida.
    expr = expr.strip()
    if not expr:
        return False, "La expresión no puede estar vacía."

    permitidas = [
        'exp', 'sin', 'cos', 'tan', 'log', 'sqrt', 'pi', 'e',
        'abs', 'sen', 'arcsin', 'arccos', 'arctan'
    ]
    limpia = expr.lower().replace('**', '^').replace('e^', 'exp')
    for p in permitidas:
        limpia = limpia.replace(p.lower(), '')

    limpia = re.sub(r'[0-9+\-*/^()., xX]', '', limpia)
    if limpia.strip():
        return False, f"Caracter(es) no válido(s): '{limpia.strip()[:10]}'"

    try:
        x = sp.Symbol('x')
        sp.sympify(expr, locals={'e': sp.E})
        return True, ""
    except Exception as e:
        return False, f"Expresión inválida: {str(e)}"


def validar_numero(texto, nombre):
    #Verifica que el texto sea un número válido (acepta punto y coma).
    texto = texto.strip().replace(',', '.')
    if not texto:
        return False, f"{nombre} no puede estar vacío."
    try:
        float(texto)
        return True, ""
    except ValueError:
        return False, f"{nombre} debe ser un número válido."

# Funciones auxiliares para la interfaz

def _limpiar_frame(frame):
    # Elimina todos los widgets dentro de un frame.
    for widget in frame.winfo_children():
        widget.destroy()


def _incrustar_figura(fig, frame):
    # Incrusta una figura de matplotlib en un frame de tkinter.
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Visualización de integración analítica y numérica

def grafica_analitica(f_expr, a, b, real):
    # Grafica la curva de f(x) con el área bajo la curva sombreada.
    x = sp.Symbol('x')
    f = sp.sympify(f_expr, locals={'e': sp.E})
    f_lambda = sp.lambdify(x, f, 'numpy')

    margen = (b - a) * 0.15
    xs = np.linspace(a - margen, b + margen, 800)
    ys = f_lambda(xs)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(BG_SOFT)
    ax.set_facecolor(WHITE)

    ax.plot(xs, ys, color=CHART_LINE, linewidth=2.2, label=r'$f(x)$')

    x_fill = np.linspace(a, b, 400)
    y_fill = f_lambda(x_fill)
    ax.fill_between(x_fill, y_fill, alpha=0.35, color=ROSE_LIGHT,
                    label=f'Área = {real:.6f}')

    ax.axvline(a, color=SUCCESS, linestyle='--', linewidth=1.2, alpha=0.7)
    ax.axvline(b, color=ROSE, linestyle='--', linewidth=1.2, alpha=0.7)

    ax.set_title('Integral Analítica — Curva y Área', fontsize=13,
                 fontweight='bold', color=CHART_LINE, pad=12)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('f(x)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10, framealpha=0.9, edgecolor=BORDER)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    return fig


def grafica_numerica(f_expr, a, b, puntos, h):
    # Grafica los puntos de Simpson 3/8 con interpolación.
    x = sp.Symbol('x')
    f = sp.sympify(f_expr, locals={'e': sp.E})
    f_lambda = sp.lambdify(x, f, 'numpy')

    margen = (b - a) * 0.15
    xs = np.linspace(a - margen, b + margen, 800)
    ys = f_lambda(xs)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(BG_SOFT)
    ax.set_facecolor(WHITE)

    # Curva real de referencia
    ax.plot(xs, ys, color=GRAY_TEXT, linewidth=1.5, alpha=0.6,
            label=r'$f(x)$', linestyle='--')

    # Interpolación en el intervalo
    xs_interp = np.linspace(a, b, 200)
    f_lambda_np = sp.lambdify(x, f, 'numpy')
    ys_interp = f_lambda_np(xs_interp)
    ax.plot(xs_interp, ys_interp, color=CHART_LINE, linewidth=2.2,
            label='Interpolación')

    # Puntos del método
    colores = [ROSE, '#e67e22', SUCCESS, '#9b59b6']
    x_vals = [p[0] for p in puntos]
    y_vals = [p[1] for p in puntos]
    for i, (xi, yi) in enumerate(puntos):
        ax.scatter(xi, yi, color=colores[i], s=80, zorder=5,
                   edgecolors=WHITE, linewidth=1.5)

    # Segmentos entre puntos
    for i in range(len(x_vals) - 1):
        ax.plot([x_vals[i], x_vals[i + 1]], [y_vals[i], y_vals[i + 1]],
                color=ROSE, linewidth=1.5, linestyle='-', alpha=0.7)

    # Líneas verticales de referencia
    for xi, yi in puntos:
        ax.axvline(xi, color=BORDER, linestyle=':', linewidth=0.8, alpha=0.5)

    ax.set_title('Método de Simpson 3/8 — Puntos e Interpolación', fontsize=13,
                 fontweight='bold', color=CHART_LINE, pad=12)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('f(x)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10, framealpha=0.9, edgecolor=BORDER)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Recuadro con coordenadas de los 4 puntos
    leyenda = (
        f'$x_0$={puntos[0][0]:.4f},  $x_1$={puntos[1][0]:.4f}\n'
        f'$x_2$={puntos[2][0]:.4f},  $x_3$={puntos[3][0]:.4f}'
    )
    ax.text(0.02, 0.98, leyenda, transform=ax.transAxes,
            fontsize=8.5, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=WHITE,
                      edgecolor=BORDER, alpha=0.9))

    fig.tight_layout()
    return fig

# Aplicación principal con interfaz gráfica usando tkinter

class Simpson38App:
    def __init__(self, root):
        self.root = root
        self.root.title("Integración Numérica — Regla de Simpson 3/8")
        self.root.configure(bg=BG_SOFT)

        # Centrar ventana en pantalla
        px = (self.root.winfo_screenwidth() - WIN_WIDTH) // 2
        py = (self.root.winfo_screenheight() - WIN_HEIGHT) // 2
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+{px}+{py}")
        self.root.minsize(WIN_MIN_WIDTH, WIN_MIN_HEIGHT)
        self.root.protocol("WM_DELETE_WINDOW", self._salir)

        # Estado del cálculo
        self.resultado_aprox = None
        self.resultado_real = None
        self.datos_puntos = None
        self.h_paso = None

        self._crear_estilos()
        self._crear_widgets()

    # Estilos

    def _crear_estilos(self):
        # Configura estilos globales de ttk con tema clam.
        estilo = ttk.Style()
        estilo.theme_use('clam')

        estilo.configure('TLabel', background=WHITE, foreground=TEXT_DARK, font=FONT_NORMAL)
        estilo.configure('TFrame', background=WHITE)
        estilo.configure('TButton', font=FONT_NORMAL, padding=(12, 6))
        estilo.configure('TEntry', font=FONT_NORMAL, padding=(6, 4))
        estilo.configure('TLabelframe', background=WHITE, foreground=ROSE, font=FONT_SUBTITLE)
        estilo.configure('TLabelframe.Label', background=WHITE, foreground=ROSE, font=FONT_SUBTITLE)
        estilo.configure('Panel.TFrame', background=BG_SOFT)

        # Botón Calcular
        estilo.configure('Calcular.TButton', background=ROSE, foreground=WHITE,
                         font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(20, 8))
        estilo.map('Calcular.TButton', background=[('active', ROSE_HOVER)])

        # Botón Limpiar
        estilo.configure('Limpiar.TButton', background=GRAY_TEXT, foreground=WHITE,
                         font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(20, 8))
        estilo.map('Limpiar.TButton', background=[('active', '#7a7a7f')])

        # Botón Salir
        estilo.configure('Salir.TButton', background=ERROR, foreground=WHITE,
                         font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(20, 8))
        estilo.map('Salir.TButton', background=[('active', '#c0392b')])

        # Pestañas
        estilo.configure('TNotebook', background=WHITE, borderwidth=0)
        estilo.configure('TNotebook.Tab', font=FONT_NORMAL, padding=(12, 5))
        estilo.map('TNotebook.Tab', background=[('selected', WHITE)])

        # Tabla
        estilo.configure('Treeview', font=FONT_SMALL, rowheight=26)
        estilo.configure('Treeview.Heading', font=FONT_NORMAL, padding=(6, 4))
        estilo.map('Treeview', background=[('selected', ROSE)],
                   foreground=[('selected', WHITE)])

    # Widgets

    def _crear_widgets(self):
        # Construye la jerarquía completa de la interfaz.
        principal = ttk.Frame(self.root, style='Panel.TFrame')
        principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self._crear_cabecera(principal)

        cuerpo = ttk.Frame(principal, style='Panel.TFrame')
        cuerpo.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self._crear_panel_izquierdo(cuerpo)
        self._crear_panel_derecho(cuerpo)

        # Barra de estado
        self.barra = tk.Label(principal, text="Listo. Ingrese la función y los límites, luego presione Calcular.",
                              font=FONT_SMALL, bg='#e8e0e4', fg=GRAY_TEXT,
                              anchor=tk.W, padx=12, pady=6, relief='sunken', bd=1)
        self.barra.pack(fill=tk.X, pady=(8, 0))

    def _crear_cabecera(self, padre):
        # Crea la barra de título superior.
        tk.Label(padre, text="Integración Numérica — Regla de Simpson 3/8",
                 font=('Segoe UI', 16, 'bold'), bg=BG_SOFT, fg=TEXT_DARK).pack(anchor=tk.W)
        tk.Label(padre, text="Aproximación por interpolación cúbica con 4 puntos",
                 font=('Segoe UI', 11, 'italic'), bg=BG_SOFT, fg=GRAY_TEXT).pack(anchor=tk.W)

    def _crear_panel_izquierdo(self, padre):
        # Panel izquierdo: función, límites y botones.
        frame = tk.Frame(padre, bg=WHITE, highlightbackground=BORDER,
                         highlightthickness=1, relief='solid')
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12), ipadx=5, ipady=8)

        tk.Label(frame, text="Parámetros de entrada", font=FONT_SUBTITLE,
                 bg=WHITE, fg=ROSE).pack(anchor=tk.W, padx=15, pady=(12, 5))
        tk.Frame(frame, bg=ROSE_LIGHT, height=2).pack(fill=tk.X, padx=15, pady=(0, 8))

        # Función a integrar
        tk.Label(frame, text="Función a integrar", font=('Segoe UI', 9, 'bold'),
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor=tk.W, padx=15, pady=(5, 3))
        self.entry_funcion = self._campo(frame, "f(x):", placeholder="exp(x), sin(x), x**2...")

        # Límites de integración
        tk.Label(frame, text="Límites de integración", font=('Segoe UI', 9, 'bold'),
                 bg=WHITE, fg=GRAY_TEXT).pack(anchor=tk.W, padx=15, pady=(12, 3))
        self.entry_a = self._campo(frame, "a (límite inf.):")
        self.entry_b = self._campo(frame, "b (límite sup.):")

        # Botones
        tk.Frame(frame, bg=WHITE, height=8).pack(fill=tk.X)
        bf = tk.Frame(frame, bg=WHITE)
        bf.pack(fill=tk.X, padx=15, pady=(8, 10))

        ttk.Button(bf, text="Calcular", style='Calcular.TButton',
                   command=self._calcular).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(bf, text="Limpiar", style='Limpiar.TButton',
                   command=self._limpiar).pack(fill=tk.X, pady=(0, 6))
        ttk.Button(bf, text="Salir", style='Salir.TButton',
                   command=self._salir).pack(fill=tk.X)

    def _campo(self, padre, texto, placeholder=None):
        # Crea una fila etiqueta + campo de entrada.
        fila = tk.Frame(padre, bg=WHITE)
        fila.pack(fill=tk.X, padx=15, pady=3)
        tk.Label(fila, text=texto, font=FONT_NORMAL, bg=WHITE,
                 fg=TEXT_DARK, width=18, anchor=tk.W).pack(side=tk.LEFT)
        e = tk.Entry(fila, font=FONT_NORMAL, bd=1, relief='solid',
                     highlightthickness=1, highlightcolor=ROSE,
                     highlightbackground=BORDER)
        e.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if placeholder:
            e.insert(0, placeholder)
            e.bind('<FocusIn>', lambda ev, entry=e: (
                entry.delete(0, tk.END) if entry.get() == placeholder else None
            ))
        return e

    def _crear_panel_derecho(self, padre):
        # Panel derecho: resumen de resultados y notebook con pestañas.
        frame = tk.Frame(padre, bg=WHITE, highlightbackground=BORDER,
                         highlightthickness=1, relief='solid')
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Resumen de resultados
        rf = tk.Frame(frame, bg=WHITE)
        rf.pack(fill=tk.X, padx=12, pady=(10, 5))
        tk.Label(rf, text="Resultados", font=FONT_SUBTITLE,
                 bg=WHITE, fg=TEXT_DARK).pack(anchor=tk.W)
        tk.Frame(rf, bg=ROSE_LIGHT, height=2).pack(fill=tk.X, pady=(5, 8))

        # Tarjetas de resultados (3 columnas)
        ind = tk.Frame(rf, bg=WHITE)
        ind.pack(fill=tk.X)
        for i, (tit, color, attr) in enumerate([
            ("Simpson 3/8", ROSE, 'lbl_aprox'),
            ("Valor real", SUCCESS, 'lbl_real'),
            ("Error porcentual", '#e67e22', 'lbl_error')
        ]):
            card = tk.Frame(ind, bg=BG_SOFT, highlightbackground=BORDER,
                            highlightthickness=1, relief='solid')
            card.grid(row=0, column=i, padx=4, pady=3, sticky='nsew')
            ind.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=tit, font=('Segoe UI', 9),
                     bg=BG_SOFT, fg=GRAY_TEXT).pack(padx=10, pady=(8, 2))
            lbl = tk.Label(card, text="—", font=FONT_MONO, bg=BG_SOFT, fg=color)
            lbl.pack(padx=10, pady=(0, 8))
            setattr(self, attr, lbl)

        # Notebook con pestañas
        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(5, 8))

        # Pestaña 1: Tabla de puntos
        self.tab_tabla = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tabla, text="Puntos de Simpson")
        self._crear_tabla()

        # Pestaña 2: Gráfica analítica
        self.tab_an = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_an, text="Gráfica analítica")
        self.frame_an = tk.Frame(self.tab_an, bg=WHITE)
        self.frame_an.pack(fill=tk.BOTH, expand=True)
        self._placeholder(self.frame_an, "Gráfica analítica")

        # Pestaña 3: Gráfica numérica
        self.tab_num = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_num, text="Gráfica numérica")
        self.frame_num = tk.Frame(self.tab_num, bg=WHITE)
        self.frame_num.pack(fill=tk.BOTH, expand=True)
        self._placeholder(self.frame_num, "Gráfica numérica")

    def _crear_tabla(self):
        # Crea el Treeview para la tabla de puntos de Simpson.
        ft = tk.Frame(self.tab_tabla, bg=WHITE)
        ft.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ('i', 'x_i', 'f(x_i)')
        self.tabla = ttk.Treeview(ft, columns=cols, show='headings', height=6)

        for c in cols:
            self.tabla.heading(c, text=c)
        self.tabla.column('i', width=80, anchor='center')
        self.tabla.column('x_i', width=200, anchor='center')
        self.tabla.column('f(x_i)', width=200, anchor='center')

        self.tabla.pack(fill=tk.BOTH, expand=True)

        self.tabla_ph = tk.Label(self.tab_tabla, text="Realice un cálculo para ver los puntos",
                                 font=FONT_NORMAL, bg=WHITE, fg='#bdc3c7')
        self.tabla_ph.pack(pady=20)

    def _placeholder(self, frame, texto):
        # Muestra un mensaje placeholder en un frame vacío.
        _limpiar_frame(frame)
        tk.Label(frame, text=f"Realice un cálculo para ver la {texto.lower()}",
                 font=FONT_NORMAL, bg=WHITE, fg='#bdc3c7').pack(expand=True)

    # Lógica de cálculo y actualización de resultados

    def _calcular(self):
        # Ejecuta el cálculo completo: valida, procesa y actualiza.
        f_expr = self.entry_funcion.get().strip()
        a_str = self.entry_a.get().strip()
        b_str = self.entry_b.get().strip()

        # Validar expresión
        valido, msg = validar_expresion(f_expr)
        if not valido:
            messagebox.showerror("Error de entrada", msg)
            return

        # Validar límites
        valido_a, msg_a = validar_numero(a_str, "a")
        if not valido_a:
            messagebox.showerror("Error de entrada", msg_a)
            return
        valido_b, msg_b = validar_numero(b_str, "b")
        if not valido_b:
            messagebox.showerror("Error de entrada", msg_b)
            return

        a = float(a_str.replace(',', '.'))
        b = float(b_str.replace(',', '.'))

        if a >= b:
            messagebox.showerror("Error de entrada",
                                 "El límite inferior (a) debe ser menor que (b).")
            return

        try:
            # Simpson 3/8
            aprox, puntos, h = simpson_38(f_expr, a, b)

            # Integral exacta con sympy
            x = sp.Symbol('x')
            f = sp.sympify(f_expr, locals={'e': sp.E})
            real = float(sp.integrate(f, (x, a, b)))

            # Error
            error = calcular_error(aprox, real)

            # Guardar estado
            self.resultado_aprox = aprox
            self.resultado_real = real
            self.datos_puntos = puntos
            self.h_paso = h

            # Actualizar interfaz
            self._actualizar_resultados()
            self._actualizar_tabla(puntos)
            self._actualizar_graficas(f_expr, a, b, real, aprox, puntos, h)

            self.barra.config(text=f"Cálculo completado. Simpson 3/8 ≈ {aprox:.6f}", fg=SUCCESS)

        except Exception as e:
            messagebox.showerror("Error de cálculo", f"Ocurrió un error al calcular:\n{str(e)}")
            self.barra.config(text="Error en el cálculo.", fg=ERROR)

    def _actualizar_resultados(self):
        # Actualiza las tres tarjetas de resultados numéricos.
        self.lbl_aprox.config(text=f"{self.resultado_aprox:.8f}")
        self.lbl_real.config(text=f"{self.resultado_real:.8f}")
        error = calcular_error(self.resultado_aprox, self.resultado_real)
        self.lbl_error.config(text=f"{error:.4f} %")

    def _actualizar_tabla(self, puntos):
        # Llena la tabla con los 4 puntos calculados por Simpson 3/8.
        self.tabla_ph.pack_forget()
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for i, (xi, fxi) in enumerate(puntos):
            self.tabla.insert('', tk.END, values=(i, f"{xi:.6f}", f"{fxi:.6f}"))

    def _actualizar_graficas(self, f_expr, a, b, real, aprox, puntos, h):
        # Genera y muestra ambas gráficas en las pestañas.
        # Gráfica analítica
        _limpiar_frame(self.frame_an)
        fig1 = grafica_analitica(f_expr, a, b, real)
        canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_an)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Gráfica numérica
        _limpiar_frame(self.frame_num)
        fig2 = grafica_numerica(f_expr, a, b, puntos, h)
        canvas2 = FigureCanvasTkAgg(fig2, master=self.frame_num)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cerrar figuras al salir
        def on_close():
            plt.close(fig1)
            plt.close(fig2)
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)

    # Acciones de botones

    def _limpiar(self):
        # Restablece todos los campos y resultados al estado inicial.
        self.entry_funcion.delete(0, tk.END)
        self.entry_a.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)

        for lbl in [self.lbl_aprox, self.lbl_real, self.lbl_error]:
            lbl.config(text="—")

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.tabla_ph.pack(pady=20)

        # Restablecer gráficas
        self._placeholder(self.frame_an, "Gráfica analítica")
        self._placeholder(self.frame_num, "Gráfica numérica")

        # Restablecer estado
        self.resultado_aprox = None
        self.resultado_real = None
        self.datos_puntos = None
        self.h_paso = None

        self.barra.config(text="Campos limpiados.", fg=GRAY_TEXT)

    def _salir(self):
        plt.close('all')
        self.root.destroy()

# Entrada al programa

def main():
    root = tk.Tk()
    app = Simpson38App(root)
    root.mainloop()

if __name__ == "__main__":
    main()