# siiau-consultas-api: Consulta información del SIIAU de la UDG
# Copyright (C) 2022  Benjamín Ramírez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from .utiles import limpiar_pantalla, regresar_cursor_inicio_pantalla, tam_consola
from .esquemas import Teclas, Opcion
from .getch import getch

from typing import List, Tuple
from colorama import Style, Back, Fore


def advertencia(texto: str, msj: str = 'ADVE'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.YELLOW}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.YELLOW}{texto}{Style.RESET_ALL}', ancho_real


def error(texto: str, msj: str = ' ERR'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.RED}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.RED}{texto}{Style.RESET_ALL}', ancho_real


def correcto(texto: str, msj: str = 'CORR'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.GREEN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.GREEN}{texto}{Style.RESET_ALL}', ancho_real


def seleccion(texto: str, cursor: str):
    ancho_real = f'{cursor} {texto}'.__len__()
    pre, _ = sub_titulo(cursor)
    seleccionado = f'{Style.BRIGHT}{Fore.BLUE}{texto}{Style.RESET_ALL}'
    return f'{pre} {seleccionado}', ancho_real


def titulo(texto: str, margen: int = 1):
    ancho_real = f'{" "*margen}{texto}{" "*margen}'.__len__()
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.CYAN}{" "*margen}{texto}{" "*margen}{Style.RESET_ALL}', ancho_real

    
def definicion(concepto: str, definicion: str, margen: int = 1):
    ancho_real = f'{" "*margen}{concepto}{" "*margen} {definicion}'.__len__()
    concepto_marcado = f'{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA}{" "*margen}{concepto}{" "*margen}{Style.RESET_ALL}'
    concepto_y_definicion = f'{concepto_marcado} {definicion}'
    return concepto_y_definicion, ancho_real


def sub_titulo(texto: str):
    ancho_real = texto.__len__()
    return f'{Style.BRIGHT}{Fore.CYAN}{texto}{Style.RESET_ALL}', ancho_real


def log(texto: str, trazo: str):
    dentro, _ = seleccion(trazo)
    ancho_real = f'[{texto}] {trazo}'.__len__()
    izq, _ = sub_titulo('[')
    der, _ = sub_titulo(']')
    pre = f'{izq}{dentro}{der}'
    return f'{pre} {texto}', ancho_real


CURSOR = '>'
ESC_CODE = '\x1b'
DELIMITADOR_RECUADRO = '|'
EXTRA_ESP_CURSOR = len(CURSOR) + 1
USUARIO_DEFECTO  = 'Usuario Desconocido'
PROGRAMA, LEN_PROG = sub_titulo('SIIAU Consulta')
MARGEN_RECUADRO_OPC = 10
ENC_PIE = 2
TAM_MAX_COLS = 187
TAM_MAX_FILAS = 44


def centrar_linea(linea: str, ancho_total: int, ancho_linea: int, relleno: str=' '):
    mitad = ancho_total // 2
    mitad_linea = ancho_linea // 2
    mitad_restada = mitad - mitad_linea
    espacio_izq = relleno * mitad_restada
    espacio_der = relleno * (ancho_total - (len(espacio_izq) + ancho_linea))

    return ''.join([espacio_izq, linea, espacio_der])


def alinear_linea_derecha(linea: str, ancho_total: int, ancho_linea: int, relleno: str=' '):
    espacio = relleno * (ancho_total - ancho_linea)

    return ''.join([espacio, linea])


def alinear_linea_izquierda(linea: str, ancho_total: int, ancho_linea: int, relleno: str=' '):
    espacio = relleno * (ancho_total - ancho_linea)

    return ''.join([linea, espacio])


def columnas_en_fila(*columnas: tuple, alineaciones, ancho_total):
    """
    #### COLUMNAS
    Enviar:
    >>> (
            (dato, len(dato)),
            (dato, len(dato)),
            ...
        )

    #### ALINEACIONES
    Enviar:
    >>> (
            alinear_linea_izquierda,
            alinear_linea_derecha,
            ...
        )

    #### ANCHO TOTAL
    Enviar: Entero indicando el ancho total entre todas las columnas
    """
    alineacion_defecto = alinear_linea_izquierda
    tam_columna = ancho_total // len(columnas)

    formadas = []

    for i_columna, columna in enumerate(columnas):
        dato_columna, ancho_columna = columna
        try:
            formadas.append(alineaciones[i_columna](dato_columna, tam_columna, ancho_columna, ' '))
        except IndexError:
            formadas.append(alineacion_defecto(dato_columna, tam_columna, ancho_columna, ' '))
    
    return ''.join(formadas)


def centrar_verticalmente(texto: str, alto_total: int, correccion: int = 2 ):
    alto_corregido = alto_total - correccion
    lineas = texto.splitlines()
    alto_lineas = len(lineas)
    alto_partes = (alto_corregido - alto_lineas) // 2
    arriba = '\n' * alto_partes
    abajo = '\n' * alto_partes
    centrado =  ''.join([arriba, texto, '\n', abajo])
    centrado = centrado [:-1]

    return centrado


def __formatear_una_opcion(opcion_texto: str, max_len: int, 
                           i_seleccion: int, i_opcion: int,
                           cols_terminal) -> str:
    esta_seleccionado = i_seleccion == i_opcion
    if esta_seleccionado:
        opcion_formateada, len_opcion = seleccion(opcion_texto, CURSOR)
    else:
        opcion_formateada = opcion_texto
        len_opcion = len(opcion_formateada)
    nuevo_max_len = max_len + EXTRA_ESP_CURSOR

    a_izquierda = alinear_linea_izquierda(opcion_formateada, nuevo_max_len, len_opcion)
    linea_recuadro_opciones = centrar_linea(a_izquierda, nuevo_max_len + MARGEN_RECUADRO_OPC, nuevo_max_len)
    linea_recuadro_opciones = ''.join([DELIMITADOR_RECUADRO, linea_recuadro_opciones, DELIMITADOR_RECUADRO])
    len_linea_recuadro = len(DELIMITADOR_RECUADRO) * 2 + nuevo_max_len + MARGEN_RECUADRO_OPC

    linea_recuadro_centrada = centrar_linea(linea_recuadro_opciones, cols_terminal, len_linea_recuadro, ' ')

    return linea_recuadro_centrada


