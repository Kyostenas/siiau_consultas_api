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


from typing import List, Tuple
from utiles import limpiar_pantalla, regresar_cursor_inicio_pantalla, print_actualizable
from utiles import es_alguna_instancia, limpiar_secuencias_ANSI
from servicio_horario_siiau import __obtener_fecha_completa
from esquemas import Teclas, Opcion
from getch import ObtenerChar

from colorama import Style, Back, Fore
from datetime import datetime
import os


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
    return f'{Style.BRIGHT}{Fore.BLUE}{pre} {texto}{Style.RESET_ALL}', ancho_real

def titulo(texto: str, margin: int = 1):
    ancho_real = f'{" "*margin}{texto}{" "*margin}'.__len__()
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.CYAN}{" "*margin}{texto}{" "*margin}{Style.RESET_ALL}', ancho_real

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




if cols_terminal > 200:
    cols_terminal = 187

CURSOR = '>>'
DELIMITADOR_RECUADRO = '|'
EXTRA_ESP_CURSOR = len(CURSOR) + 1
USUARIO_DEFECTO  = '000000000'
PROGRAMA, LEN_PROG = sub_titulo('SIIAU Consulta')
MARGEN_RECUADRO_OPC = 10



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


def centrar_horizontalmente(texto: str, alto_total: int):
    alto_corregido = alto_total - 1
    lineas = texto.splitlines()
    alto_lineas = len(lineas)
    alto_partes = (alto_corregido - alto_lineas) // 2
    arriba = '\n' * alto_partes
    abajo = '\n' * alto_partes
    centrado =  ''.join([arriba, texto, '\n', abajo])
    centrado = centrado [:-1]

    return centrado


def __formatear_una_opcion(opcion_texto: str, max_len: int, i_seleccion: int, i_opcion: int) -> str:
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


def __formatear_opciones(opciones: Tuple[Opcion], i_seleccion: int) -> List[str]:
    max_len_opciones_crudas = max(list(map(lambda opc: len(opc.mensaje), opciones)))
    opciones_con_formato = []
    for i_opcion, opcion_a_formatear in enumerate(opciones):
        opcion_a_formatear: Opcion
        nueva_linea_opc = __formatear_una_opcion(
            opcion_a_formatear.mensaje,
            max_len_opciones_crudas,
            i_seleccion,
            i_opcion
        )
        opciones_con_formato.append(nueva_linea_opc)
    
    return opciones_con_formato


def __formatear_encabezados() -> str:
    fecha = datetime.now()
    fecha = f'{fecha.day}-{fecha.month}-{fecha.year}'
    fecha_completa, len_fech_com = sub_titulo(__obtener_fecha_completa(str(fecha), '-'))
    usuario, len_usua = sub_titulo(USUARIO_DEFECTO)
    encabezados = columnas_en_fila((fecha_completa, len_fech_com),
                                    (PROGRAMA, LEN_PROG),
                                    (usuario, len_usua),
                                    alineaciones=(
                                        alinear_linea_izquierda,
                                        centrar_linea,
                                        alinear_linea_derecha
                                    ),
                                    ancho_total=cols_terminal)
    
    return encabezados


def menu(titulo_menu: str, opciones: Tuple[Opcion]):
    i_seleccion = 0
    # limpiar_pantalla()
    while True:
        titulo_formateado, len_titulo = titulo(titulo_menu, 2)
        titulo_centrado = centrar_linea(titulo_formateado, cols_terminal, len_titulo)
        # Para hacer bucle de selecccion.
        # Se llega al final regresa al comienzo y viceversa
        if i_seleccion > (len(opciones) - 1):
            i_seleccion = 0
        if i_seleccion < 0:
            i_seleccion = (len(opciones) - 1)

        encabezados = __formatear_encabezados()
        opciones_formateadas = __formatear_opciones(opciones, i_seleccion)
        menu_principal = [
            titulo_centrado,
            '',
            *opciones_formateadas
        ]
        menu_centrado = centrar_horizontalmente('\n'.join(menu_principal), filas_terminal - 1)

        print(__formatear_encabezados())
        print(menu_centrado)
        input()
        i_seleccion += 1
        limpiar_pantalla()

if __name__ == '__main__':
    titulo_menu = 'MENU PRINCIPAL'
    opciones = [
    Opcion('Consultar oferta', str),
    Opcion('Consultar horario', str),
    Opcion('Registrar materias', str),
    ]
    menu(titulo_menu, opciones)
