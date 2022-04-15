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


if __name__ == '__main__':
    ESC_CODE = '\x1b'
    def __leer_tecla(retornar_original = False):
        ch = getch()
        # print([ch])
        if ch == ESC_CODE:
            otro_ch = getch()
            if otro_ch == '[':
                ch += '['
                decisivo_ctrl = getch()
                if decisivo_ctrl.isnumeric():
                    ch += decisivo_ctrl
                    ch += getch()
                    ch += getch()
                    ch += getch()
                else:
                    ch += decisivo_ctrl
                if retornar_original:
                    return sum(map(ord, ch)), ch
                else:
                    return sum(map(ord, ch))
            else:
                print([[otro_ch]])
                if retornar_original:
                    return ord(ch), ch
                else:
                    return ord(ch)
        else:
            if retornar_original:
                return ord(ch), ch
            else:
                return ord(ch)

    import os

    while True:
        otro, ch = __leer_tecla(retornar_original=True)
        # os.system('cls' if os.name=='nt' else 'clear')
        print(otro, [ch])
        if ch == 'm':
            print('Ingrese codigo especial: ', end='\n')
            tec = __leer_tecla()
            if tec == 3:
                exit()