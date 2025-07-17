# main_example.py (Actualizado para usar VisualizadorPortico)
from Portico import Portico
import numpy as np

# -----------------------------------------------------------------------------
# 1. Crear una instancia del Pórtico
#    El Portico ahora contendrá un GestorDeModelo y un VisualizadorPortico internamente.
# -----------------------------------------------------------------------------
mi_portico = Portico()
print("--- Pórtico inicial ---")
print(mi_portico)

# -----------------------------------------------------------------------------
# 2. Definir la geometría y las propiedades del modelo usando GestorDeModelo
#    El Portico delega estas operaciones a su gestor_modelo.
# -----------------------------------------------------------------------------

# Crear Nodos
id_n0 = mi_portico.gestor_modelo.crear_nodo(0, 0, 0) # Nodo 0
id_n1 = mi_portico.gestor_modelo.crear_nodo(4, 0, 0) # Nodo 1
id_n2 = mi_portico.gestor_modelo.crear_nodo(4, 3, 0) # Nodo 2
id_n3 = mi_portico.gestor_modelo.crear_nodo(0, 3, 0) # Nodo 3

print("\n--- Nodos creados ---")
for id_n, nodo in mi_portico.gestor_modelo.get_nodos().items():
    print(f"ID: {id_n}, {nodo}")

# Añadir Barras (columnas y viga)
# Valores típicos de acero: E=210 GPa, A=0.01 m^2, I=1e-5 m^4
E_acero = 210e9 # Pa
A_col = 0.005  # m^2 (50 cm^2)
I_col = 1e-5   # m^4 (1000 cm^4)
A_viga = 0.008 # m^2 (80 cm^2)
I_viga = 2e-5  # m^4 (2000 cm^4)

id_b0 = mi_portico.gestor_modelo.añadir_barra(id_n0, id_n3, E=E_acero, A=A_col, I=I_col) # Columna izquierda
id_b1 = mi_portico.gestor_modelo.añadir_barra(id_n1, id_n2, E=E_acero, A=A_col, I=I_col) # Columna derecha
id_b2 = mi_portico.gestor_modelo.añadir_barra(id_n3, id_n2, E=E_acero, A=A_viga, I=I_viga) # Viga superior

print("\n--- Barras creadas ---")
for id_b, barra in mi_portico.gestor_modelo.get_barras().items():
    print(f"ID: {id_b}, {barra}")

# Asignar cargas (a través de la barra obtenida del gestor)
# Carga uniforme en la viga (20 kN/m hacia abajo)
mi_portico.gestor_modelo.barras[id_b2].asignar_carga_uniforme(-20000) # 20 kN/m = 20000 N/m

# -----------------------------------------------------------------------------
# 3. Aplicar Restricciones (apoyos) usando GestorDeModelo
# -----------------------------------------------------------------------------
# Empotramiento en la base de las columnas (Nodos 0 y 1)
mi_portico.gestor_modelo.restringir_nodo(id_n0, restringir_x=True, restringir_y=True, restringir_rot=True)
mi_portico.gestor_modelo.restringir_nodo(id_n1, restringir_x=True, restringir_y=True, restringir_rot=True)

print("\n--- Restricciones aplicadas ---")
print(mi_portico.gestor_modelo)


# -----------------------------------------------------------------------------
# 4. Realizar el Análisis Estructural
#    El método analizar() de Portico orquesta el ensamblaje, restricciones y resolución.
# -----------------------------------------------------------------------------
print("\n--- Realizando análisis estructural ---")
desplazamientos_globales = mi_portico.analizar()

print("\n--- Desplazamientos Globales (u_global) ---")
dof_map = mi_portico.gestor_modelo.get_dof_map()
for id_n, idx_in_dof in dof_map.items():
    print(f"Nodo {id_n}:")
    print(f"  ux = {desplazamientos_globales[3*idx_in_dof]:.6e} m")
    print(f"  uy = {desplazamientos_globales[3*idx_in_dof+1]:.6e} m")
    print(f"  rz = {desplazamientos_globales[3*idx_in_dof+2]:.6e} rad")


# -----------------------------------------------------------------------------
# 5. Visualizar Resultados usando la clase VisualizadorPortico
#    Ahora las llamadas se hacen a través de la instancia de visualizador
#    que está dentro del objeto mi_portico.
# -----------------------------------------------------------------------------
print("\n--- Visualizando resultados ---")

# Visualizar la forma deformada (factor de amplificación para que sea visible)
mi_portico.mostrar_forma_deformada(desplazamientos_globales, factor=500) # Llama a self.visualizador.visualizar_estructura_deformada

# Visualizar diagramas de Momento Flector superpuestos
mi_portico.mostrar_diagramas_superpuestos(desplazamientos_globales, tipo='M', escala=0.00001, factor=500)

# Visualizar diagramas de Cortante superpuestos
mi_portico.mostrar_diagramas_superpuestos(desplazamientos_globales, tipo='V', escala=0.00001, factor=500)

# También puedes usar los diagramas simples si quieres
# mi_portico.mostrar_diagramas_simples(desplazamientos_globales, tipo='M')
# mi_portico.mostrar_diagramas_simples(desplazamientos_globales, tipo='V')

print("\nEjemplo de uso completado con VisualizadorPortico.")
