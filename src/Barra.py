# Barra.py (CONTENIDO SUGERIDO)
import numpy as np
import math
# No necesitas importar Nodo aquí directamente, ya que lo recibes como objeto.


class Barra:
    def __init__(self, nodo1, nodo2, E=210e9, A=0.01, I=1e-6):
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.E = E # modulo de Young
        self.A = A # Area de la barra
        self.I = I # momento de inercia
        self.q = 0 # carga distribuida vertical uniforme (en N/m)
        
    def obtener_L(self):
        """Calcula la longitud de la barra."""
        dx = self.nodo2.x - self.nodo1.x
        dy = self.nodo2.y - self.nodo1.y
        return np.sqrt(dx**2 + dy**2)

    def asignar_carga_uniforme(self, q_val): # Cambié el nombre del parámetro para evitar conflicto con self.q
        """Asigna una carga distribuida vertical uniforme (N/m, hacia abajo)."""
        self.q = q_val

    def obtener_cos_sen(self):
        """Calcula el coseno y el seno del ángulo de la barra con el eje X global."""
        dx = self.nodo2.x - self.nodo1.x
        dy = self.nodo2.y - self.nodo1.y
        L = self.obtener_L()
        if L == 0: # Evitar división por cero para nodos coincidentes (aunque debería manejarse antes)
            return 1.0, 0.0 # O raise ValueError
        c = dx / L
        s = dy / L
        return c, s
    
    def __repr__(self):
        return f"Barra(N{self.nodo1.id}, N{self.nodo2.id}, L={self.obtener_L():.2f}, q={self.q:.2f})"
