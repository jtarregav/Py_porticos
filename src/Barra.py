import Nodo
import math
import numpy as np



class Barra:
    def __init__(self, nodo1, nodo2, E=210e9, A=0.01,I=1e-6):
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.E = E #modulo de young
        self.A = A #Area de la barra
        self.I = I #momento de inercia
        self.q = 0 #carga distribuida vertical uniforme (en N/m)
        
    def obtener_L(self):
        dx = self.nodo2.x - self.nodo1.x
        dy = self.nodo2.y - self.nodo1.y
        return np.sqrt(dx**2 + dy**2)


    def asignar_carga_uniforme(self,q):
        """Carga distribuida vertical uniforme (N/m, hacia abajo)"""
        self.q = q

    def fuerzas_equivalentes_locales(self):
        """Fuerzas nodales equivalentes por carga uniforme (en coordenadas LOCALES)"""
        L = self.obtener_L()
        q = self.q
        # Solo vertical (local Y) y momento flector
        return np.array([
            0,        q * L / 2,   q * L**2 / 12,
            0,        q * L / 2,  -q * L**2 / 12
        ])

    def fuerzas_equivalentes_globales(self):
        """Transforma las fuerzas equivalentes locales a globales"""
        f_local = self.fuerzas_equivalentes_locales()
        c, s = self.obtener_cos_sen()

        # Matriz de transformación 3x3
        T = np.array([
            [ c,  s, 0],
            [-s,  c, 0],
            [ 0, 0, 1]
        ])
        T6 = np.block([
            [T,        np.zeros((3, 3))],
            [np.zeros((3, 3)), T]
        ])

        return T6 @ f_local
    

    def obtener_cos_sen(self):
        dx = self.nodo2.x - self.nodo1.x
        dy = self.nodo2.y - self.nodo1.y
        L = self.obtener_L()
        c = dx / L
        s = dy / L
        return c, s

    
    def rigidez_local_global(self):
        """Devuelve la matriz de rigidez de una barra de pórtico 2D (6x6) en coordenadas globales"""
        L = self.obtener_L()
        c, s = self.obtener_cos_sen()
        A = self.A
        E = self.E
        I = self.I

        # Matriz de rigidez local (en coordenadas locales)
        k = E / L
        klocal = k * np.array([
            [ A,     0,           0,     -A,     0,           0],
            [ 0,  12*I/L**2,  6*I/L,     0, -12*I/L**2,  6*I/L],
            [ 0,   6*I/L,     4*I,       0,  -6*I/L,     2*I],
            [-A,     0,           0,      A,     0,           0],
            [ 0, -12*I/L**2, -6*I/L,     0,  12*I/L**2, -6*I/L],
            [ 0,   6*I/L,     2*I,       0,  -6*I/L,     4*I],
        ])

        # Matriz de transformación
        T = np.array([
            [ c,  s, 0],
            [-s,  c, 0],
            [ 0, 0, 1]
        ])

        # Matriz de transformación extendida (6x6)
        T6 = np.block([
            [T,        np.zeros((3, 3))],
            [np.zeros((3, 3)), T]
        ])

        # Retorno matriz global
        return T6.T @ klocal @ T6

    def esfuerzos_internos(self, u_global, idn1, idn2, npts=50):
        """Calcula V(x) y M(x) en la barra a lo largo de su longitud"""
        L = self.obtener_L()
        c, s = self.obtener_cos_sen()

        # Transformación
        T = np.array([
            [ c,  s, 0],
            [-s,  c, 0],
            [ 0,  0, 1]
        ])
        T6 = np.block([
            [T, np.zeros((3, 3))],
            [np.zeros((3, 3)), T]
        ])

        # Obtener vector de desplazamientos de los dos nodos
        dofs = np.array([3*idn1, 3*idn1+1, 3*idn1+2, 3*idn2, 3*idn2+1, 3*idn2+2])
        u_barra_global = u_global[dofs]
        u_local = T6 @ u_barra_global

        q = self.q
        E, I = self.E, self.I

        # Posiciones a lo largo de la barra
        x = np.linspace(0, L, npts)

        # Cálculo del momento y cortante
        V = q * (L / 2 - x) + 12 * E * I / L**3 * (u_local[1] - u_local[4]) \
            + 6 * E * I / L**2 * (u_local[2] + u_local[5])
        
        M = (q * x * (L - x) / 2) \
            - 6 * E * I / L**2 * (u_local[1] - u_local[4]) * x \
            - 2 * E * I / L * u_local[2] * (1 - 3 * x / L + 2 * x**2 / L**2) \
            + 2 * E * I / L * u_local[5] * (3 * x / L - 2 * x**2 / L**2)

        return x, V, M

                    
            

    def __repr__(self):
        return f"Barra({self.nodo1}, {self.nodo2})"