def __formatear_opciones(opciones: Tuple[Opcion], i_seleccion: int, cols_terminal) -> List[str]:
    max_len_opciones_crudas = max(list(map(lambda opc: len(opc.mensaje), opciones)))
    opciones_con_formato = []
    for i_opcion, opcion_a_formatear in enumerate(opciones):
        opcion_a_formatear: Opcion
        nueva_linea_opc = __formatear_una_opcion(
            opcion_a_formatear.mensaje,
            max_len_opciones_crudas,
            i_seleccion,
            i_opcion,
            cols_terminal
        )
        opciones_con_formato.append(nueva_linea_opc)
    
    return opciones_con_formato


def __formatear_encabezados(cols_terminal) -> str:
    usuario, len_usua = sub_titulo(USUARIO_DEFECTO)
    encabezados = columnas_en_fila((PROGRAMA, LEN_PROG),
                                   (usuario, len_usua),
                                   alineaciones=(
                                       centrar_linea,
                                       centrar_linea,
                                   ),
                                   ancho_total=cols_terminal)
    
    return encabezados


def __formatear_indicaciones(cols_terminal) -> str:
    atajos = [
        definicion('/\ \/', 'Moverse'),
        definicion('ENTER', 'Selecc'),
        definicion('Backs', 'Salir'),
    ]
    linea_indicaciones = columnas_en_fila(
        *atajos, 
        alineaciones=[centrar_linea for _ in atajos], 
        ancho_total=cols_terminal
    )

    return linea_indicaciones


def __limpar_cli():
    limpiar_pantalla()
    regresar_cursor_inicio_pantalla()


def __leer_tecla():
    # TODO probar compatibilidad con Windows
    ch = getch()
    # print([ch])
    if ch == ESC_CODE:
        if getch() == '[':
            ch += '['
            ch += getch()
            return sum(map(ord, ch))
        else:
            return ord(ch)
    else:
        return ord(ch)


def menu_generico_seleccion(opciones: Tuple[Opcion], titulo_menu: str = 'MENU', subtitulo_menu: str = None,
                            principal = True):
    i_seleccion = 0
    ultimo_tam_cols, ultimo_tam_filas = tam_consola()
    if ultimo_tam_cols > TAM_MAX_COLS:
            ultimo_tam_cols = TAM_MAX_COLS
    if ultimo_tam_filas > TAM_MAX_FILAS:
            ultimo_tam_filas = TAM_MAX_FILAS

    __limpar_cli()
    while True:
        cols_terminal, filas_terminal = tam_consola()
        if cols_terminal > TAM_MAX_COLS:
            cols_terminal = TAM_MAX_COLS
        if filas_terminal > TAM_MAX_FILAS:
            filas_terminal = TAM_MAX_FILAS

        if (cols_terminal != ultimo_tam_cols) or (filas_terminal != ultimo_tam_filas):
            ultimo_tam_cols = cols_terminal
            ultimo_tam_filas = filas_terminal
            __limpar_cli()

        titulo_formateado, len_titulo = titulo(titulo_menu.upper(), 2)
        titulo_centrado = centrar_linea(titulo_formateado, cols_terminal, len_titulo)
        if subtitulo_menu != None:
            subt_formateado, len_sub = sub_titulo(subtitulo_menu.upper())
            subt_centrado = centrar_linea(subt_formateado, cols_terminal, len_sub)
        
        # Para hacer bucle de selecccion.
        # Se llega al final regresa al comienzo y viceversa
        if i_seleccion > (len(opciones) - 1):
            i_seleccion = 0
        if i_seleccion < 0:
            i_seleccion = (len(opciones) - 1)

        encabezados_formados = __formatear_encabezados(cols_terminal)
        indicaciones = __formatear_indicaciones(cols_terminal)
        opciones_formateadas = __formatear_opciones(opciones, i_seleccion, cols_terminal)

        menu_principal = [
            titulo_centrado,
            '',
            '',
            *opciones_formateadas
        ]
        if subtitulo_menu != None:
            menu_principal.insert(1, subt_centrado)

        menu_centrado = centrar_verticalmente('\n'.join(menu_principal), filas_terminal - ENC_PIE)
        print(encabezados_formados, menu_centrado, indicaciones)

        tecla = __leer_tecla()
        if tecla == Teclas().tec_flecha_ar or tecla == Teclas().tec_flecha_iz:
            i_seleccion -= 1
        elif tecla == Teclas().tec_flecha_ab or tecla == Teclas().tec_flecha_de:
            i_seleccion += 1
        elif tecla == Teclas().tec_enter:
            __limpar_cli()
            opciones[i_seleccion].funcion()  # Se ejecuta la funcion guardada en esa opcion
            __limpar_cli()
        elif tecla == Teclas().tec_retroceso or tecla == Teclas().com_ctrl_c:
            __limpar_cli()
            if principal:  # Si es principal, y se aprieta salir, cierra el programa
                print('Hasta luego')
                exit()
            else:  # Si no es principal, se sale del menu
                break

        regresar_cursor_inicio_pantalla()


if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando desde cli.py')
