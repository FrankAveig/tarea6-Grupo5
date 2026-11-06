"""Sistema de optimización de rutas de reparto (Tarea 6).

Aplicación de escritorio con Tkinter y Matplotlib. Registra paradas con
coordenadas y paquetes, y calcula la ruta más corta con un algoritmo voraz
que respeta la capacidad del vehículo.

Ejecución:
    python main.py
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

CAPACIDAD = 60
TARIFA_KM = 0.75

NAVY = "#0F1A24"
ROJO = "#E4012E"
FONDO = "#F4F6F9"
TARJETA = "#FFFFFF"
BORDE = "#E3E8EF"
TEXTO = "#1F2937"
GRIS = "#64748B"


@dataclass(frozen=True)
class Parada:
    nombre: str
    x: float
    y: float
    paquetes: int


def distancia(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def optimizar(paradas: list[Parada]) -> tuple[list[tuple], float, int]:
    """Recorre las paradas con un voraz: siempre la más cercana.

    Si la carga supera la capacidad, el vehículo vuelve a la base y comienza
    un nuevo viaje. Devuelve las filas de la ruta, los km y los viajes.
    """
    pendientes = list(paradas)
    filas: list[tuple] = []
    actual = (0.0, 0.0)
    carga = 0
    viaje = 1
    orden = 1
    total = 0.0

    while pendientes:
        cercana = min(pendientes, key=lambda p: distancia(actual, (p.x, p.y)))

        if carga + cercana.paquetes > CAPACIDAD:
            tramo = distancia(actual, (0.0, 0.0))
            total += tramo
            filas.append((viaje, orden, "Base (regreso)", tramo, "-", round(total, 2)))
            actual = (0.0, 0.0)
            carga = 0
            viaje += 1
            orden = 1
            continue

        tramo = distancia(actual, (cercana.x, cercana.y))
        total += tramo
        carga += cercana.paquetes
        filas.append(
            (viaje, orden, cercana.nombre, tramo, carga, round(total, 2))
        )
        actual = (cercana.x, cercana.y)
        pendientes.remove(cercana)
        orden += 1

    total += distancia(actual, (0.0, 0.0))
    filas.append((viaje, orden, "Base (regreso)", distancia(actual, (0.0, 0.0)), "-", round(total, 2)))
    return filas, total, viaje


def ruta_por_registro(paradas: list[Parada]) -> float:
    """Distancia de la ruta si se visitan en el orden de registro."""
    actual = (0.0, 0.0)
    total = 0.0
    carga = 0
    for parada in paradas:
        if carga + parada.paquetes > CAPACIDAD:
            total += distancia(actual, (0.0, 0.0))
            actual = (0.0, 0.0)
            carga = 0
        total += distancia(actual, (parada.x, parada.y))
        actual = (parada.x, parada.y)
        carga += parada.paquetes
    total += distancia(actual, (0.0, 0.0))
    return total


class VentanaRutas(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Optimizador de rutas · Tarea 6 · Grupo 5")
        self.geometry("1180x760")
        self.minsize(1100, 720)
        self.configure(bg=FONDO)

        self.paradas: list[Parada] = []
        self.ruta: list[tuple] = []
        self.total = 0.0
        self.viajes = 0

        self.var_nombre = tk.StringVar()
        self.var_x = tk.StringVar()
        self.var_y = tk.StringVar()
        self.var_paquetes = tk.StringVar()

        self._estilos()
        self._construir()
        self.cargar_ejemplo()

    # ------------------------------------------------------------------
    def _estilos(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure(".", font=("Segoe UI", 10), background=FONDO)
        estilo.configure(
            "TEntry", fieldbackground=TARJETA, bordercolor=BORDE,
            lightcolor=BORDE, darkcolor=BORDE, padding=6,
        )
        estilo.map("TEntry", bordercolor=[("focus", ROJO)])
        estilo.configure(
            "TButton", background=TARJETA, foreground=NAVY, bordercolor=BORDE,
            padding=(10, 7), font=("Segoe UI", 9, "bold"),
        )
        estilo.map("TButton", background=[("active", "#F1F5F9")])
        estilo.configure(
            "Primario.TButton", background=ROJO, foreground="white",
            borderwidth=0, padding=(12, 9), font=("Segoe UI", 10, "bold"),
        )
        estilo.map("Primario.TButton", background=[("active", "#B80025")])
        estilo.configure(
            "Treeview", background=TARJETA, fieldbackground=TARJETA,
            rowheight=25, borderwidth=0, font=("Segoe UI", 9),
        )
        estilo.configure(
            "Treeview.Heading", background="#F1F5F9", foreground="#475569",
            font=("Segoe UI", 8, "bold"), relief="flat", padding=(5, 5),
        )

    def _tarjeta(self, padre) -> tk.Frame:
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BORDE,
                        highlightthickness=1, bd=0)

    def _construir(self) -> None:
        cabecera = tk.Frame(self, bg=NAVY, height=78)
        cabecera.pack(fill="x")
        cabecera.pack_propagate(False)
        tk.Label(cabecera, text="OPTIRUTA", bg=ROJO, fg="white",
                 font=("Segoe UI", 11, "bold"), width=8, height=2).pack(side="left", padx=(24, 14))
        textos = tk.Frame(cabecera, bg=NAVY)
        textos.pack(side="left")
        tk.Label(textos, text="Optimización de rutas de reparto", bg=NAVY, fg="white",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(textos, text="Tarea 6 · Grupo 5 · Algoritmo voraz con capacidad",
                 bg=NAVY, fg="#94A3B8", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Frame(self, bg=ROJO, height=3).pack(fill="x")

        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=18, pady=14)
        cuerpo.columnconfigure(0, weight=0, minsize=310)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=0)
        cuerpo.rowconfigure(1, weight=1)

        self._panel_formulario(cuerpo)
        self._panel_tablas(cuerpo)
        self._panel_grafica(cuerpo)
        self._pie()

    def _panel_formulario(self, padre) -> None:
        panel = self._tarjeta(padre)
        panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 14))

        tk.Label(panel, text="REGISTRO DE PARADAS", bg=TARJETA, fg="#94A3B8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(panel, text="Nueva parada", bg=TARJETA, fg=NAVY,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16)
        tk.Label(panel, text="Coordenadas en km desde la base (0, 0).",
                 bg=TARJETA, fg=GRIS, font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(2, 8))

        for etiqueta, variable, ancho in (
            ("Nombre del punto", self.var_nombre, 22),
            ("Coordenada X (km)", self.var_x, 10),
            ("Coordenada Y (km)", self.var_y, 10),
            ("Paquetes", self.var_paquetes, 10),
        ):
            tk.Label(panel, text=etiqueta, bg=TARJETA, fg="#475569",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(8, 3))
            ttk.Entry(panel, textvariable=variable, width=ancho).pack(fill="x", padx=16)

        ttk.Button(panel, text="Agregar parada", command=self.agregar).pack(
            fill="x", padx=16, pady=(14, 6))
        fila = tk.Frame(panel, bg=TARJETA)
        fila.pack(fill="x", padx=16)
        ttk.Button(fila, text="Eliminar", command=self.eliminar).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(fila, text="Limpiar", command=self.limpiar).pack(side="left", expand=True, fill="x", padx=(4, 0))
        ttk.Button(panel, text="Cargar ejemplo", command=self.cargar_ejemplo).pack(
            fill="x", padx=16, pady=(6, 0))
        ttk.Button(panel, text="Optimizar ruta", style="Primario.TButton",
                   command=self.optimizar).pack(fill="x", padx=16, pady=(12, 10))

        tk.Frame(panel, bg=BORDE, height=1).pack(fill="x", padx=16, pady=4)
        self.lbl_resumen = tk.Label(panel, text="Sin paradas registradas", bg=TARJETA,
                                    fg=NAVY, font=("Segoe UI", 9), justify="left",
                                    wraplength=270)
        self.lbl_resumen.pack(anchor="w", padx=16, pady=(6, 10))

    def _panel_tablas(self, padre) -> None:
        contenedor = tk.Frame(padre, bg=FONDO)
        contenedor.grid(row=0, column=1, sticky="nsew")
        contenedor.columnconfigure(0, weight=1, uniform="tabla")
        contenedor.columnconfigure(1, weight=1, uniform="tabla")

        izquierda = self._tarjeta(contenedor)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(izquierda, text="Paradas registradas", bg=TARJETA, fg=NAVY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
        self.tabla_paradas = ttk.Treeview(
            izquierda, columns=("nombre", "x", "y", "paquetes"),
            show="headings", height=6, selectmode="browse",
        )
        for columna, titulo, ancho in (
            ("nombre", "Parada", 120), ("x", "X", 60),
            ("y", "Y", 60), ("paquetes", "Paq.", 55),
        ):
            self.tabla_paradas.heading(columna, text=titulo)
            self.tabla_paradas.column(columna, width=ancho, anchor="center" if columna != "nombre" else "w")
        self.tabla_paradas.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        derecha = self._tarjeta(contenedor)
        derecha.grid(row=0, column=1, sticky="nsew")
        tk.Label(derecha, text="Ruta optimizada", bg=TARJETA, fg=NAVY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
        self.tabla_ruta = ttk.Treeview(
            derecha, columns=("viaje", "orden", "parada", "tramo", "carga", "acumulado"),
            show="headings", height=6, selectmode="browse",
        )
        for columna, titulo, ancho in (
            ("viaje", "Viaje", 50), ("orden", "N.º", 40), ("parada", "Parada", 130),
            ("tramo", "km", 55), ("carga", "Carga", 55), ("acumulado", "Acum.", 70),
        ):
            self.tabla_ruta.heading(columna, text=titulo)
            self.tabla_ruta.column(columna, width=ancho, anchor="center" if columna != "parada" else "w")
        self.tabla_ruta.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    def _panel_grafica(self, padre) -> None:
        tarjeta = self._tarjeta(padre)
        tarjeta.grid(row=1, column=1, sticky="nsew", pady=(12, 0))
        tk.Label(tarjeta, text="Mapa de la ruta", bg=TARJETA, fg=NAVY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(8, 0))
        self.figura = Figure(figsize=(7.6, 3.1), dpi=100, facecolor="white")
        self.lienzo = FigureCanvasTkAgg(self.figura, master=tarjeta)
        self.lienzo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 8))

    def _pie(self) -> None:
        pie = tk.Frame(self, bg="#E9EEF4", height=28)
        pie.pack(fill="x", side="bottom")
        pie.pack_propagate(False)
        self.lbl_estado = tk.Label(pie, text="Listo", bg="#E9EEF4", fg="#475569",
                                   font=("Segoe UI", 8))
        self.lbl_estado.pack(side="left", padx=20)
        tk.Label(pie, text="Lógica de Programación · Grupo 5 · UBE", bg="#E9EEF4",
                 fg="#94A3B8", font=("Segoe UI", 8)).pack(side="right", padx=20)

    # ------------------------------------------------------------------
    def agregar(self) -> None:
        nombre = self.var_nombre.get().strip()
        try:
            x = float(self.var_x.get().replace(",", "."))
            y = float(self.var_y.get().replace(",", "."))
            paquetes = int(self.var_paquetes.get())
        except ValueError:
            messagebox.showwarning("Datos inválidos", "Revise las coordenadas y los paquetes.")
            return
        if not nombre:
            messagebox.showwarning("Datos inválidos", "El nombre de la parada es obligatorio.")
            return
        if any(parada.nombre.lower() == nombre.lower() for parada in self.paradas):
            messagebox.showwarning("Datos inválidos", "Ya existe una parada con ese nombre.")
            return
        if paquetes <= 0:
            messagebox.showwarning("Datos inválidos", "Los paquetes deben ser mayores que cero.")
            return
        if paquetes > CAPACIDAD:
            messagebox.showwarning("Datos inválidos", f"Cada parada admite hasta {CAPACIDAD} paquetes.")
            return

        self.paradas.append(Parada(nombre, x, y, paquetes))
        self.var_nombre.set("")
        self._actualizar()
        self.lbl_estado.configure(text=f"Parada agregada: {nombre}")

    def eliminar(self) -> None:
        seleccion = self.tabla_paradas.selection()
        if not seleccion:
            messagebox.showinfo("Seleccionar", "Seleccione una parada de la tabla.")
            return
        self.paradas.pop(int(seleccion[0]))
        self._actualizar()

    def limpiar(self) -> None:
        self.paradas.clear()
        self.ruta = []
        self._actualizar()

    def cargar_ejemplo(self) -> None:
        self.paradas = [
            Parada("Mercado Central", 2, 3, 12),
            Parada("Clínica Norte", 5, 7, 8),
            Parada("Barrio El Sol", -4, 2, 15),
            Parada("Universidad", -6, -3, 20),
            Parada("Terminal", 3, -5, 18),
            Parada("Parque Industrial", 8, -2, 25),
        ]
        self._actualizar()
        self.lbl_estado.configure(text="Datos de ejemplo cargados")

    def optimizar(self) -> None:
        if len(self.paradas) < 2:
            messagebox.showinfo("Faltan datos", "Registre al menos dos paradas.")
            return
        self.ruta, self.total, self.viajes = optimizar(self.paradas)
        self._actualizar()

    # ------------------------------------------------------------------
    def _actualizar(self) -> None:
        for tabla in (self.tabla_paradas, self.tabla_ruta):
            for elemento in tabla.get_children():
                tabla.delete(elemento)

        for indice, parada in enumerate(self.paradas):
            self.tabla_paradas.insert(
                "", "end", iid=str(indice),
                values=(parada.nombre, parada.x, parada.y, parada.paquetes),
            )

        for indice, fila in enumerate(self.ruta):
            self.tabla_ruta.insert(
                "", "end", iid=str(indice),
                values=(fila[0], fila[1], fila[2], f"{fila[3]:.2f}", fila[4], f"{fila[5]:.2f}"),
            )

        if self.ruta:
            costo = self.total * TARIFA_KM
            self.lbl_resumen.configure(
                text=(
                    f"Paradas: {len(self.paradas)}   ·   Paquetes: "
                    f"{sum(p.paquetes for p in self.paradas)}\n"
                    f"Distancia: {self.total:.2f} km   ·   Costo: ${costo:.2f}\n"
                    f"Viajes: {self.viajes}   ·   Tarifa: ${TARIFA_KM:.2f}/km"
                )
            )
        else:
            self.lbl_resumen.configure(
                text=(
                    f"Paradas: {len(self.paradas)}   ·   Paquetes: "
                    f"{sum(p.paquetes for p in self.paradas)}\n"
                    "Presione «Optimizar ruta» para calcular el recorrido."
                )
            )

        self._dibujar()
        self.lbl_estado.configure(
            text=f"{len(self.paradas)} paradas · {self.total:.2f} km · {self.viajes} viajes"
        )

    def _dibujar(self) -> None:
        self.figura.clear()
        eje = self.figura.add_subplot(111)
        eje.set_title("Ruta de reparto desde la base")
        eje.set_xlabel("X (km)")
        eje.set_ylabel("Y (km)")
        eje.grid(True, linestyle="--", alpha=0.35)
        eje.axhline(0, color="#CBD5E1", linewidth=0.8)
        eje.axvline(0, color="#CBD5E1", linewidth=0.8)
        eje.plot(0, 0, marker="s", markersize=10, color="#0F1A24", label="Base")

        if self.ruta:
            actual = (0.0, 0.0)
            colores = ["#E4012E", "#0E7C86", "#B45309", "#5B6C8F", "#7C3AED"]
            for fila in self.ruta:
                viaje, _orden, nombre, _tramo, _carga, _acumulado = fila
                if nombre.startswith("Base"):
                    destino = (0.0, 0.0)
                else:
                    parada = next(p for p in self.paradas if p.nombre == nombre)
                    destino = (parada.x, parada.y)
                eje.plot([actual[0], destino[0]], [actual[1], destino[1]],
                         color=colores[(viaje - 1) % len(colores)], linewidth=1.6)
                actual = destino

        for parada in self.paradas:
            eje.plot(parada.x, parada.y, "o", color="#16324F", markersize=7)
            eje.annotate(parada.nombre, (parada.x, parada.y), textcoords="offset points",
                         xytext=(6, 5), fontsize=8, color="#334155")
        eje.legend(loc="upper right", fontsize=8, frameon=False)
        self.figura.tight_layout()
        self.lienzo.draw()


if __name__ == "__main__":
    aplicacion = VentanaRutas()
    aplicacion.mainloop()
