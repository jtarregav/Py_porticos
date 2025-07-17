# gestor_modelo.py
from Nodo import Nodo
from Barra import Barra
import numpy as np # Necesario para numpy.array si se usa en alguna parte (ej. en restricciones más complejas)

class GestorDeModelo:
    def __init__(self):
        self.nodos = {}   # Diccionario: id_nodo → Nodo
        self.barras = {}  # Diccionario: id_barra → Barra
        self.restricciones = set()  # Conjunto de DOFs restringidos (índices globales)

        self._next_node_id = 0
        self._next_barra_id = 0

    def crear_nodo(self, x, y, z=0.0):
        id_nodo = self._next_node_id
        nodo = Nodo(id_nodo, x, y, z) # Pasar el ID al constructor del Nodo
        self.nodos[id_nodo] = nodo
        self._next_node_id += 1
        return id_nodo

    def borrar_nodo(self, id_nodo):
        """
        Elimina un nodo y todas las barras conectadas a él.
        También remueve las restricciones asociadas a ese nodo.
        Args:
            id_nodo (int): ID del nodo a borrar.
        Raises:
            KeyError: Si el ID del nodo no existe.
        """
        if id_nodo not in self.nodos:
            raise KeyError(f"Error: El nodo con ID {id_nodo} no existe.")
        
        # Identificar y borrar las barras conectadas a este nodo
        barras_a_borrar_ids = [
            id_b for id_b, barra in self.barras.items()
            if barra.nodo1 == self.nodos[id_nodo] or barra.nodo2 == self.nodos[id_nodo]
        ]
        for id_b in barras_a_borrar_ids:
            del self.barras[id_b]
        
        # Eliminar restricciones asociadas a este nodo
        # Necesitamos saber el índice del nodo en el orden global para eliminar DOFs
        sorted_node_ids = sorted(self.nodos.keys())
        if id_nodo in sorted_node_ids: # Asegurarse de que el nodo todavía está en la lista ordenada antes de borrarlo
            node_index = sorted_node_ids.index(id_nodo)
            dofs_to_remove = {3*node_index, 3*node_index + 1, 3*node_index + 2}
            self.restricciones = self.restricciones - dofs_to_remove

        del self.nodos[id_nodo]
        print(f"Nodo {id_nodo} y sus barras asociadas han sido borrados.")


    def añadir_barra(self, id_nodo1, id_nodo2, E=210e9, A=0.01, I=1e-6):
        """
        Crea una barra entre dos nodos existentes y la añade al modelo.
        Args:
            id_nodo1 (int): ID del nodo inicial de la barra.
            id_nodo2 (int): ID del nodo final de la barra.
            E (float): Módulo de elasticidad del material.
            A (float): Área de la sección transversal de la barra.
            I (float): Momento de inercia de la sección transversal de la barra.
        Returns:
            int: El ID único de la barra creada.
        Raises:
            KeyError: Si uno o ambos IDs de nodo no existen.
            ValueError: Si los nodos son idénticos.
        """
        if id_nodo1 not in self.nodos:
            raise KeyError(f"Error: El nodo con ID {id_nodo1} no existe.")
        if id_nodo2 not in self.nodos:
            raise KeyError(f"Error: El nodo con ID {id_nodo2} no existe.")
        if id_nodo1 == id_nodo2:
            raise ValueError("Error: No se puede crear una barra entre el mismo nodo.")

        nodo1_obj = self.nodos[id_nodo1]
        nodo2_obj = self.nodos[id_nodo2]
        
        barra = Barra(nodo1_obj, nodo2_obj, E, A, I)
        id_barra = self._next_barra_id
        self.barras[id_barra] = barra
        self._next_barra_id += 1
        return id_barra

    def borrar_barra(self, id_barra):
        """
        Elimina una barra del modelo por su ID.
        Args:
            id_barra (int): ID de la barra a borrar.
        Raises:
            KeyError: Si el ID de la barra no existe.
        """
        if id_barra not in self.barras:
            raise KeyError(f"Error: La barra con ID {id_barra} no existe.")
        del self.barras[id_barra]
        print(f"Barra {id_barra} ha sido borrada.")

    def editar_barra(self, id_barra, nuevo_id_nodo1=None, nuevo_id_nodo2=None, E=None, A=None, I=None):
        """
        Edita una barra existente cambiando sus nodos o propiedades.
        Args:
            id_barra (int): ID de la barra a editar.
            nuevo_id_nodo1 (int, optional): Nuevo ID del nodo inicial. No cambia si es None.
            nuevo_id_nodo2 (int, optional): Nuevo ID del nodo final. No cambia si es None.
            E (float, optional): Nuevo módulo de elasticidad. No cambia si es None.
            A (float, optional): Nueva área de la sección. No cambia si es None.
            I (float, optional): Nuevo momento de inercia. No cambia si es None.
        Raises:
            KeyError: Si la barra o alguno de los nuevos nodos no existen.
            ValueError: Si los nuevos nodos son idénticos.
        """
        if id_barra not in self.barras:
            raise KeyError(f"Error: La barra con ID {id_barra} no existe.")
        
        barra = self.barras[id_barra]

        if nuevo_id_nodo1 is not None:
            if nuevo_id_nodo1 not in self.nodos:
                raise KeyError(f"Error: El nuevo nodo inicial con ID {nuevo_id_nodo1} no existe.")
            barra.nodo1 = self.nodos[nuevo_id_nodo1]

        if nuevo_id_nodo2 is not None:
            if nuevo_id_nodo2 not in self.nodos:
                raise KeyError(f"Error: El nuevo nodo final con ID {nuevo_id_nodo2} no existe.")
            barra.nodo2 = self.nodos[nuevo_id_nodo2]

        if nuevo_id_nodo1 is not None and nuevo_id_nodo2 is not None and nuevo_id_nodo1 == nuevo_id_nodo2:
            raise ValueError("Error: Los nuevos nodos de la barra no pueden ser idénticos.")

        if E is not None:
            barra.E = E
        if A is not None:
            barra.A = A
        if I is not None:
            barra.I = I
        print(f"Barra {id_barra} ha sido editada.")


    def restringir_nodo(self, id_nodo, restringir_x=False, restringir_y=False, restringir_rot=False):
        """
        Añade restricciones a los grados de libertad de un nodo.
        Los DOFs se añaden al conjunto 'restricciones' como índices globales.
        Args:
            id_nodo (int): ID del nodo a restringir.
            restringir_x (bool): True para restringir desplazamiento en X.
            restringir_y (bool): True para restringir desplazamiento en Y.
            restringir_rot (bool): True para restringir rotación en Z.
        Raises:
            KeyError: Si el ID del nodo no existe.
        """
        if id_nodo not in self.nodos:
            raise KeyError(f"Error: El nodo con ID {id_nodo} no existe.")

        # Es crucial que el orden de los nodos sea consistente para mapear IDs a índices de DOF.
        # sorted(self.nodos.keys()) asegura un orden fijo basado en los IDs numéricos.
        sorted_node_ids = sorted(self.nodos.keys())
        if id_nodo not in sorted_node_ids: # Puede pasar si el nodo fue borrado pero el ID no se actualizó
            raise ValueError(f"Error interno: El nodo {id_nodo} no está en la lista de nodos ordenados.")
            
        node_index_in_dofs = sorted_node_ids.index(id_nodo)
        
        base_dof = node_index_in_dofs * 3 # DOF inicial para este nodo (ux, uy, rz)
        if restringir_x:
            self.restricciones.add(base_dof)
        if restringir_y:
            self.restricciones.add(base_dof + 1)
        if restringir_rot:
            self.restricciones.add(base_dof + 2)
        print(f"Restricciones aplicadas al nodo {id_nodo}.")

    def eliminar_restriccion_nodo(self, id_nodo, liberar_x=False, liberar_y=False, liberar_rot=False):
        """
        Elimina restricciones a los grados de libertad de un nodo.
        Args:
            id_nodo (int): ID del nodo a liberar.
            liberar_x (bool): True para liberar desplazamiento en X.
            liberar_y (bool): True para liberar desplazamiento en Y.
            liberar_rot (bool): True para liberar rotación en Z.
        Raises:
            KeyError: Si el ID del nodo no existe.
        """
        if id_nodo not in self.nodos:
            raise KeyError(f"Error: El nodo con ID {id_nodo} no existe.")

        sorted_node_ids = sorted(self.nodos.keys())
        if id_nodo not in sorted_node_ids:
            raise ValueError(f"Error interno: El nodo {id_nodo} no está en la lista de nodos ordenados.")
            
        node_index_in_dofs = sorted_node_ids.index(id_nodo)
        
        base_dof = node_index_in_dofs * 3
        if liberar_x and (base_dof in self.restricciones):
            self.restricciones.remove(base_dof)
        if liberar_y and (base_dof + 1 in self.restricciones):
            self.restricciones.remove(base_dof + 1)
        if liberar_rot and (base_dof + 2 in self.restricciones):
            self.restricciones.remove(base_dof + 2)
        print(f"Restricciones liberadas en el nodo {id_nodo}.")


    def get_nodos(self):
        """Devuelve el diccionario de nodos del modelo."""
        return self.nodos

    def get_barras(self):
        """Devuelve el diccionario de barras del modelo."""
        return self.barras

    def get_restricciones(self):
        """Devuelve el conjunto de DOFs restringidos."""
        return self.restricciones

    def get_dof_map(self):
        """
        Devuelve un mapeo de ID de nodo a su índice base en el vector de DOFs globales.
        Esencial para el ensamblaje matricial.
        Returns:
            dict: {id_nodo: index_en_dofs}
        """
        sorted_node_ids = sorted(self.nodos.keys())
        return {idn: i for i, idn in enumerate(sorted_node_ids)}

    def __repr__(self):
        resumen_nodos = "\n".join(f"  {idn}: {n}" for idn, n in self.nodos.items())
        resumen_barras = "\n".join(f"  {idb}: {b}" for idb, b in self.barras.items())
        resumen_restricciones = ", ".join(map(str, sorted(list(self.restricciones)))) if self.restricciones else "Ninguna"
        
        return (f"--- GestorDeModelo ---\n"
                f"Nodos ({len(self.nodos)}):\n{resumen_nodos}\n\n"
                f"Barras ({len(self.barras)}):\n{resumen_barras}\n\n"
                f"DOFs Restringidos: {resumen_restricciones}\n"
                f"--------------------")
