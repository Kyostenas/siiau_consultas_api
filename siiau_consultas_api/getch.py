# Código obtenido de https://code.activestate.com/recipes/134892/

def getch():
    """
    Obtener un caracter de entrada sin mostrarlo 
    """
    try:
        ejecutar = getchwindows()
    except (ImportError or ModuleNotFoundError):  # Significa que no existen esos modulos y no se está en Windows
        ejecutar = getchunix()
    return ejecutar


def getchunix():
    import tty, sys, termios
    descriptor_de_archivo = sys.stdin.fileno()
    vieja_config = termios.tcgetattr(descriptor_de_archivo)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(descriptor_de_archivo, termios.TCSADRAIN, vieja_config)

    return ch


def getchwindows():
    import msvcrt
    return msvcrt.getch()
