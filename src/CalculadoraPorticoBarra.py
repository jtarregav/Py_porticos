import numpy as np
import math
# No necesitas importar Nodo aquí, ya que Barra lo maneja.

class CalculadoraPorticoBarra:
    def __init__(self):
        """
        Constructor de la clase CalculadoraPórticoBarra.
        Esta clase no necesita mantener un estado propio, ya que opera sobre objetos Barra.
        """
        pass

    def _matriz_transformacion_T3(self, barra):
        """
        Calcula la matriz de transformación 3x3 para un grado de libertad (axial o flexión/cortante).
        """
        c, s = barra.obtener_cos_sen()
        return np.array([
            [ c,  s, 0],
            [-s,  c, 0],
            [ 0, 0, 1]
        ])

    def _matriz_transformacion_T6(self, barra):
        """
        Calcula la matriz de transformación 6x6 para la barra completa.
        """
        T3 = self._matriz_transformacion_T3(barra)
        return np.block([
            [T3,        np.zeros((3, 3))],\
            [np.zeros((3, 3)), T3]
        ])

    def rigidez_local_global(self, barra):
        """
        Devuelve la matriz de rigidez de una barra de pórtico 2D (6x6) en coordenadas globales.
        Args:
            barra (Barra): Objeto Barra para el que se calcula la matriz.
        Returns:
            np.ndarray: Matriz de rigidez global (6x6).
        """
        E, A, I, L = barra.E, barra.A, barra.I, barra.obtener_L()

        if L == 0:
            return np.zeros((6, 6))

        # Matriz de rigidez local en coordenadas locales de la barra (axial y flexural)
        # Recordatorio: La convención es [u_axial1, u_vertical1, rot1, u_axial2, u_vertical2, rot2]
        klocal = np.array([
            [E * A / L,             0,              0, -E * A / L,             0,             0],
            [        0,   12 * E * I / L**3,  6 * E * I / L**2,          0,  -12 * E * I / L**3,  6 * E * I / L**2],
            [        0,    6 * E * I / L**2,  4 * E * I / L,           0,   -6 * E * I / L**2,  2 * E * I / L],
            [-E * A / L,            0,              0,   E * A / L,             0,             0],
            [        0,  -12 * E * I / L**3, -6 * E * I / L**2,          0,   12 * E * I / L**3, -6 * E * I / L**2],
            [        0,    6 * E * I / L**2,  2 * E * I / L,           0,   -6 * E * I / L**2,  4 * E * I / L]
        ])

        # Matriz de transformación T6 (global a local)
        T6 = self._matriz_transformacion_T6(barra)

        # Retorno matriz global
        return T6.T @ klocal @ T6

    def fuerzas_equivalentes_locales(self, barra):
        """Fuerzas nodales equivalentes por carga uniforme (en coordenadas LOCALES).
           Asume carga q actuando hacia abajo (en -Y local)
        """
        L = barra.obtener_L()
        q = barra.q # Carga distribuida vertical (en la dirección Y local, si la barra es horizontal)

        # Estas son las fuerzas de empotramiento perfecto debido a la carga uniforme 'q'
        # [Fx1, Fy1, Mz1, Fx2, Fy2, Mz2]
        # Donde q es la carga por unidad de longitud en el sistema de coordenadas local
        # Asumiendo q es positiva para cargas hacia abajo (en dirección -Y local)

        # Para carga uniforme q (positiva hacia abajo en Y local):
        # Fy1 = qL/2
        # Mz1 = qL^2/12 (en sentido antihorario, por convención de momentos)
        # Fy2 = qL/2
        # Mz2 = -qL^2/12 (en sentido horario)

        # Ajuste de signo: Si q en Barra es una carga vertical global,
        # y la barra no es horizontal, 'q' en el sistema local es 'q * cos(theta_barra)'.
        # Pero, para un pórtico 2D, generalmente q se refiere a carga perpendicular a la barra.
        # Si barra.q es una carga externa GLOBAL Y (vertical), su componente local 'qy'
        # dependerá del ángulo. Asumiremos que barra.q ya es la componente local perpendicular
        # si se usa para calcular FEQ locales directamente.
        # En el main_example, q = 20000 N/m es vertical global.
        # Si la barra es horizontal (como la viga), q_local_y = q_global_y.
        # Para una barra vertical (columna), q_local_x = q_global_y si q es vertical.
        # Sin embargo, las FEQ se aplican para carga PERPENDICULAR a la barra (en dirección Y local).
        # Si q es una carga uniforme en la dirección y global, y la barra tiene un ángulo,
        # entonces la componente q perpendicular a la barra es q * cos(theta_barra)
        # y la componente q axial es q * sin(theta_barra).
        # El código actual de Barra asume 'q' es una carga ya orientada o aplicada a barras horizontales.
        # Para simplicidad, se mantiene 'q' como directamente la carga uniforme perpendicular a la barra.
        # Si `barra.q` representa una carga vertical global, para una viga horizontal, `q_local = barra.q`.
        # Para una columna, `q_local = 0` (no hay carga perpendicular si la carga es solo vertical).

        # Aquí, estamos usando barra.q directamente. Esto implica que barra.q ya es
        # la carga uniforme perpendicular al eje local de la barra.
        # Para el ejemplo de la viga horizontal, barra.q = 20000 N/m (hacia abajo global y local Y).
        
        return np.array([
            0,            q * L / 2,   q * L**2 / 12,
            0,            q * L / 2,  -q * L**2 / 12
        ])

    def fuerzas_equivalentes_globales(self, barra):
        """
        Calcula las fuerzas nodales equivalentes de una barra con carga distribuida uniforme
        en coordenadas GLOBALES.
        """
        feq_local = self.fuerzas_equivalentes_locales(barra)
        T6 = self._matriz_transformacion_T6(barra)
        
        # Las fuerzas se transforman de local a global usando la transpuesta de la matriz de transformación
        return T6.T @ feq_local


    def esfuerzos_internos(self, barra, u_global, idn1, idn2, npts=50):
        """Calcula V(x) y M(x) en la barra a lo largo de su longitud"""
        L = barra.obtener_L()
        E, I, q = barra.E, barra.I, barra.q

        if L == 0:
            return np.zeros(npts), np.zeros(npts), np.zeros(npts)

        # Transformación a coordenadas locales
        T6 = self._matriz_transformacion_T6(barra)

        # Obtener vector de desplazamientos de los dos nodos
        dofs = np.array([3*idn1, 3*idn1+1, 3*idn1+2, 3*idn2, 3*idn2+1, 3*idn2+2])
        u_barra_global = u_global[dofs]
        u_local = T6 @ u_barra_global

        # Vector de fuerzas nodales de empotramiento perfecto en coordenadas locales
        feq_local = self.fuerzas_equivalentes_locales(barra)
        # Las reacciones de empotramiento perfecto son las fuerzas que se generan para "detener" la deformación
        # causada por la carga distribuida. Estas son F_izq_y, M_izq_z, F_der_y, M_der_z.
        # Consideramos solo los términos de cortante y momento:
        # Reacciones en Y: feq_local[1] y feq_local[4]
        # Momentos: feq_local[2] y feq_local[5]

        # Posiciones a lo largo de la barra
        x = np.linspace(0, L, npts)

        # --- Cálculo del cortante (V) ---
        # La fórmula general para el cortante V(x) incluye las reacciones por carga distribuida
        # y las reacciones por los desplazamientos de los extremos.
        # V(x) = V_carga(x) + V_desplazamientos(x)
        # V_carga(x) = Reacción inicial debido a q - q*x = q*L/2 - q*x = q*(L/2 - x)
        # V_desplazamientos(x) = V_inicial_por_desplazamientos (constante a lo largo de la barra)
        #                       = (12 * E * I / L**3) * (uy1 - uy2) + (6 * E * I / L**2) * (r1 + r2)

        V = (q * (L / 2 - x)) \
            + (12 * E * I / L**3) * (u_local[1] - u_local[4]) \
            + (6 * E * I / L**2) * (u_local[2] + u_local[5])

        # --- Cálculo del momento flector (M) ---
        # La fórmula general para el momento M(x) incluye el momento por carga distribuida
        # y el momento por los desplazamientos de los extremos.
        # M(x) = M_carga(x) + M_desplazamientos(x)
        # M_carga(x) = q*x*(L-x)/2 (momento parabólico para carga uniforme)
        # M_desplazamientos(x) = (6*EI/L^2)*(uy1 - uy2)*(1-2x/L) + (4*EI/L)*r1*(1-x/L) + (2*EI/L)*r2*(x/L)
        # Mejor usar la fórmula que incluye los momentos y cortantes del extremo izquierdo y la carga q
        # M(x) = M_reaccion_izq - V_reaccion_izq * x + q * x^2 / 2
        # O la forma más común para elementos de viga con FEM y end displacements:
        
        M = (q * x * (L - x) / 2) \
            + (6 * E * I / L**2) * (u_local[1] - u_local[4]) \
            + (2 * E * I / L) * u_local[2] * (2 - 3 * x / L) \
            + (2 * E * I / L) * u_local[5] * (3 * x / L - 1)
            # Nota: La convención de signos para M y los términos r1, r2 aquí puede requerir un ajuste
            # dependiendo de cómo se definen las funciones de forma y los signos de M.
            # Se ha ajustado la fórmula a una forma estándar para el momento en un elemento de viga
            # incluyendo los efectos de desplazamientos y rotaciones en los nudos.
            # Esta fórmula está más en línea con la superposición de soluciones de
            # elemento de viga con cargas puntuales y distribuidas, y deformaciones.


        return x, V, M
