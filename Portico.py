from Nodo import Nodo
from Barra import Barra
import numpy as np
import math
import matplotlib.pyplot as plt




class Portico:
    def __init__(self):
        self.nodos = {}   # Diccionario: id_nodo → Nodo
        self.barras = {}  # Diccionario: id_barra → Barra
        self._id_nodo = 0
        self._id_barra = 0

        self.restricciones = set()  # conjunto de DOFs restringidos

        

    def crear_nodo(self,x,y,z):
        """Crea un nodo con ID único."""
        nodo = Nodo(x, y, z)
        id_nodo = self._id_nodo
        self.nodos[id_nodo] = nodo
        self._id_nodo += 1
        return id_nodo

    def borrar_nodo(self, id_nodo):
        """Elimina un nodo y todas las barras que lo usan."""
        if id_nodo not in self.nodos:
            raise KeyError("ID de nodo no existe.")
        
        # Eliminar las barras conectadas a ese nodo
        self.barras = {
            idb: barra for idb, barra in self.barras.items()
            if barra.nodo1 != self.nodos[id_nodo] and barra.nodo2 != self.nodos[id_nodo]
        }

        del self.nodos[id_nodo]
        
    def añadir_barra(self, id_nodo1, id_nodo2):
        """Crea una barra entre dos nodos dados por sus IDs."""
        if id_nodo1 in self.nodos and id_nodo2 in self.nodos:
            nodo1 = self.nodos[id_nodo1]
            nodo2 = self.nodos[id_nodo2]
            barra = Barra(nodo1, nodo2)
            id_barra = self._id_barra
            self.barras[id_barra] = barra
            self._id_barra += 1
            return id_barra
        else:
            raise KeyError("Uno o ambos IDs de nodo no existen.")

    def borrar_barra(self, id_barra):
        """Elimina una barra por su ID."""
        if id_barra in self.barras:
            del self.barras[id_barra]
        else:
            raise KeyError("ID de barra no existe.")

    def editar_barra(self, id_barra, nuevo_id_nodo1, nuevo_id_nodo2):
        """Reemplaza los nodos de una barra por sus nuevos IDs."""
        if id_barra not in self.barras:
            raise KeyError("ID de barra no existe.")
        if nuevo_id_nodo1 not in self.nodos or nuevo_id_nodo2 not in self.nodos:
            raise KeyError("Uno o ambos IDs de nodo no existen.")
        self.barras[id_barra].nodo1 = self.nodos[nuevo_id_nodo1]
        self.barras[id_barra].nodo2 = self.nodos[nuevo_id_nodo2]

    def matriz_incidencia(self):
        """Devuelve la matriz de incidencia como un numpy.ndarray."""
        n_nodos = len(self.nodos)
        n_barras = len(self.barras)

        # Mapear IDs de nodos a filas (índices)
        id_nodo_to_index = {idn: i for i, idn in enumerate(self.nodos.keys())}
        matriz = np.zeros((n_nodos, n_barras), dtype=int)

        for j, (id_barra, barra) in enumerate(self.barras.items()):
            # Obtener los IDs de los nodos de la barra
            id_nodo1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id_nodo2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            i1 = id_nodo_to_index[id_nodo1]
            i2 = id_nodo_to_index[id_nodo2]

            matriz[i1, j] = +1
            matriz[i2, j] = -1

        return matriz

    def matriz_rigidez_global(self):
        """Genera la matriz de rigidez global 2D con 3 DOFs por nodo (ux, uy, rotación)"""
        n_nodos = len(self.nodos)
        n_dof = 3 * n_nodos
        K = np.zeros((n_dof, n_dof))

        id_to_index = {idn: i for i, idn in enumerate(self.nodos)}

        for id_barra, barra in self.barras.items():
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            # DOFs: [ux1, uy1, θ1, ux2, uy2, θ2]
            dofs = [3*i1, 3*i1+1, 3*i1+2, 3*i2, 3*i2+1, 3*i2+2]

            k_local = barra.rigidez_local_global()

            for i in range(6):
                for j in range(6):
                    K[dofs[i], dofs[j]] += k_local[i, j]

        return K


    def restringir_nodo(self, id_nodo, restringir_x=True, restringir_y=True, restringir_rot=True):
        """Restringe los DOFs de un nodo: desplazamiento x, y, rotación."""
        if id_nodo not in self.nodos:
            raise KeyError("ID de nodo no existe.")

        base = list(self.nodos.keys()).index(id_nodo) * 3
        if restringir_x:
            self.restricciones.add(base)
        if restringir_y:
            self.restricciones.add(base + 1)
        if restringir_rot:
            self.restricciones.add(base + 2)


    def aplicar_restricciones(self, K, f=None):
        """Modifica la matriz K y el vector f para aplicar restricciones."""
        K_mod = K.copy()
        n = K.shape[0]

        if f is None:
            f = np.zeros(n)

        f_mod = f.copy()

        for dof in self.restricciones:
            # Anular fila y columna y poner 1 en la diagonal
            K_mod[dof, :] = 0
            K_mod[:, dof] = 0
            K_mod[dof, dof] = 1
            f_mod[dof] = 0

        return K_mod, f_mod

    def vector_fuerzas_equivalentes(self):
        """Suma todas las fuerzas nodales equivalentes de las cargas distribuidas"""
        n_nodos = len(self.nodos)
        f_eq = np.zeros(3 * n_nodos)

        id_to_index = {idn: i for i, idn in enumerate(self.nodos)}

        for barra in self.barras.values():
            feq = barra.fuerzas_equivalentes_globales()
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            dofs = [3*i1, 3*i1+1, 3*i1+2, 3*i2, 3*i2+1, 3*i2+2]
            for i, dof in enumerate(dofs):
                f_eq[dof] += feq[i]

        return f_eq


    def visualizar(self, desplazamientos, factor=100):
        """Visualiza la estructura original y deformada (2D con rotación)"""
        fig, ax = plt.subplots(figsize=(8, 6))

        # Mapeo de IDs de nodo a índice de desplazamiento
        id_to_index = {idn: i for i, idn in enumerate(self.nodos)}

        # Dibujar cada barra
        for barra in self.barras.values():
            # IDs de nodos
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            # Índices de DOF
            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            ux1, uy1 = desplazamientos[3*i1], desplazamientos[3*i1+1]
            ux2, uy2 = desplazamientos[3*i2], desplazamientos[3*i2+1]

            x1, y1 = barra.nodo1.x, barra.nodo1.y
            x2, y2 = barra.nodo2.x, barra.nodo2.y

            # Dibujar barra original
            ax.plot([x1, x2], [y1, y2], 'k--', lw=1, label='Original' if barra == list(self.barras.values())[0] else "")

            # Dibujar barra deformada
            xd1 = x1 + ux1 * factor
            yd1 = y1 + uy1 * factor
            xd2 = x2 + ux2 * factor
            yd2 = y2 + uy2 * factor

            ax.plot([xd1, xd2], [yd1, yd2], 'b-', lw=2, label='Deformada' if barra == list(self.barras.values())[0] else "")

        ax.set_aspect('equal')
        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.set_title('Estructura: original vs. deformada')
        ax.grid(True)
        ax.legend()
        plt.show()


    def graficar_diagramas(self, u_global, tipo='V', npts=50):
        """Dibuja el diagrama de cortante (V) o momento flector (M)"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        id_to_index = {idn: i for i, idn in enumerate(self.nodos)}

        for barra in self.barras.values():
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            x, V, M = barra.esfuerzos_internos(u_global, id_to_index[id1], id_to_index[id2], npts=npts)
            
            if tipo == 'V':
                ax.plot(np.linspace(0, barra.obtener_L(), npts), V, label=f'Barra {id1}-{id2}')
            elif tipo == 'M':
                ax.plot(np.linspace(0, barra.obtener_L(), npts), M, label=f'Barra {id1}-{id2}')
        
        ax.axhline(0, color='black', lw=0.5)
        ax.set_title('Diagrama de Cortante V(x)' if tipo == 'V' else 'Diagrama de Momento Flector M(x)')
        ax.set_xlabel('x [m]')
        ax.set_ylabel('V [N]' if tipo == 'V' else 'M [Nm]')
        ax.grid(True)
        ax.legend()
        plt.show()

    def visualizar_con_diagramas(self, u_global, tipo='M', escala=0.001, factor=100, npts=100):
        """
        Dibuja el pórtico original, la forma deformada y el diagrama interno (M o V)
        
        Parámetros:
        - u_global: vector de desplazamientos globales
        - tipo: 'M' para momento flector, 'V' para cortante
        - escala: escala del diagrama de esfuerzos
        - factor: amplificación de deformación
        - npts: número de puntos interpolados por barra
        """
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(10, 6))
        id_to_index = {idn: i for i, idn in enumerate(self.nodos)}

        # Dibujar estructura original (línea punteada)
        for barra in self.barras.values():
            x0, y0 = barra.nodo1.x, barra.nodo1.y
            x1, y1 = barra.nodo2.x, barra.nodo2.y
            ax.plot([x0, x1], [y0, y1], 'k--', lw=1.5, label='Original', zorder=1)

        # Dibujar nodos originales
        for nodo in self.nodos.values():
            ax.plot(nodo.x, nodo.y, 'ko', markersize=4)

        # Dibujar estructura deformada (interpolada)
        for barra in self.barras.values():
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            i1 = id_to_index[id1]
            i2 = id_to_index[id2]

            u_elem = np.concatenate([
                u_global[3*i1:3*i1+3],
                u_global[3*i2:3*i2+3]
            ])  # ux1, uy1, r1, ux2, uy2, r2

            # Coordenadas originales
            x0, y0 = barra.nodo1.x, barra.nodo1.y
            x1, y1 = barra.nodo2.x, barra.nodo2.y
            dx, dy = x1 - x0, y1 - y0
            L = np.sqrt(dx**2 + dy**2)
            cosθ, sinθ = dx / L, dy / L

            # Matriz de transformación
            T = np.array([
                [cosθ, sinθ, 0],
                [-sinθ, cosθ, 0],
                [0, 0, 1]
            ])
            T6 = np.block([
                [T, np.zeros((3, 3))],
                [np.zeros((3, 3)), T]
            ])
            u_local = T6 @ u_elem  # Desplazamientos en coordenadas locales

            # Dibujar curva deformada
            xs, ys = [], []
            for xi in np.linspace(0, L, npts):
                N1 = 1 - 3*(xi/L)**2 + 2*(xi/L)**3
                N2 = xi - 2*(xi**2)/L + (xi**3)/(L**2)
                N3 = 3*(xi/L)**2 - 2*(xi/L)**3
                N4 = - (xi**2)/L + (xi**3)/(L**2)

                uy = (N1 * u_local[1] +
                      N2 * u_local[2] +
                      N3 * u_local[4] +
                      N4 * u_local[5])

                # Coordenadas globales del punto deformado
                xg = x0 + xi * cosθ - factor * uy * sinθ
                yg = y0 + xi * sinθ + factor * uy * cosθ

                xs.append(xg)
                ys.append(yg)

            ax.plot(xs, ys, color='green', lw=2.5, zorder=2, label='Deformado')

        # Dibujar diagramas de momento/cortante
        for barra in self.barras.values():
            id1 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo1)
            id2 = next(idn for idn, nodo in self.nodos.items() if nodo == barra.nodo2)

            x, V, M = barra.esfuerzos_internos(u_global, id_to_index[id1], id_to_index[id2], npts=npts)

            # Coordenadas deformadas de nodos
            u1 = u_global[3*id_to_index[id1]:3*id_to_index[id1]+2]
            u2 = u_global[3*id_to_index[id2]:3*id_to_index[id2]+2]

            x0 = barra.nodo1.x + factor * u1[0]
            y0 = barra.nodo1.y + factor * u1[1]
            x1 = barra.nodo2.x + factor * u2[0]
            y1 = barra.nodo2.y + factor * u2[1]

            dx = x1 - x0
            dy = y1 - y0
            L = np.sqrt(dx**2 + dy**2)
            tangente = np.array([dx, dy]) / L
            normal = np.array([-dy, dx]) / L

            valores = M if tipo == 'M' else V
            color = 'blue' if tipo == 'M' else 'red'

            for i in range(npts):
                xi = x[i]
                val = valores[i]
                px = x0 + xi * tangente[0] + escala * val * normal[0]
                py = y0 + xi * tangente[1] + escala * val * normal[1]
                if i > 0:
                    ax.plot([px_ant, px], [py_ant, py], color=color, lw=2, alpha=0.8, zorder=3)
                px_ant, py_ant = px, py

        ax.set_aspect('equal')
        ax.set_title(f"Pórtico deformado con diagrama de {'Momento flector' if tipo == 'M' else 'Cortante'}")
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        ax.grid(True)
        ax.legend(loc='best')
        plt.show()


        

    def __repr__(self):
        resumen_nodos = "\n".join(f"{idn}: {n}" for idn, n in self.nodos.items())
        resumen_barras = "\n".join(f"{idb}: {b}" for idb, b in self.barras.items())
        return f"Portico con {len(self.nodos)} nodos y {len(self.barras)} barras:\n\n" + \
               "NODOS:\n" + resumen_nodos + "\n\nBARRAS:\n" + resumen_barras

    
    
                
                


                      



        
        

        

               

        
        
                


    



    
