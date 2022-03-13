# Código obtenido de https://code.activestate.com/recipes/134892/

class ObtenerChar:
    """
    Obtener un caracter de entrada sin mostrarlo 
    """
    def __init__(self):
        try:
            self.ejecutar = None
        except ImportError:  # Significa que no existen esos modulos y no se está en Windows
            self.ejecutar = None
    
    def __call__(self):
        return self.ejecutar()


class __ObtenerChUnix:
    def __init__(self):  # Intento de importación
        import tty, sys
    
    def __call__(self):
        import sys, tty, termios
        descriptor_de_archivo = sys.stdin.fileno()
        vieja_config = termios.tcgetattr(descriptor_de_archivo)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(descriptor_de_archivo, termios.TCSADRAIN, vieja_config)
        return ch


class __ObtenerChWindows:
    def __init__(self):  # Intento de importación
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()
