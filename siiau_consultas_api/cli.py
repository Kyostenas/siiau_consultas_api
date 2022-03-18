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


from .utiles import aplanar_lista, limpiar_pantalla, particion_arbitraria, regresar_cursor_inicio_pantalla, tam_consola
from .esquemas import Teclas, Opcion, LETRAS, NUMEROS, LETRAS_DIC, NUMEROS_DIC
from .utiles import particionar
from .getch import getch

from typing import List, Tuple, Union
from colorama import Style, Back, Fore, Cursor, init
init()
from math import sqrt


# TODO mejorar nombres de estilos de texto para que no conflictuen con variables

def advertencia(texto: str, msj: str = 'ADVE'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.YELLOW}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.YELLOW}{texto}{Style.RESET_ALL}', ancho_real


def error(texto: str, msj: str = ' ERR'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.RED}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.RED}{texto}{Style.RESET_ALL}', ancho_real


def correcto(texto: str, msj: str = '  OK'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.GREEN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.GREEN}{texto}{Style.RESET_ALL}', ancho_real


def seleccion(texto: str, cursor: str):
    ancho_real = f'{cursor} {texto}'.__len__()
    pre, _ = sub_titulo(cursor)
    seleccionado = f'{Style.BRIGHT}{Fore.BLUE}{texto}{Style.RESET_ALL}'
    return f'{pre} {seleccionado}', ancho_real


def seleccion_modificable(texto: str, cursor: str):
    ancho_real = f'{cursor} {texto}{CARET}'.__len__()
    pre, _ = sub_titulo(cursor)
    seleccionado = f'{Style.BRIGHT}{Fore.BLUE}{texto}{Style.RESET_ALL}{CARET}'
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

def comentario(texto: str):
    ancho_real = texto.__len__()
    return f'{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{texto}{Style.RESET_ALL}', ancho_real


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
MSJ_VACIO = 'escribe'
CARET = '│'


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

    a_izquierda = alinear_linea_izquierda(opcion_formateada, 
                                          nuevo_max_len, 
                                          len_opcion)
    linea_recuadro_opciones = centrar_linea(a_izquierda, 
                                            nuevo_max_len + MARGEN_RECUADRO_OPC, 
                                            nuevo_max_len)
    linea_recuadro_opciones = ''.join([DELIMITADOR_RECUADRO, 
                                       linea_recuadro_opciones, 
                                       DELIMITADOR_RECUADRO])
    len_linea_recuadro = len(DELIMITADOR_RECUADRO) * 2 + nuevo_max_len + MARGEN_RECUADRO_OPC
    linea_recuadro_centrada = centrar_linea(linea_recuadro_opciones, 
                                            cols_terminal, 
                                            len_linea_recuadro, 
                                            ' ')

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


def __formatear_indicaciones(tam_espacio, principal: bool) -> str:
    if principal:
        salir = 'salir'
    else:
        salir = 'regresar'
    atajos = [
        definicion('/\ \/', 'moverse'),
        definicion('ENTER', 'selecc'),
        definicion('Retroc', salir),
    ]
    linea_indicaciones = columnas_en_fila(
        *atajos, 
        alineaciones=[centrar_linea for _ in atajos], 
        ancho_total=tam_espacio
    )

    return linea_indicaciones


