class Nodo:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
        #Reactions
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0

        self.mx = 0.0
        self.my = 0.0
        self.mz = 0.0   


        

    def __repr__(self):
        return f"Nodo(x={self.x}, y={self.y}, z={self.z})"
