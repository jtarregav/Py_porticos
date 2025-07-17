from Portico import Portico
from Nodo import Nodo
from Barra import Barra
import numpy as np



def main():
    print('Iniciando Programa Portico')

    #crear portico
    p = Portico()
    
    # Crear nodos y guardar sus IDs
    id0 = p.crear_nodo(0, 0, 0)
    id1 = p.crear_nodo(0, 3, 0)
    id2 = p.crear_nodo(3, 3, 0)
    id3 = p.crear_nodo(3, 0, 0)
    id4 = p.crear_nodo(6, 3, 0)
    id5 = p.crear_nodo(6, 0, 0)
   

    

    # Crear barras usando IDs
    idb0 = p.añadir_barra(id0, id1)
    idb1 = p.añadir_barra(id1, id2)
    idb2 = p.añadir_barra(id2, id3)
    idb3 = p.añadir_barra(id2, id4)
    idb4 = p.añadir_barra(id4, id5)
   
    
    

    p.restringir_nodo(id0)
    p.restringir_nodo(id3)
    p.restringir_nodo(id5)


    # Crear matriz de rigidez
    K = p.matriz_rigidez_global()

    # Cargas
    f = np.zeros(K.shape[0])

    #indices
    i1 = list(p.nodos.keys()).index(id1)
    i2 = list(p.nodos.keys()).index(id2)
    i4 = list(p.nodos.keys()).index(id4)

    qb1 = list(p.barras.values())[1]
    qb1.asignar_carga_uniforme(-500)
    

    #Cargas Verticales
    f[3*i1 + 1] = -1000  # fuerza en Y
    f[3*i2 + 1] = -5000  # fuerza en Y
    f[3*i4 + 1] = -3000  # fuerza en Y

    f += p.vector_fuerzas_equivalentes()

    K_mod, f_mod = p.aplicar_restricciones(K, f)


    

    print(p)
    print("\nMatriz de rigidez Global:")
    print(p.matriz_rigidez_global())

    u = np.linalg.solve(K_mod, f_mod)
    print("Desplazamientos y rotaciones:")
    print(u)

    p.visualizar_con_diagramas(u, tipo='M', escala=0.001, factor = 200, npts = 100)
    p.visualizar_con_diagramas(u, tipo='V', escala=0.001, factor = 200, npts = 100)
    

if __name__ == '__main__':
    main()
    
    

    
