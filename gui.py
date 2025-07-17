import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class Nodo:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Barra:
    def __init__(self, nodo1, nodo2):
        self.nodo1 = nodo1
        self.nodo2 = nodo2

class PorticoGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Editor de Pórticos")
        
        self.nodos = []
        self.barras = []
        self.nodos_seleccionados = []

        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(side=tk.LEFT)

        self.controls = tk.Frame(master)
        self.controls.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_barra = tk.Button(self.controls, text="Crear barra", command=self.crear_barra)
        self.btn_barra.pack(pady=10)

        self.btn_reset = tk.Button(self.controls, text="Reset", command=self.reset)
        self.btn_reset.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(5,5))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.set_title("Haz clic para agregar nodos")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.dibujar()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        nodo = Nodo(x, y)
        self.nodos.append(nodo)
        self.nodos_seleccionados.append(nodo)
        if len(self.nodos_seleccionados) > 2:
            self.nodos_seleccionados.pop(0)
        self.dibujar()

    def crear_barra(self):
        if len(self.nodos_seleccionados) == 2:
            b = Barra(self.nodos_seleccionados[0], self.nodos_seleccionados[1])
            self.barras.append(b)
            self.nodos_seleccionados = []
            self.dibujar()
        else:
            messagebox.showinfo("Info", "Selecciona 2 nodos con clic para conectar.")

    def reset(self):
        self.nodos.clear()
        self.barras.clear()
        self.nodos_seleccionados.clear()
        self.dibujar()

    def dibujar(self):
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.set_title("Haz clic para agregar nodos")

        # Dibujar barras
        for b in self.barras:
            self.ax.plot([b.nodo1.x, b.nodo2.x], [b.nodo1.y, b.nodo2.y], 'k-', lw=2)

        # Dibujar nodos
        for i, nodo in enumerate(self.nodos):
            self.ax.plot(nodo.x, nodo.y, 'bo')
            self.ax.text(nodo.x + 0.1, nodo.y + 0.1, f"N{i}")

        self.canvas.draw()

# Lanzar GUI
root = tk.Tk()
app = PorticoGUI(root)
root.mainloop()
