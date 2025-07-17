# visualizador_portico.py
import numpy as np
import matplotlib.pyplot as plt
import math

# Esta clase no importa directamente GestorDeModelo o CalculadoraPorticoBarra,
# sino que recibe instancias de estas clases en su constructor.

class VisualizadorPortico:
    def __init__(self, gestor_modelo, calculadora_barra):
        """
        Constructor de la clase VisualizadorPortico.
        Args:
            gestor_modelo (GestorDeModelo): Una instancia del GestorDeModelo que contiene los datos del modelo.
            calculadora_barra (CalculadoraPorticoBarra): Una instancia de CalculadoraPorticoBarra para cálculos.
        """
        self.gestor_modelo = gestor_modelo
        self.calculadora_barra = calculadora_barra

    def visualizar_estructura_deformada(self, u_global, factor=500):
        """
        Visualiza la estructura original y deformada (2D con rotación).
        Args:
            u_global (np.ndarray): Vector de desplazamientos globales.
            factor (float): Factor de amplificación para los desplazamientos (para hacerlos visibles).
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        nodos = self.gestor_modelo.get_nodos()
        barras = self.gestor_modelo.get_barras()
        id_to_index = self.gestor_modelo.get_dof_map()

        for id_barra, barra in barras.items():
            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            # Desplazamientos globales de los nodos de la barra
            ux1, uy1 = u_global[3*i1], u_global[3*i1+1]
            ux2, uy2 = u_global[3*i2], u_global[3*i2+1]

            # Coordenadas originales
            x1, y1 = barra.nodo1.x, barra.nodo1.y
            x2, y2 = barra.nodo2.x, barra.nodo2.y

            # Dibujar barra original (línea punteada)
            ax.plot([x1, x2], [y1, y2], 'k--', lw=1,
                    label='Original' if id_barra == sorted(list(barras.keys()))[0] else "")

            # Coordenadas deformadas
            xd1 = x1 + ux1 * factor
            yd1 = y1 + uy1 * factor
            xd2 = x2 + ux2 * factor
            yd2 = y2 + uy2 * factor

            # Dibujar barra deformada (línea sólida)
            ax.plot([xd1, xd2], [yd1, yd2], 'b-', lw=2,
                    label='Deformada' if id_barra == sorted(list(barras.keys()))[0] else "")

        # Configuración del gráfico
        ax.set_aspect('equal')
        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.set_title('Estructura: original vs. deformada')
        ax.grid(True)
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        plt.show()

    def graficar_diagramas(self, u_global, tipo='V', npts=50):
        """
        Dibuja el diagrama de cortante (V) o momento flector (M) para todas las barras.
        Args:
            u_global (np.ndarray): Vector de desplazamientos globales.
            tipo (str): 'V' para cortante, 'M' para momento flector.
            npts (int): Número de puntos para interpolar a lo largo de cada barra.
        """
        fig, ax = plt.subplots(figsize=(10, 4))

        nodos = self.gestor_modelo.get_nodos()
        barras = self.gestor_modelo.get_barras()
        id_to_index = self.gestor_modelo.get_dof_map()

        for id_barra, barra in barras.items():
            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            # Delegar el cálculo de esfuerzos internos a CalculadoraPorticoBarra
            x, V, M = self.calculadora_barra.esfuerzos_internos(barra, u_global, id_to_index[id1], id_to_index[id2], npts=npts)

            if tipo == 'V':
                ax.plot(x, V, label=f'Barra {id1}-{id2}')
            elif tipo == 'M':
                ax.plot(x, M, label=f'Barra {id1}-{id2}')
            else:
                raise ValueError("Tipo de diagrama no válido. Use 'V' para cortante o 'M' para momento.")

        # Configuración del gráfico
        ax.axhline(0, color='black', lw=0.5)
        ax.set_title('Diagrama de Cortante V(x)' if tipo == 'V' else 'Diagrama de Momento Flector M(x)')
        ax.set_xlabel('x local de la barra [m]')
        ax.set_ylabel('V [N]' if tipo == 'V' else 'M [Nm]')
        ax.grid(True)
        ax.legend()
        plt.show()

    def visualizar_con_diagramas_superpuestos(self, u_global, tipo='M', escala=0.001, factor=100, npts=100):
        """
        Dibuja el pórtico original, la forma deformada y el diagrama interno (M o V) superpuesto.
        Los diagramas se dibujan perpendicularmente a la forma deformada de la barra.

        Args:
            u_global (np.ndarray): Vector de desplazamientos globales.
            tipo (str): 'M' para momento flector, 'V' para cortante.
            escala (float): Factor de escala para el diagrama de esfuerzos (ajustar para visibilidad).
            factor (float): Factor de amplificación para la forma deformada.
            npts (int): Número de puntos para interpolar a lo largo de cada barra.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        nodos = self.gestor_modelo.get_nodos()
        barras = self.gestor_modelo.get_barras()
        id_to_index = self.gestor_modelo.get_dof_map()

        # Dibujar estructura original (línea punteada)
        for id_barra, barra in barras.items():
            x0, y0 = barra.nodo1.x, barra.nodo1.y
            x1, y1 = barra.nodo2.x, barra.nodo2.y
            ax.plot([x0, x1], [y0, y1], 'k--', lw=1.5,
                    label='Original' if id_barra == sorted(list(barras.keys()))[0] else "", zorder=1)

        # Dibujar nodos originales
        for nodo in nodos.values():
            ax.plot(nodo.x, nodo.y, 'ko', markersize=4)

        # Dibujar estructura deformada (interpolada)
        for id_barra, barra in barras.items():
            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            u_elem = np.concatenate([
                u_global[3*i1:3*i1+3],
                u_global[3*i2:3*i2+3]
            ])  # ux1, uy1, r1, ux2, uy2, r2

            x0, y0 = barra.nodo1.x, barra.nodo1.y
            x1, y1 = barra.nodo2.x, barra.nodo2.y
            dx, dy = x1 - x0, y1 - y0
            L_original = np.sqrt(dx**2 + dy**2)
            if L_original == 0:
                continue
            cosθ, sinθ = dx / L_original, dy / L_original

            # Transformar desplazamientos a coordenadas locales de la barra
            u_local = self.calculadora_barra._matriz_transformacion_T6(barra) @ u_elem

            xs_deformed, ys_deformed = [], []
            for xi_local_original in np.linspace(0, L_original, npts):
                # Funciones de forma cúbicas de Hermite para interpolación de uy local
                N1 = 1 - 3*(xi_local_original/L_original)**2 + 2*(xi_local_original/L_original)**3
                N2 = xi_local_original - 2*(xi_local_original**2)/L_original + (xi_local_original**3)/(L_original**2)
                N3 = 3*(xi_local_original/L_original)**2 - 2*(xi_local_original/L_original)**3
                N4 = - (xi_local_original**2)/L_original + (xi_local_original**3)/(L_original**2)

                uy_interp_local = (N1 * u_local[1] +  # uy1
                                   N2 * u_local[2] +  # rz1 * L
                                   N3 * u_local[4] +  # uy2
                                   N4 * u_local[5])   # rz2 * L

                # Coordenadas globales del punto en la barra DEFORMADA
                # Se utiliza el ángulo original de la barra para mapear la posición,
                # y luego se aplica el desplazamiento local amplificado.
                xg_deformed_point = x0 + xi_local_original * cosθ - factor * uy_interp_local * sinθ
                yg_deformed_point = y0 + xi_local_original * sinθ + factor * uy_interp_local * cosθ

                xs_deformed.append(xg_deformed_point)
                ys_deformed.append(yg_deformed_point)

            ax.plot(xs_deformed, ys_deformed, color='green', lw=2.5, zorder=2,
                    label='Deformado' if id_barra == sorted(list(barras.keys()))[0] else "")

        # Dibujar diagramas de momento/cortante sobre la estructura deformada
        for id_barra, barra in barras.items():
            id1 = barra.nodo1.id
            id2 = barra.nodo2.id

            # Delegar el cálculo de esfuerzos internos a CalculadoraPorticoBarra
            # 'x' aquí son las coordenadas locales a lo largo de la barra original
            x_local_bar, V, M = self.calculadora_barra.esfuerzos_internos(barra, u_global, id_to_index[id1], id_to_index[id2], npts=npts)

            # Calcular el vector normal a la barra DEFORMADA
            u1_deformed_x = barra.nodo1.x + factor * u_global[3*id_to_index[id1]]
            u1_deformed_y = barra.nodo1.y + factor * u_global[3*id_to_index[id1]+1]
            u2_deformed_x = barra.nodo2.x + factor * u_global[3*id_to_index[id2]]
            u2_deformed_y = barra.nodo2.y + factor * u_global[3*id_to_index[id2]+1]

            dx_def = u2_deformed_x - u1_deformed_x
            dy_def = u2_deformed_y - u1_deformed_y
            L_deformed_segment = np.sqrt(dx_def**2 + dy_def**2) # Longitud del segmento deformado
            if L_deformed_segment == 0:
                continue
            # La tangente y normal de la barra deformada (asumiendo recta entre nodos deformados)
            tangente_def = np.array([dx_def, dy_def]) / L_deformed_segment
            normal_def = np.array([-dy_def, dx_def]) / L_deformed_segment # Normal apunta "hacia arriba" desde la barra

            valores = M if tipo == 'M' else V
            color = 'blue' if tipo == 'M' else 'red'

            # Dibujar el diagrama
            px_ant, py_ant = None, None
            for i in range(npts):
                xi_original_local = x_local_bar[i]
                val = valores[i]

                # Obtener el punto correspondiente en la curva deformada de la barra
                # Reutilizar el cálculo de la posición deformed_point_x/y
                # Esto es crucial para que el diagrama se pegue a la forma deformada
                N1_pt = 1 - 3*(xi_original_local/L_original)**2 + 2*(xi_original_local/L_original)**3
                N2_pt = xi_original_local - 2*(xi_original_local**2)/L_original + (xi_original_local**3)/(L_original**2)
                N3_pt = 3*(xi_original_local/L_original)**2 - 2*(xi_original_local/L_original)**3
                N4_pt = - (xi_original_local**2)/L_original + (xi_original_local**3)/(L_original**2)

                uy_interp_local_pt = (N1_pt * u_local[1] +
                                      N2_pt * u_local[2] +
                                      N3_pt * u_local[4] +
                                      N4_pt * u_local[5])

                xg_deformed_point = x0 + xi_original_local * cosθ - factor * uy_interp_local_pt * sinθ
                yg_deformed_point = y0 + xi_original_local * sinθ + factor * uy_interp_local_pt * cosθ

                # Calcular el punto final del vector del diagrama
                px = xg_deformed_point + escala * val * normal_def[0]
                py = yg_deformed_point + escala * val * normal_def[1]

                if i > 0:
                    ax.plot([px_ant, px], [py_ant, py], color=color, lw=2, alpha=0.8, zorder=3)
                px_ant, py_ant = px, py

        # Configuración del gráfico
        ax.set_aspect('equal')
        ax.set_title(f"Pórtico deformado con diagrama de {'Momento flector' if tipo == 'M' else 'Cortante'}")
        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.grid(True)
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='best')
        plt.show()