def __indicaciones_personalicadas(atajos: tuple, tam_espacio) -> str:
    atajos = [definicion(*un_atajo) for un_atajo in atajos]
    linea_indicaciones = columnas_en_fila(
        *atajos, 
        alineaciones=[centrar_linea for _ in atajos], 
        ancho_total=tam_espacio
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


def menu_generico_seleccion(opciones: Tuple[Opcion], principal: bool,
                            titulo_menu: str = 'MENU', subtitulo_menu: str = None):
    resultados_ejecuciones = {}
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
        indicaciones = __formatear_indicaciones(cols_terminal, principal)
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
        print(encabezados_formados, menu_centrado, indicaciones)  # Se muestra el menu

        """ En esta parte se espera una tecla y se hace algo con el resultado """
        tecla = __leer_tecla()
        if tecla == Teclas().tec_flecha_ar or tecla == Teclas().tec_flecha_iz:
            i_seleccion -= 1
        elif tecla == Teclas().tec_flecha_ab or tecla == Teclas().tec_flecha_de:
            i_seleccion += 1
        elif tecla == Teclas().tec_enter:
            __limpar_cli()
            funcion_obtenida = opciones[i_seleccion].funcion  # Se obtiene la funcion
            nombre_funcion = funcion_obtenida.__name__  # Se obtiene el nombre como cadena
            try:
                # Se ejecuta la funcion guardada en esa opcion y se intenta enviar
                # la transferencia (resultados anteriores de otras ejecuciones)
                retorno_funcion = funcion_obtenida(transferencia=resultados_ejecuciones)
            except TypeError:
                # Se ejecuta la funcion guardada en esa opcion
                retorno_funcion = funcion_obtenida()  

            # Se guarda el resultado de la funcion en un diccionario
            try:            
                resultados_ejecuciones[nombre_funcion].append(retorno_funcion)
            except:
                resultados_ejecuciones[nombre_funcion] = [retorno_funcion]
                
            __limpar_cli()
        elif tecla == Teclas().tec_retroceso or tecla == Teclas().com_ctrl_c:
            __limpar_cli()
            if principal:  # Si es principal, y se aprieta salir, cierra el programa
                print('Hasta luego')
                exit()
            else:  # Si no es principal, se sale del menu
                return resultados_ejecuciones

        regresar_cursor_inicio_pantalla()
        
        
def __centrar_agregados(agregados, espacio, i_fila_sel, i_col_sel):
    lineas_en_columnas = []
    for i_fila, fila in enumerate(agregados):
        para_hacer_linea = []
        for i_col, col in enumerate(fila):
            if col == '' and not ((i_fila, i_col) == (i_fila_sel, i_col_sel)):
                nueva_col = comentario(MSJ_VACIO)
            elif (i_fila, i_col) == (i_fila_sel, i_col_sel):
                if col == '':
                    nueva_col = seleccion(MSJ_VACIO, CURSOR)
                else:
                    nueva_col = seleccion_modificable(col, CURSOR)
            else:
                nueva_col = tuple([col, len(col)])
            para_hacer_linea.append(nueva_col)
        linea_centrada = columnas_en_fila(
            *para_hacer_linea,
            alineaciones=[
                centrar_linea
                for _ in para_hacer_linea
            ],
            ancho_total=espacio
        )
        lineas_en_columnas.append(linea_centrada)
        
    return lineas_en_columnas


def pantalla_agregado_centrada(tam_max_agregado: int,
                               mensaje = 'agregar elementos', 
                               transferencia: Union[list, tuple] = None):
    if transferencia != None:
        agregado = transferencia
        if len(agregado) == 0:
            agregado.append('')
    else:
        agregado = ['']
    i_fila_seleccion = 0
    i_col_seleccion = 0
    ultimo_tam_cols, ultimo_tam_filas = tam_consola()
    if ultimo_tam_cols > TAM_MAX_COLS:
            ultimo_tam_cols = TAM_MAX_COLS
    if ultimo_tam_filas > TAM_MAX_FILAS:
            ultimo_tam_filas = TAM_MAX_FILAS
            
    indicaciones = [
        ('flech', 'moverse'),
        ('Ctrl+A', 'agreg'),
        ('Ctrl+X', 'elim'),
        ('Retroc', 'borr'),
        ('Ctrl+R', 'regresar'),
    ]

    __limpar_cli()
    while True:
        # Se calcula el tam. de cada fila para la representacion
        # grafica.
        agregado_modificable = list(agregado)
        tams_filas = sqrt(len(agregado_modificable))
        if tams_filas < int(tams_filas):
            tams_filas = int(tams_filas) + 1
        else:
            tams_filas = int(tams_filas)
        tams_reales_filas = []
        tam_agregado = len(agregado_modificable)
        
        # Se crean los tam de cada fila.
        while tam_agregado > tams_filas:
            tam_agregado -= tams_filas
            tams_reales_filas.append(tams_filas)
            
        # Si sobra, significa que una fila sera menor, y se agrega el
        # sobrane para que se cree dicha fila.
        if tam_agregado > 0:
            tams_reales_filas.append(tam_agregado)
            
        # Se crea una particion arbitraria, que es una particion en el
        # que se decide el tam. de cada parte individualmente.
        # El tam de cada parte esta en "tams_reales_filas", y se pasa
        # con el operador * porque el argumento partes puede recibir
        # n cantidad de enteros; asi recibe cada entero individualmente.
        agregado_ordenado = particion_arbitraria(agregado_modificable, 
                                                 *tams_reales_filas)
                
        filas_agregado = len(agregado_ordenado)
        cols_agregado = max([len(fila) for fila in agregado_ordenado])
        cols_terminal, filas_terminal = tam_consola()
        if cols_terminal > TAM_MAX_COLS:
            cols_terminal = TAM_MAX_COLS
        if filas_terminal > TAM_MAX_FILAS:
            filas_terminal = TAM_MAX_FILAS
            
        # Para hacer bucle de selecccion.
        # Se llega al final regresa al comienzo y viceversa
        if i_fila_seleccion > filas_agregado:
            i_fila_seleccion = 0
        elif i_fila_seleccion < 0:
            i_fila_seleccion = filas_agregado
        if i_col_seleccion > cols_agregado:
            i_col_seleccion = 0
        elif i_col_seleccion < 0:
            i_col_seleccion = cols_agregado
        
        # Si cambia el tam. de la terminal, se limpia por completo
        # para que no queden rastros de la visualizacion anterior.
        if (cols_terminal != ultimo_tam_cols) or (filas_terminal != ultimo_tam_filas):
            ultimo_tam_cols = cols_terminal
            ultimo_tam_filas = filas_terminal
            __limpar_cli()
            
        titulo_formateado, len_titulo = titulo(mensaje, 2)
        titulo_centrado = centrar_linea(titulo_formateado, 
                                        cols_terminal, 
                                        len_titulo)
        encabezados = __formatear_encabezados(cols_terminal)
        pie = __indicaciones_personalicadas(indicaciones, cols_terminal)
        agregados_alineados = __centrar_agregados(
            agregados=agregado_ordenado,
            espacio=int(cols_terminal * .70),  # Se quiere el 70% del ancho de la consola
            i_fila_sel=i_fila_seleccion,
            i_col_sel=i_col_seleccion
        )
        agregados_centrados = list(map(
            lambda linea: centrar_linea(linea, 
                                        cols_terminal,
                                        int(cols_terminal * .70)),
            agregados_alineados
        ))
        pantalla_agregado = [
            titulo_centrado,
            '',
            '',
            *agregados_centrados
        ]
        pantalla_agregado_centrada = centrar_verticalmente('\n'.join(pantalla_agregado),
                                                           filas_terminal - ENC_PIE)
        print(encabezados, pantalla_agregado_centrada, pie)
        
        """ En esta parte se espera una tecla y se hace algo con el resultado """
        tecla = __leer_tecla()
        if tecla == Teclas().tec_flecha_ar:
            i_fila_seleccion -= 1
        elif tecla == Teclas().tec_flecha_ab:
            i_fila_seleccion += 1
        elif tecla == Teclas().tec_flecha_de:
            i_col_seleccion += 1
        elif tecla == Teclas().tec_flecha_iz:
            i_col_seleccion -= 1
        elif tecla == Teclas().com_ctrl_a:
            agregado.append('')
            __limpar_cli()
        elif tecla == Teclas().com_ctrl_x:
            if len(agregado) > 0:
                i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
                agregado.pop(i_original)
            __limpar_cli()       
        elif tecla in LETRAS:
            i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
            if len(agregado[i_original]) < tam_max_agregado:
                agregado[i_original] += LETRAS_DIC[tecla]
        elif tecla in NUMEROS:
            i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
            if len(agregado[i_original]) < tam_max_agregado:
                agregado[i_original] += NUMEROS_DIC[tecla]
        elif tecla == Teclas().tec_retroceso:
            i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
            if len(agregado[i_original]) > 0:
                agregado[i_original] = agregado[i_original][:-1]  # Se le quita el ultimo caracter
        elif tecla == Teclas().com_ctrl_r or tecla == Teclas().com_ctrl_c:
            __limpar_cli()
            return agregado
    
        regresar_cursor_inicio_pantalla()


if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando desde cli.py')
