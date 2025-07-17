# Portico.py (Actualizado para usar VisualizadorPortico)
import numpy as np
import math
import matplotlib.pyplot as plt # Ya no lo necesita directamente para graficar, pero lo dejo por si acaso

from GestorDeModelo import GestorDeModelo
from CalculadoraPorticoBarra import CalculadoraPorticoBarra
from VisualizadorPortico import VisualizadorPortico # ¡Importar la nueva clase!


class Portico:
    def __init__(self):
        self.gestor_modelo = GestorDeModelo()
        self.calculadora_barra = CalculadoraPorticoBarra()
        # ¡Nueva instancia del visualizador!
        self.visualizador = VisualizadorPortico(self.gestor_modelo, self.calculadora_barra)

    def matriz_rigidez_global(self):
        nodos = self.gestor_modelo.get_nodos()
        barras = self.gestor_modelo.get_barras()
        id_to_index = self.gestor_modelo.get_dof_map()

        n_nodos = len(nodos)
        n_dof = 3 * n_nodos
        K = np.zeros((n_dof, n_dof))

        for id_barra, barra in barras.items():
            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            dofs = [3*i1, 3*i1+1, 3*i1+2, 3*i2, 3*i2+1, 3*i2+2]

            k_global_barra = self.calculadora_barra.rigidez_local_global(barra)

            for i in range(6):
                for j in range(6):
                    K[dofs[i], dofs[j]] += k_global_barra[i, j]

        return K

    def vector_fuerzas_equivalentes(self):
        nodos = self.gestor_modelo.get_nodos()
        barras = self.gestor_modelo.get_barras()
        id_to_index = self.gestor_modelo.get_dof_map()

        n_nodos = len(nodos)
        f_eq = np.zeros(3 * n_nodos)

        for barra in barras.values():
            feq = self.calculadora_barra.fuerzas_equivalentes_globales(barra)

            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            dofs = [3*i1, 3*i1+1, 3*i1+2, 3*i2, 3*i2+1, 3*i2+2]
            for i, dof in enumerate(dofs):
                f_eq[dof] += feq[i]

        return f_eq

    def aplicar_restricciones(self, K, f=None):
        restricciones = self.gestor_modelo.get_restricciones()
        K_mod = K.copy()
        n = K.shape[0]

        if f is None:
            f = np.zeros(n)

        f_mod = f.copy()

        for dof in sorted(list(restricciones)):
            K_mod[dof, :] = 0
            K_mod[:, dof] = 0
            K_mod[dof, dof] = 1
            f_mod[dof] = 0

        return K_mod, f_mod

    def analizar(self, fuerzas_nodales_aplicadas=None):
        K_global = self.matriz_rigidez_global()
        f_equivalentes = self.vector_fuerzas_equivalentes()

        f_total = f_equivalentes
        if fuerzas_nodales_aplicadas is not None:
            if fuerzas_nodales_aplicadas.shape != f_total.shape:
                raise ValueError("El vector de fuerzas_nodales_aplicadas debe tener el mismo tamaño que el vector de DOFs global.")
            f_total += fuerzas_nodales_aplicadas

        K_mod, f_mod = self.aplicar_restricciones(K_global, f_total)

        try:
            u_global = np.linalg.solve(K_mod, f_mod)
        except np.linalg.LinAlgError:
            print("Error: La matriz de rigidez es singular. Revise apoyos o conectividad.")
            u_global = np.zeros(K_mod.shape[0])

        return u_global

    # Los métodos de visualización han sido movidos a VisualizadorPortico
    # Puedes crear métodos "wrapper" si lo deseas, o llamar directamente desde el script principal
    def mostrar_forma_deformada(self, u_global, factor=500):
        self.visualizador.visualizar_estructura_deformada(u_global, factor)

    def mostrar_diagramas_simples(self, u_global, tipo='V', npts=50):
        self.visualizador.graficar_diagramas(u_global, tipo, npts)

    def mostrar_diagramas_superpuestos(self, u_global, tipo='M', escala=0.001, factor=100, npts=100):
        self.visualizador.visualizar_con_diagramas_superpuestos(u_global, tipo, escala, factor, npts)


    def __repr__(self):
        return f"Portico con:\n{self.gestor_modelo}"
