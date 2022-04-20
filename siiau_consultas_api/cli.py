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


from .utiles import (limpiar_pantalla, 
                     limpiar_secuencias_ANSI, 
                     regresar_cursor_inicio_pantalla, 
                     tam_consola,
                     particion_arbitraria,
                     escribir_json,
                     mk_dir_en_dir_actual)
from .esquemas import Teclas, Opcion, LETRAS, NUMEROS, LETRAS_DIC, NUMEROS_DIC
from .getch import getch

from random import choice
from colorama import Style, Back, Fore, init
from typing import List, Tuple, Union
from tabulate import tabulate
from math import sqrt
init()  # Para que colorama funcione en Windows


# TODO mejorar nombres de estilos de texto para que no conflictuen con variables
# TODO quitar retorno de tam de texto y hacer correcciones necesarias

def advertencia(texto: str, msj: str = 'ADVE'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.YELLOW}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.YELLOW}{texto}{Style.RESET_ALL}', ancho_real


def error(texto: str, msj: str = ' ERR', mostrar_pre = True):
    if mostrar_pre:
        ancho_real = f'{msj} {texto}'.__len__()
        pre = f'{Style.BRIGHT}{Back.RED}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL} '
    else:
        ancho_real = f'{texto}'.__len__()
        pre = ''
    return f'{pre}{Style.BRIGHT}{Fore.RED}{texto}{Style.RESET_ALL}', ancho_real


def correcto(texto: str, msj: str = '  OK'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.BRIGHT}{Back.GREEN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.GREEN}{texto}{Style.RESET_ALL}', ancho_real

def ayuda(texto: str, msj: str = 'AYUD'):
    ancho_real = f'{msj} {texto}'.__len__()
    pre = f'{Style.DIM}{Back.CYAN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.CYAN}{texto}{Style.RESET_ALL}', ancho_real


def seleccion(texto: str, cursor: str):
    # ancho_real = f'{cursor} {texto}'.__len__()
    ancho_real = f'{texto}'.__len__()
    # pre, _ = sub_titulo(cursor)
    seleccionado = f'{Style.BRIGHT}{Back.WHITE}{Fore.BLACK}{texto}{Style.RESET_ALL}'
    return f'{seleccionado}', ancho_real
    # return f'{pre} {seleccionado}', ancho_real


def seleccion_modificable(texto: str, cursor: str):
    # ancho_real = f'{cursor} {texto}{CARET}'.__len__()
    ancho_real = f'{texto}'.__len__()
    # pre, _ = sub_titulo(cursor)
    caret = f'{Style.BRIGHT}{Fore.CYAN}{CARET}{Style.RESET_ALL}'
    seleccionado = (
        f'{Style.BRIGHT}{Back.WHITE}{Fore.BLACK}{texto}{Style.RESET_ALL}{caret}'
    )
    return f'{seleccionado}', ancho_real
    # return f'{pre} {seleccionado}', ancho_real


def titulo(texto: str, margen: int = 1):
    ancho_real = f'{" "*margen}{texto}{" "*margen}'.__len__()
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.CYAN}{" "*margen}{texto.upper()}{" "*margen}{Style.RESET_ALL}', ancho_real


def negativo(texto: str, margen: int = 1):
    ancho_real = f'{" "*margen}{texto}{" "*margen}'.__len__()
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.BLACK}{" "*margen}{texto}{" "*margen}{Style.RESET_ALL}', ancho_real

    
def definicion(concepto: str, definicion: str, margen: int = 1):
    ancho_real = f'{" "*margen}{concepto}{" "*margen} {definicion}'.__len__()
    concepto_marcado = f'{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA}{" "*margen}{concepto}{" "*margen}{Style.RESET_ALL}'
    concepto_y_definicion = f'{concepto_marcado} {definicion}'
    return concepto_y_definicion, ancho_real


def sub_titulo(texto: str):
    ancho_real = texto.__len__()
    return f'{Style.BRIGHT}{Fore.CYAN}{texto}{Style.RESET_ALL}', ancho_real


def log(texto: str, trazo: str, margen: int = 1):
    espacio = ' ' * margen
    ancho_real = f'[{espacio}{trazo}{espacio}] {texto}'.__len__()
    pre = f'{Fore.WHITE}[{espacio}{trazo}{espacio}]{Style.RESET_ALL}'
    texto, _ = comentario(texto)
    return f'{pre} {texto}', ancho_real


def log2(texto: str, trazo: str, margen: int = 1):
    espacio = ' ' * margen
    ancho_real = f'{espacio}{trazo}{espacio} {texto}'.__len__()
    pre = f'{Back.BLACK}{Style.BRIGHT}{Fore.BLUE}{espacio}{trazo}{espacio}{Style.RESET_ALL}'
    texto, _ = comentario(texto)
    return f'{pre} {texto}', ancho_real


def comentario(texto: str):
    ancho_real = texto.__len__()
    return f'{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{texto}{Style.RESET_ALL}', ancho_real


CURSOR = '>'
CARET = '│'
ESC_CODE = '\x1b'
DELIMITADOR_RECUADRO = '|'
EXTRA_ESP_CURSOR = 0
EXTRA_ESP_CARET = len(CARET)
USUARIO_DEFECTO  = 'Usuario Desconocido'
PROGRAMA, LEN_PROG = sub_titulo('SIIAU Consulta')
MARGEN_RECUADRO_OPC = 10
ENC_PIE = 2
ENC_PIE_TITULO_SUBT = ENC_PIE + 5
ENC_PIE_BORDE = ENC_PIE + 12
MAX_TAM_COLS = 200
MAX_TAM_FILAS = 200
MSJ_VACIO = '...'
MSJ_SIN_ELEMENTOS = 'No hay elementos para mostrar'
ESP_EXTRA_NOTICIAS = 5
I_CADENA_COLOR = 0
I_TAM_CADENA_COLOR = 1  # REMINDER Se borrara obtencion de tam de texto de los colores
ESP_BLANCO_TABLA = '\\'
ESP_TITULO_Y_ESPS_BLANCOS = 7
ESP_CORRECCION_COLS_TERMINAL = 1
TRAZO = 'siiaucli'
PUNTOS_TEXTO_CORTADO = '...'
MSJ_OBTENCION = 'se obtuvo: '
PRIMERA_PAGINA = 0
TECLAS = Teclas()


def despedida():
    print('Hasta luego')


def __obtener_espacio_bordes_tabla(cols): 
    return (2 * cols) + 2


def __obtener_max_filas_opciones(filas_term): 
    return filas_term - ENC_PIE_BORDE


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
    nuevo_max_len = max_len + EXTRA_ESP_CURSOR
    len_opcion = len(opcion_texto)
    if esta_seleccionado:
        a_izquierda = alinear_linea_izquierda(
            opcion_texto, 
            nuevo_max_len, 
            len_opcion
        )
        linea_recuadro_opciones = centrar_linea(
            a_izquierda, 
            nuevo_max_len + MARGEN_RECUADRO_OPC, 
            nuevo_max_len
        )
        linea_recuadro_opciones, len_opcion = seleccion(
            linea_recuadro_opciones, 
            CURSOR
        )
    else:
        a_izquierda = alinear_linea_izquierda(
            opcion_texto, 
            nuevo_max_len, 
            len_opcion
        )
        linea_recuadro_opciones = centrar_linea(
            a_izquierda, 
            nuevo_max_len + MARGEN_RECUADRO_OPC, 
            nuevo_max_len
        )
        
    linea_recuadro_opciones = ''.join([
        DELIMITADOR_RECUADRO, 
        linea_recuadro_opciones, 
        DELIMITADOR_RECUADRO
    ])
    len_linea_recuadro = (
        len(DELIMITADOR_RECUADRO) * 2 + nuevo_max_len + MARGEN_RECUADRO_OPC
    )
    linea_recuadro_centrada = centrar_linea(
        linea_recuadro_opciones, 
        cols_terminal, 
        len_linea_recuadro, 
    )

    return linea_recuadro_centrada


def __formatear_opciones(opciones: Tuple[Opcion], i_seleccion: int, 
                         cols_terminal) -> List[str]:
    max_len_opciones_crudas = max(list(map(
        lambda opc: len(opc.mensaje), 
        opciones
    )))
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
    encabezados = columnas_en_fila(
        (PROGRAMA, LEN_PROG),
        (usuario, len_usua),
        alineaciones=(
            centrar_linea,
            centrar_linea,
        ),
        ancho_total=cols_terminal
    )
    
    return encabezados


def __formatear_indicaciones(tam_espacio, principal: bool, paginado: bool = False) -> str:
    if principal:
        salir = 'salir'
    else:
        salir = 'regresar'
    atajos = [
        definicion('/\ \/', 'moverse'),
        definicion('ENTER', 'selecc'),
        definicion('Retroc', salir),
    ]
    if paginado:
        atajos.append(
            definicion('Ctrl+flech', 'pag')
        )
    linea_indicaciones = columnas_en_fila(
        *atajos, 
        alineaciones=[centrar_linea for _ in atajos], 
        ancho_total=tam_espacio
    )

    return linea_indicaciones


def __indicaciones_personalizadas(atajos: tuple, tam_espacio) -> str:
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
    

def __soobreescribir_cli():
    cols_consola, filas_consola = tam_consola()
    barra_vacia = ' ' * (cols_consola - 1)
    cuadro_vacio = '\n'.join([barra_vacia for _ in range(filas_consola - 1)])
    print(cuadro_vacio)


def __leer_tecla(retornar_original = False):
    # TODO probar compatibilidad con Windows
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

# FIX cuando pagina sin ser cuadricula, no se puede cambiar página (¿Por qué?)
def menu_generico_seleccion(opciones: Tuple[Opcion], 
                            principal: bool,
                            # memoria_total: dict,
                            titulo_menu: str = 'MENU',
                            subtitulo_menu: str = None, 
                            # transferencia_memoria: dict = None,
                            regresar_en_seleccion: bool = False,
                            cuadricula: bool = False):
    
    # Se revisa si hay transferencia de retorno de funciones anteriores enlazadas    
    # if transferencia_memoria != None:
    #     cache_ejecuciones_temporal = transferencia_memoria
    # else:
    #     cache_ejecuciones_temporal = {}
        
    i_fila_seleccion = 0
    i_col_seleccion = 0
    pagina = 0
    total_paginas = 0
    paginar = False
    ultima_cant_filas = 0
        
    ult_tam_de_filas_cuadricula = 0
    ultimo_tam_cols_terminal, ultimo_tam_filas_terminal = tam_consola()
    if ultimo_tam_cols_terminal > MAX_TAM_COLS:
            ultimo_tam_cols_terminal = MAX_TAM_COLS
    if ultimo_tam_filas_terminal > MAX_TAM_FILAS:
            ultimo_tam_filas_terminal = MAX_TAM_FILAS
            
    tam_opcion_mas_grande = max(list(map(
        lambda opcion: len(opcion.mensaje), 
        opciones
    )))
    
    varios_retornos = []

    __limpar_cli()
    while True:
        if cuadricula :
            
            # Se calcula el tam. de cada fila para la representacion
            # grafica.
            cuadricula_modificable = list(map(lambda opcion: opcion.mensaje, opciones))
            cuadricula_funciones = list(opciones)
            elem_por_fila = sqrt(len(cuadricula_modificable))
            if elem_por_fila < int(elem_por_fila):
                elem_por_fila = int(elem_por_fila) + 1
            else:
                elem_por_fila = int(elem_por_fila)
            ancho_cols = (int(elem_por_fila) * tam_opcion_mas_grande)
            ancho_cuadricula = ancho_cols + __obtener_espacio_bordes_tabla(elem_por_fila)
            tam_max_ancho_cuadricula = ultimo_tam_cols_terminal - 50
            while True:
                if ancho_cuadricula > tam_max_ancho_cuadricula:
                    elem_por_fila -= 1
                    ancho_cols = (int(elem_por_fila) * tam_opcion_mas_grande)
                    ancho_cuadricula = ancho_cols + __obtener_espacio_bordes_tabla(elem_por_fila)
                else:
                    break
            
            if elem_por_fila != ult_tam_de_filas_cuadricula:
                ult_tam_de_filas_cuadricula = elem_por_fila
                __limpar_cli()
            
            tams_reales_filas = []
            cant_opciones = len(cuadricula_modificable)
            
            # Se crean los tam de cada fila.
            while cant_opciones > elem_por_fila:
                cant_opciones -= elem_por_fila
                tams_reales_filas.append(elem_por_fila)
                
            # Si sobra, significa que una fila sera menor, y se agrega el
            # sobrane para que se cree dicha fila.
            if cant_opciones > 0:
                tams_reales_filas.append(cant_opciones)
                
            # Se crea una particion arbitraria, que es una particion en el
            # que se decide el tam. de cada parte individualmente.
            # El tam de cada parte esta en "tams_reales_filas", y se pasa
            # con el operador * porque el argumento partes puede recibir
            # n cantidad de enteros; asi recibe cada entero individualmente.
            cuadricula_ordenada = particion_arbitraria(cuadricula_modificable, 
                                                       *tams_reales_filas)
            malla_funciones = particion_arbitraria(cuadricula_funciones, 
                                                   *tams_reales_filas)
                  
        cols_terminal, filas_terminal = tam_consola()
        if cols_terminal > MAX_TAM_COLS:
            cols_terminal = MAX_TAM_COLS
        if filas_terminal > MAX_TAM_FILAS:
            filas_terminal = MAX_TAM_FILAS

        if (cols_terminal != ultimo_tam_cols_terminal) or (filas_terminal != ultimo_tam_filas_terminal):
            ultimo_tam_cols_terminal = cols_terminal
            ultimo_tam_filas_terminal = filas_terminal
            __limpar_cli()
            
        # Comprobación para paginar (de ser necesario)
        if pagina > total_paginas - 1:
            if total_paginas > 0:
                pagina = total_paginas - 1
            else:
                pagina = 0
        elif pagina < 0:
            pagina = 0
        tam_max_filas = __obtener_max_filas_opciones(ultimo_tam_filas_terminal)
        if cuadricula:
            cant_filas_cuadricula = len(cuadricula_ordenada)
            if  cant_filas_cuadricula > tam_max_filas:
                if paginar is False:
                    paginar = True
                partes_particion = []
                while cant_filas_cuadricula > tam_max_filas:
                    cant_filas_cuadricula -= tam_max_filas
                    partes_particion.append(tam_max_filas)
                partes_particion.append(cant_filas_cuadricula)
                
                cuadricula_ordenada = particion_arbitraria(
                    cuadricula_ordenada,
                    *partes_particion
                )
                malla_funciones = particion_arbitraria(
                    malla_funciones,
                    *partes_particion
                )
                total_paginas = len(cuadricula_ordenada)
                
                try:
                    cuadricula_ordenada = cuadricula_ordenada[pagina]
                    malla_funciones = malla_funciones[pagina]
                except IndexError:
                    pagina = 0
                    cuadricula_ordenada = cuadricula_ordenada[pagina]
                    malla_funciones = malla_funciones[pagina]
            else:
                if paginar is True:
                    paginar = False
        else:
            cant_opciones = len(opciones)
            if  cant_opciones > tam_max_filas:
                if paginar is False:
                    paginar = True
                partes_particion = []
                while cant_opciones > tam_max_filas:
                    cant_opciones -= tam_max_filas
                    partes_particion.append(tam_max_filas)
                partes_particion.append(cant_opciones)
                
                opciones = particion_arbitraria(
                    opciones,
                    *partes_particion
                )
                total_paginas = len(opciones)
                try:
                    opciones = opciones[pagina]
                except IndexError:
                    pagina = 0
                    opciones = opciones[pagina]
            else:
                if paginar is True:
                    paginar = False
        
        if paginar:
            # Se vuelve a obtener la cantidad de opciones (filas de opciones) 
            # porque al paginar cambian cuantas se muestran.
            if cuadricula:
                cant_filas_opciones = len(cuadricula_ordenada)
            else:
                cant_filas_opciones = len(opciones)
            if cant_filas_opciones != ultima_cant_filas:
                ultima_cant_filas = cant_filas_opciones
                # Si varía, se limpia la consola completa.
                __limpar_cli()

        titulo_formateado, len_titulo = titulo(titulo_menu.upper(), 2)
        titulo_centrado = centrar_linea(titulo_formateado, cols_terminal, len_titulo)
        if subtitulo_menu != None:
            subt_formateado, len_sub = sub_titulo(subtitulo_menu.upper())
            subt_centrado = centrar_linea(subt_formateado, cols_terminal, len_sub)
        
        if cuadricula:
            # Para hacer bucle de selecccion.
            # Se llega al final, regresa al comienzo y viceversa.
            tam_cuadricula_ordenada  = len(cuadricula_ordenada) - 1
            if i_fila_seleccion > tam_cuadricula_ordenada :
                i_fila_seleccion = 0
            elif i_fila_seleccion < 0:
                i_fila_seleccion = tam_cuadricula_ordenada 
            try:
                tam_fila_seleccionada = len(cuadricula_ordenada[i_fila_seleccion]) - 1
            except IndexError:
                tam_fila_seleccionada = 0
            if i_col_seleccion > tam_fila_seleccionada:
                i_col_seleccion = 0
            elif i_col_seleccion < 0:
                i_col_seleccion = tam_fila_seleccionada
        else:
            # Para hacer bucle de selecccion.
            # Se llega al final regresa al comienzo y viceversa
            if i_fila_seleccion > (len(opciones) - 1):
                i_fila_seleccion = 0
            if i_fila_seleccion < 0:
                i_fila_seleccion = (len(opciones) - 1)

        encabezados_formados = __formatear_encabezados(cols_terminal)
        indicaciones_pag = True if paginar else False
        indicaciones = __formatear_indicaciones(cols_terminal, principal, indicaciones_pag)
        
        if cuadricula:
            lineas_cuadricula = __centrar_cuadricula(
                cuadricula_ordenada, 
                tam_opcion_mas_grande,
                i_fila_seleccion,
                i_col_seleccion,
                modificable=False,
                alineacion='left'
            )
            opciones_formateadas = list(map(
                lambda linea: centrar_linea(
                    linea,
                    cols_terminal,
                    len(limpiar_secuencias_ANSI(linea))
                ), 
                lineas_cuadricula
            ))
        else:
            opciones_formateadas = __formatear_opciones(opciones, i_fila_seleccion, cols_terminal)
        
        if paginar:
            num_pag, len_num_pag = comentario(f'PAG {pagina + 1}/{total_paginas}')
            num_pag = centrar_linea(num_pag, cols_terminal, len_num_pag)
        else:
            num_pag = ''

        menu_principal = [
            titulo_centrado,
            '',
            '',
            *opciones_formateadas,
            '',
            num_pag,
        ]
        if subtitulo_menu != None:
            menu_principal.insert(1, subt_centrado)

        menu_centrado = centrar_verticalmente('\n'.join(menu_principal), filas_terminal - ENC_PIE)
        print(encabezados_formados, menu_centrado, indicaciones)  # Se muestra el menu

        """ En esta parte se espera una tecla y se hace algo con el resultado """
        tecla = __leer_tecla()
        if tecla == Teclas().tec_flecha_ar:
            i_fila_seleccion -= 1
        elif tecla == Teclas().tec_flecha_ab:
            i_fila_seleccion += 1
        elif tecla == Teclas().tec_flecha_iz:
            if cuadricula:
                i_col_seleccion -= 1
        elif tecla == Teclas().tec_flecha_de:
            if cuadricula:
                i_col_seleccion += 1
        elif tecla == Teclas().com_ctrl_flecha_iz:
            if paginar:
                pagina -= 1
        elif tecla == Teclas().com_ctrl_flecha_de:
            if paginar:
                pagina += 1
        elif tecla == Teclas().tec_enter:
            if cuadricula:
                # Se obtiene la funcion.
                funcion_obtenida = (
                    malla_funciones[i_fila_seleccion][i_col_seleccion].funcion
                )
                # Se obtiene los argumentos.
                argumentos_obtenidos = (
                    malla_funciones[i_fila_seleccion][i_col_seleccion].argumentos
                ) 
                # nombre_transferencia = malla_funciones[i_fila_seleccion][i_col_seleccion].nombretransf  # Se obtiene el nombre como cadena.
            else:
                # Se obtiene la funcion.
                funcion_obtenida = opciones[i_fila_seleccion].funcion 
                # Se obtiene los argumentos.
                argumentos_obtenidos = opciones[i_fila_seleccion].argumentos
                # nombre_transferencia = opciones[i_fila_seleccion].nombretransf  # Se obtiene el nombre como cadena.
            # try:
                # Se ejecuta la funcion guardada en esa opcion y se intenta enviar
                # la transferencia (resultados anteriores de otras ejecuciones).
                # try:
                #     retorno_funcion = funcion_obtenida()
                # except KeyError:
                    # Si aun no se ha ejecutado nada, no habra un resultado de ejecucion
                    # y no existira la llave de dicho resultado. Cuando eso pasa, se crea la
                    # llave requerida y se manda con None.
                # retorno_funcion = funcion_obtenida(
                #     transferencia_memoria=cache_ejecuciones_temporal[nombre_transferencia],
                #     memoria_total=memoria_total
                # )
            # except TypeError:
                # Se ejecuta la funcion guardada en esa opcion.
            if argumentos_obtenidos is not None:
                retorno_funcion = funcion_obtenida(*argumentos_obtenidos)
            else:
                retorno_funcion = funcion_obtenida()
            __limpar_cli()
            

            # Se guarda el resultado de la funcion en un diccionario.
            # cache_ejecuciones_temporal[nombre_transferencia] = retorno_funcion
            if regresar_en_seleccion:
                return retorno_funcion
            else:
                if retorno_funcion not in varios_retornos:
                    varios_retornos.append(retorno_funcion)
        elif tecla == Teclas().tec_retroceso or tecla == Teclas().com_ctrl_c:
            __limpar_cli()
            if principal:
                # Si es principal, y se aprieta salir, cierra el programa.
                print('Hasta luego')
                return
            else:  
                # Si no es principal, se sale del menu y regresa los retornos acumulados.
                return varios_retornos

        regresar_cursor_inicio_pantalla()
        
        
def __centrar_cuadricula(elementos, 
                         max_tam, 
                         i_fila_sel, 
                         i_col_sel,
                         modificable=True,
                         alineacion='center'):
    lineas_checadas = []
    for i_fila, fila in enumerate(elementos):
        para_hacer_linea = []
        for i_col, col in enumerate(fila):
            if col == '' and not ((i_fila, i_col) == (i_fila_sel, i_col_sel)):
                msj_vacio = comentario(MSJ_VACIO)
                nueva_col = alinear_linea_izquierda(
                    msj_vacio[I_CADENA_COLOR], 
                    max_tam + EXTRA_ESP_CURSOR + (EXTRA_ESP_CARET if modificable else 0),
                    msj_vacio[I_TAM_CADENA_COLOR],
                    ESP_BLANCO_TABLA
                )
            elif (i_fila, i_col) == (i_fila_sel, i_col_sel):
                if col == '':
                    vacio_seleccionado = seleccion(MSJ_VACIO, CURSOR)
                    nueva_col = alinear_linea_izquierda(
                        vacio_seleccionado[I_CADENA_COLOR],
                        max_tam + (EXTRA_ESP_CARET if modificable else 0),
                        vacio_seleccionado[I_TAM_CADENA_COLOR],
                        ESP_BLANCO_TABLA
                    )
                else:
                    if not modificable:
                        seleccion_cursor = seleccion(col, CURSOR)
                    elif len(col) == max_tam:
                        seleccion_cursor = seleccion(col, CURSOR)
                    else:
                        seleccion_cursor = seleccion_modificable(col, CURSOR)
                    nueva_col = alinear_linea_izquierda(
                        seleccion_cursor[I_CADENA_COLOR],
                        max_tam,
                        seleccion_cursor[I_TAM_CADENA_COLOR],
                        ESP_BLANCO_TABLA
                    ) 
            else:
                nueva_col = alinear_linea_izquierda(
                    col,
                    max_tam + EXTRA_ESP_CURSOR + (EXTRA_ESP_CARET if modificable else 0),
                    len(col),
                    ESP_BLANCO_TABLA
                )
            para_hacer_linea.append(nueva_col)
        lineas_checadas.append(para_hacer_linea)
    
    lineas_en_columnas = tabulate(lineas_checadas, tablefmt='orgtbl', stralign=alineacion)
    lineas_en_columnas = lineas_en_columnas.replace(ESP_BLANCO_TABLA, ' ').splitlines()
        
    return lineas_en_columnas


def __centrar_formatear_noticia(noticia: str, espacio: int, 
                                max_len_noticias: int, formato) -> str:
    """
    Solo debe recibir:
    ```
    noticia:            "cualquier cadena de texto"
    espacio:            1-n
    max_len_noticas:    el tam de la noticia mas grande
    formato:            advertencia | error | correcto | ayuda
    
    # espacio recibe cualquier numero del 1 en adelante
    # formato recibe funciones sin callback
    ```
    """
    espacio_alineado = max_len_noticias + ESP_EXTRA_NOTICIAS
    formateada, tam = formato(noticia)
    alinieada_izquierda = alinear_linea_izquierda(formateada, espacio_alineado, tam)
    centrada = centrar_linea(alinieada_izquierda, espacio, espacio_alineado)
    
    return centrada


def pantalla_agregado_centrada(tam_max_agregado: int,
                               lim_cant_agregados: int,
                               mensaje = 'agregar elementos',
                               nombre_elemento = 'elemento',
                               transferencia: list = None,
                               numerico: bool = False,
                               ref_transferencia: str = None,):
    agregado = [] if transferencia is None else transferencia
    i_fila_seleccion = 0
    i_col_seleccion = 0
    ultimo_tam_cols, ultimo_tam_filas = tam_consola()
    if ultimo_tam_cols > MAX_TAM_COLS:
            ultimo_tam_cols = MAX_TAM_COLS
    if ultimo_tam_filas > MAX_TAM_FILAS:
            ultimo_tam_filas = MAX_TAM_FILAS
            
    indicaciones = (
        ('flech', 'moverse'),
        ('Ctrl+A', 'agreg'),
        ('Ctrl+X', 'elim'),
        ('Retroc', 'borr'),
        ('Ctrl+R', 'regresar'),
    )
    
    advertencias = []
    errores = []
    correctos = []
    
    ultima_cantidad_de_noticias = 0
    nueva_cantidad_de_noticias = 0

    __limpar_cli()
    while True:
        
        if nueva_cantidad_de_noticias != ultima_cantidad_de_noticias:
            ultima_cantidad_de_noticias = nueva_cantidad_de_noticias
            __limpar_cli()
        
        # Se calcula el tam. de cada fila para la representacion
        # grafica.
        agregado_modificable = list(map(
            lambda string: f'{string}'.upper(), agregado
        ))
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
        
        cols_terminal, filas_terminal = tam_consola()
        if cols_terminal > MAX_TAM_COLS:
            cols_terminal = MAX_TAM_COLS
        if filas_terminal > MAX_TAM_FILAS:
            filas_terminal = MAX_TAM_FILAS
        
        # Para hacer bucle de selecccion.
        # Se llega al final regresa al comienzo y viceversa
        tam_agregado_ordenado = len(agregado_ordenado) - 1
        if i_fila_seleccion > tam_agregado_ordenado:
            i_fila_seleccion = 0
        elif i_fila_seleccion < 0:
            i_fila_seleccion = tam_agregado_ordenado
        try:
            tam_fila_seleccionada = len(agregado_ordenado[i_fila_seleccion]) - 1
        except IndexError:
            tam_fila_seleccionada = 0
        if i_col_seleccion > tam_fila_seleccionada:
            i_col_seleccion = 0
        elif i_col_seleccion < 0:
            i_col_seleccion = tam_fila_seleccionada

        if len(agregado_modificable) > 0:
            cols_agregado = max([len(fila) for fila in agregado_ordenado])
            agregados_alineados = __centrar_cuadricula(
                elementos=agregado_ordenado,
                max_tam=tam_max_agregado,
                i_fila_sel=i_fila_seleccion,
                i_col_sel=i_col_seleccion
            )
            agregados_centrados = list(map(
                lambda linea: centrar_linea(linea, 
                                            cols_terminal,
                                            len(limpiar_secuencias_ANSI(linea))),
                agregados_alineados
            ))
        else :
            cols_agregado = 0
            agregados_centrados = [centrar_linea(MSJ_SIN_ELEMENTOS, cols_terminal,
                                                 len(MSJ_SIN_ELEMENTOS))]
        
        encabezados = __formatear_encabezados(cols_terminal)
        pie = __indicaciones_personalizadas(indicaciones, cols_terminal)
        
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
        
        # Noticias de errores, advertencias o ejecuciones correctas.
        todas_las_noticias = advertencias + errores + correctos
        if len(todas_las_noticias) == 0:
            noticia_mas_grande = 0
        else:    
            noticia_mas_grande = max(list(map(len, todas_las_noticias)))
        advertencias_centradas = tuple(map(
            lambda noticia: __centrar_formatear_noticia(
                noticia, 
                cols_terminal,
                noticia_mas_grande,
                advertencia
            ),
            advertencias
        ))
        errores_centrados = tuple(map(
            lambda noticia: __centrar_formatear_noticia(
                noticia, 
                cols_terminal,
                noticia_mas_grande,
                error
            ),
            errores
        ))
        correctos_centrados = tuple(map(
            lambda noticia: __centrar_formatear_noticia(
                noticia, 
                cols_terminal,
                noticia_mas_grande,
                correcto
            ),
            correctos
        ))

        pantalla_agregado = [
            titulo_centrado,
            '',
            '',
            *agregados_centrados,
            '',
            '',
            *correctos_centrados,
            *advertencias_centradas,
            *errores_centrados
        ]
        pantalla_agregado_centrada = centrar_verticalmente('\n'.join(pantalla_agregado),
                                                           filas_terminal - ENC_PIE,
                                                           correccion=3)
        print(encabezados, pantalla_agregado_centrada, pie)
        
        # Se limpian las noticias para que no se muesten de nuevo cuando ya
        # no se necesitan mas.
        correctos.clear()
        advertencias.clear()
        errores.clear()
        nueva_cantidad_de_noticias = 0
        
        """ En esta parte se espera una tecla y se hace algo con el resultado """
        tecla = __leer_tecla()
        if tecla == TECLAS.tec_flecha_ar:
            # Esto hace que la seleccion queda centrada si esta seleccionada una
            # fila con un elemento, y se mueve el cursor hacia una fila de mas de
            # dos elementos. Lo logico seria que el cursor siguiera en el centro
            # y no se fuera hacia un lado.
            # TODO hacer que deje de centrar seleccion
            try:
                tam_seleccion_arriba = len(agregado_ordenado[i_fila_seleccion - 1]) - 1
                tam_fila_seleccionada = len(agregado_ordenado[i_fila_seleccion]) - 1
                if tam_fila_seleccionada < tam_seleccion_arriba:
                    i_col_seleccion = tam_seleccion_arriba // 2
            except IndexError:
                pass

            # Despues de la comprobacion anterior, se indica el cambio del cursor
            # hacia la fila de arriba (si es que existe).
            i_fila_seleccion -= 1
            
        elif tecla == TECLAS.tec_flecha_ab:
            # Del mismo modo que en la opcion de flecha arriba, si el cursor esta 
            # en una fila de menor tam. que la de arriba y se mueve hacia abajo
            # (siendo esta fila la ultima de abajo), el cursor regresa a la primera
            # fila, y es logico que lo haga en el centro o, por lo menos, es lo que
            # se sentiria mas natural. 
            try:
                tam_primera_fila = len(agregado_ordenado[0]) - 1
                tam_fila_seleccionada = len(agregado_ordenado[i_fila_seleccion]) - 1
                if tam_fila_seleccionada < tam_primera_fila:
                    i_col_seleccion = tam_primera_fila // 2
            except IndexError:
                pass
            
            # Despues de la comprobacion anterior, se indica el cambio del cursor
            # hacia la fila de abajo (si es que existe).
            i_fila_seleccion += 1
            
        elif tecla == TECLAS.tec_flecha_de:
            i_col_seleccion += 1
        elif tecla == TECLAS.tec_flecha_iz:
            i_col_seleccion -= 1
            
        elif tecla == TECLAS.com_ctrl_a:
            if len(agregado) < lim_cant_agregados:
                agregado.append('')
                correctos.append(f'Nuevo espacio para {nombre_elemento} creado.')
                if len(agregado) == (lim_cant_agregados - 1):
                    advertencias.append(f'Acercandose al limite ({lim_cant_agregados})')
                if len(agregado) == lim_cant_agregados:
                    advertencias.append(f'Has alcanzado el limite de {nombre_elemento}s'
                                       f' ({lim_cant_agregados})')
            else:
                if lim_cant_agregados == 1:
                    final = ''
                else:
                    final = 's'
                errores.append(f'Solo puedes agregar {lim_cant_agregados}'
                                    f' {nombre_elemento}{final}')
            __limpar_cli()
        elif tecla == TECLAS.com_ctrl_x:
            if len(agregado) > 0:
                i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
                eliminado = agregado.pop(i_original)
                if eliminado == '':
                    correctos.append(f'Espacio vacio eliminado correctamente.')
                else:
                    correctos.append(f'{eliminado} eliminado correctamente.')
            else:
                errores.append(f'No hay nada que borrar')
            __limpar_cli()
        elif tecla == TECLAS.com_ctrl_r or tecla == TECLAS.com_ctrl_c:
            __limpar_cli()
            if ref_transferencia is not None:
                return ref_transferencia, agregado
            else:
                return agregado
        if len(agregado) > 0:
            if tecla in LETRAS and not numerico:
                i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
                if len(agregado[i_original]) < tam_max_agregado:
                    agregado[i_original] += LETRAS_DIC[tecla]
            elif tecla in NUMEROS:
                i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
                if len(agregado[i_original]) < tam_max_agregado:
                    agregado[i_original] += NUMEROS_DIC[tecla]
            elif tecla == TECLAS.tec_retroceso:
                i_original = (i_fila_seleccion)*(cols_agregado) + (i_col_seleccion)
                if len(agregado[i_original]) > 0:
                    agregado[i_original] = agregado[i_original][:-1]  # Se le quita el ultimo caracter

        nueva_cantidad_de_noticias += len(errores) + len(advertencias) + len(correctos)
        regresar_cursor_inicio_pantalla()


def pantalla_de_mensajes(errores: List[str] = None, advertencias: List[str] = None, 
                         correctos: List[str] = None, ayudas: List[str] = None):
    if errores is None:
        errores = []    
    if advertencias is None:
        advertencias = []    
    if correctos is None:
        correctos = []    
    if correctos is None:
        correctos = []    
    
    indicaciones = (
        ('ENTER', 'continuar'),
    )
    
    cols_terminal, filas_terminal = tam_consola()
    if cols_terminal > MAX_TAM_COLS:
            cols_terminal = MAX_TAM_COLS
    if filas_terminal > MAX_TAM_FILAS:
            filas_terminal = MAX_TAM_FILAS
    
    todas = errores + advertencias + correctos + ayudas
    max_tam_todas = max(list(map(lambda x: len(x) + ESP_EXTRA_NOTICIAS, todas)))
            
    errore_formateados = list(map(lambda notic: __centrar_formatear_noticia(
        notic, cols_terminal, max_tam_todas, error
    ), errores))
    advert_formateadas = list(map(lambda notic: __centrar_formatear_noticia(
        notic, cols_terminal, max_tam_todas, advertencia
    ), advertencias))
    correc_formateados = list(map(lambda notic: __centrar_formatear_noticia(
        notic, cols_terminal, max_tam_todas, correcto
    ), correctos))
    ayudas_formateadas = list(map(lambda notic: __centrar_formatear_noticia(
        notic, cols_terminal, max_tam_todas, ayuda
    ), ayudas))
    
    encabezados = __formatear_encabezados(cols_terminal=cols_terminal)
    pie = __indicaciones_personalizadas(indicaciones, cols_terminal)
    todos_formateados = (errore_formateados +  
                            advert_formateadas + 
                            correc_formateados + 
                            ayudas_formateadas  )
    todos_unidos = '\n'.join(todos_formateados)
    todos_centrados_vert = centrar_verticalmente(todos_unidos, filas_terminal - ENC_PIE, 3)
    
    __limpar_cli()
    print(encabezados, todos_centrados_vert, pie)
    
    while True:
        tecla = __leer_tecla()
        if tecla == Teclas().tec_enter:
            __limpar_cli()
            break
        
        
def __comprobar_ult_tam_consola(cols_terminal: int, 
                                filas_terminal: int, 
                                ult_tam_cols_terminal: int, 
                                ult_tam_filas_terminal: int):
    """
    Compara el nuevo tam de consola obtenido con el útlimo.
    
    retorna
    -------
    ```
    (ult_tam_cols: int, ult_tam_filas: int, limpiar_cli: bool)
    ```
    """
    
    ult_tam_cols = ult_tam_cols_terminal
    ult_tam_filas = ult_tam_filas_terminal
    limpiar_cli = False
    if cols_terminal != ult_tam_cols_terminal:
        ult_tam_cols_terminal = cols_terminal
        if limpiar_cli is False:
            limpiar_cli = True
    if filas_terminal != ult_tam_filas_terminal:
        ult_tam_filas_terminal = filas_terminal
        if limpiar_cli is False:
            limpiar_cli = True
        
    return ult_tam_cols_terminal, ult_tam_filas_terminal, limpiar_cli


def __comprobar_medidas_max_consola(cols_terminal: int, filas_terminal: int):
    """
    Comprueba que la medida actual de la consola no exceda el máximo
    establecido.
    
    retorna
    -------
    ```
    (cols: int, filas: int)
    ```
    """
    cols = cols_terminal if cols_terminal < MAX_TAM_COLS else MAX_TAM_COLS
    filas = filas_terminal if filas_terminal < MAX_TAM_FILAS else MAX_TAM_FILAS
    return cols, filas


def __definir_indicaciones_pantalla_informacion(cant_paginas: int):
    """
    Retorna las indicaciones para la pantalla de informacion por
    páginas. Si solo es una página o ninguna, no genera la indicación
    para cambiar de página.
    
    retorna
    -------
    ```
    indicacione: tuple
    ```
    """
    if cant_paginas <= 1:
        indicaciones = (
            ('/\ \/ < >', 'moverse'),
            ('Retrc', 'regresar')
        )
    else:
        indicaciones = (
            ('/\ \/ < >', 'moverse'),
            ('Ctrl+flech', 'pag')
            ('Retrc', 'regresar')
        )
        
    return indicaciones


def __comprobar_posicion(mininmo: int, maximo: int, posicion: int, final: bool=False,
                         limite: int = None):
    """
    Se asegura que el valor posicion no exceda el maximo ni sea menor
    al minimo; si cruzan los límites retorna el maximo o minimo según sea
    requerido pero si no lo hacen retorna la posición.
    
    retorna
    ------
    ```
    minimo: int | minimo + 1 | maximo: int | posicion: int
    ```
    """
    if final:
        if limite + posicion < maximo:
            return limite + posicion
        elif limite + posicion >= maximo:
            return maximo
    elif posicion < mininmo:
        return mininmo
    elif posicion > maximo:
        return maximo
    else:
        return posicion
    
    
def __calcular_limite_pagina(tam_pagina, tam_total_dimension):
    """
    Calcula los límites vertical y horizontal de la página
    utilizando el tam designado de página (tam de visualización).
    
    retorna
    ------
    ```
    minimo: int | maximo: int | posicion: int
    ```
    """
    if tam_total_dimension > tam_pagina:
        limite_pagina = tam_total_dimension - tam_pagina
    else:
        limite_pagina = 0
    
    return limite_pagina


def __calcular_rangos_pagina(cant_renglones: int,
                             renglon_mas_grande: int,
                             tam_vertical: int, 
                             tam_horizontal: int,
                             pos_vertical: int,
                             poas_horizontal: int,
                             factor_avanze):
    """
    Genera los rangos para truncar una página.
    
    retorna
    ------
    ```
    (rango_vertical: slice, rango_horizontal: slice)
    ```
    """

    limite_comienzo_vertical = __calcular_limite_pagina(
        tam_vertical, 
        cant_renglones
    )
    limite_comienzo_horizontal = __calcular_limite_pagina(
        tam_horizontal, 
        renglon_mas_grande
    )

    comienzo_vertical = __comprobar_posicion(
        0, 
        limite_comienzo_vertical, 
        pos_vertical
    )
    comienzo_horizontal = __comprobar_posicion(
        0, 
        limite_comienzo_horizontal, 
        poas_horizontal
    )
    final_vertical = __comprobar_posicion(
        0, 
        cant_renglones, 
        pos_vertical,
        final=True,
        limite=tam_vertical
    )
    final_horizontal = __comprobar_posicion(
        0, 
        renglon_mas_grande, 
        poas_horizontal,
        final=True,
        limite=tam_horizontal
    )
        
    rango_vertical = slice(comienzo_vertical, final_vertical)
    rango_horizintal = slice(comienzo_horizontal, final_horizontal)
    
    return rango_vertical, rango_horizintal


def __renglon_mas_grande_pagina(pagina: str):
    """
    Retorna la cadena de texto mas grande de una página.
    
    Si recibe una cadena de un solo renglón, returna su
    tam.
    
    parámetros
    ----------
    pagina: ``'pagina con varios renglones\\nque incluyen retornos...'``
    
    retorna
    -------
    ```
    (renglon_mas_grande: int, cantidad_renglones: int, tams: list[int])
    ```
    """
    renglones = pagina.splitlines()  # Se obtienen los renglones de la pagina por separado.
    cantidad_renglones = len(renglones)  # Se cuentan los renglones
    tams = list(map(len, renglones))  # Se obtiene el tam de cada renglon.  
    renglon_mas_grande = max(tams)  # Se obtiene el tam max.
    
    return renglon_mas_grande, cantidad_renglones, tams
    
    
def __comprobar_num_pagina(ult_pagina: int, pag_seleccionada: int):
    """
    Comprueba si el numero de pagina existe.
    
    retorna
    -------
    ```
    pag_corregida: int  
    ```
    """
    pag_corregida = pag_seleccionada
    if pag_seleccionada > ult_pagina:
        pag_corregida = ult_pagina
    elif pag_seleccionada < 0:
        pag_corregida = 0
        
    return pag_corregida


def __truncar_pagina(pagina: str, rango_vertical: slice, rango_horizontal: slice):
    """
    Trunca la página según los rangos dados.
    
    retorna
    -------
    ```
    lineas_pagina_truncada: list
    ```
    """
    renglones = pagina.splitlines()
    truncado_vertical = renglones[rango_vertical]
    lineas_pagina_truncada = list(map(
        lambda renglon: renglon[rango_horizontal],
        truncado_vertical
    ))
    
    # print([rango_vertical], [rango_horizontal])
    # exit()
    
    return lineas_pagina_truncada

        
def pantalla_informacion_en_paginas(titulo_pantalla: str, 
                                    paginas: List[Tuple[str, str]]):
    """
    pantalla_informacion_en_paginas
    ===============================
    
    Crea pantalla para ver páginas de información que se adapta al tam de
    la consola.
    
    Una página hace referencia a una cadena de texto con más de un renglón,
    (al menos un salto de página "\\n").
    
    parámetros
    ----------
    titulo_pantalla: ``'titulo general'``
    paginas: ``[('titulo pagina', 'pagina...'), ...]``
    
    """
    PRIMERA_PAGINA = 0
    
    ultam_cols_term = 0 
    ultam_fls_term = 0
    num_pag_selec = 0
    posicion_hori = 0
    posicion_vert = 0
    factor_avanze = 2
    
    renglones_pags: List[Tuple[int, int, List[int]]] = []
    for _, pagina in paginas:
        renglones_pags.append(__renglon_mas_grande_pagina(pagina))
        
    total_paginas = len(paginas)
    ult_pagina = total_paginas - 1
    indicaciones = __definir_indicaciones_pantalla_informacion(total_paginas)
    
    __limpar_cli()
    while True:
        num_pag_selec = __comprobar_num_pagina(ult_pagina, num_pag_selec)
        cols_terminal, filas_terminal = tam_consola()
        ultam_cols_term, ultam_fls_term, limpiar = __comprobar_ult_tam_consola(
            cols_terminal=cols_terminal,
            filas_terminal=filas_terminal,
            ult_tam_cols_terminal=ultam_cols_term,
            ult_tam_filas_terminal=ultam_fls_term
        )
        __limpar_cli() if limpiar else None
        cols_terminal, filas_terminal = __comprobar_medidas_max_consola(
            cols_terminal=cols_terminal,
            filas_terminal=filas_terminal
        )
        
        try:
            titulo_pagina, pagina_actual = paginas[num_pag_selec]
            renglon_mas_grande_pag, cant_renglones, tams_reng = renglones_pags[num_pag_selec]
        except IndexError:
            num_pag_selec = PRIMERA_PAGINA
            titulo_pagina, pagina_actual = paginas[num_pag_selec]
            renglon_mas_grande_pag, cant_renglones, tams_reng = renglones_pags[num_pag_selec]
            
        max_tam_vertical = filas_terminal - ESP_TITULO_Y_ESPS_BLANCOS
        max_tam_horizontal = cols_terminal - ESP_CORRECCION_COLS_TERMINAL
        rango_vertical, rango_horizontal = __calcular_rangos_pagina(
            cant_renglones=cant_renglones,
            renglon_mas_grande=renglon_mas_grande_pag,
            tam_vertical=max_tam_vertical,
            tam_horizontal=max_tam_horizontal,
            pos_vertical=posicion_vert,
            poas_horizontal=posicion_hori,
            factor_avanze=factor_avanze
        )
        pagina_truncada = __truncar_pagina(
            pagina=pagina_actual,
            rango_vertical=rango_vertical,
            rango_horizontal=rango_horizontal
        )
                
        encabezados = __formatear_encabezados(cols_terminal)
        titulo_color, tam_titulo_color = titulo(titulo_pantalla, 2)
        subt_color, tam_subt_color = sub_titulo(titulo_pagina)
        titulo_centrado = centrar_linea(titulo_color, cols_terminal, tam_titulo_color)
        subt_centrado = centrar_linea(subt_color, cols_terminal, tam_subt_color)
        pie = __indicaciones_personalizadas(indicaciones, cols_terminal)

        # pagina_centrada = list(map(
        #     lambda linea: centrar_linea(linea, cols_terminal, len(linea)),
        #     pagina_truncada
        # ))
        en_blanco = ((filas_terminal - ENC_PIE_TITULO_SUBT) - len(pagina_truncada)) * ['']
        pagina_a_mostrar = '\n'.join(pagina_truncada + en_blanco)
        
        titulo_subt = '\n'.join([titulo_centrado, subt_centrado])
        print(encabezados, '' , titulo_subt, pagina_a_mostrar, pie, sep='\n')
        
        # print('ultam_cols_term: ', ultam_cols_term, '             ')
        # print('ultam_fls_term: ', ultam_fls_term, '             ')
        # print('num_pag_selec: ', num_pag_selec, '             ')
        # print('posicion_hori: ', posicion_hori, '             ')
        # print('posicion_vert: ', posicion_vert, '             ')
        # print('factor_avanze: ', factor_avanze, '             ')
        # print('rango_vertical: ', repr(rango_vertical), '             ')
        # print('rango_horizontal: ', repr(rango_horizontal), '             ')
        # print('max_tam_vertical: ', max_tam_vertical, '             ')
        # print('max_tam_horizontal: ', max_tam_horizontal, '             ')
        # print(
        #     'comparador aumento posicion_hori: ', 
        #     renglon_mas_grande_pag - max_tam_horizontal, 
        #     '             '
        # )
        # print(
        #     'comparador aumento posicion_vert: ',
        #     cant_renglones - max_tam_vertical,
        #     '             '
        # )
        
        tecla = __leer_tecla()
        if tecla == TECLAS.com_ctrl_flecha_iz:
            if num_pag_selec > 0:
                num_pag_selec -= 1
        elif tecla == TECLAS.com_ctrl_flecha_de:
            if num_pag_selec < len(paginas):
                num_pag_selec += 1
        if tecla == TECLAS.tec_flecha_iz:
            if posicion_hori > 0:
                posicion_hori -= 1
        elif tecla == TECLAS.tec_flecha_de:
            if posicion_hori < renglon_mas_grande_pag - max_tam_horizontal:
                posicion_hori += 1
        elif tecla == TECLAS.tec_flecha_ar:
            if posicion_vert > 0:
                posicion_vert -= 1
        elif tecla == TECLAS.tec_flecha_ab:
            if posicion_vert < cant_renglones - max_tam_vertical:
                posicion_vert += 1
        elif tecla == TECLAS.com_ctrl_c:
            exit(despedida())
        elif tecla == TECLAS.tec_retroceso:
            return
        
        regresar_cursor_inicio_pantalla()
        
        # exit()
    


def pantalla_carga(total, 
                   progreso,
                   total_els,
                   els_complet, 
                   titulo_carga='cargando', 
                   nombre_elemento='elemento',
                   elemento=None,
                   __logs_descargas=[]):
    
    if progreso - 1 < 1:
        __logs_descargas.clear()
        print(__logs_descargas)
    
    cols_terminal, filas_terminal = tam_consola()
    tam_barra = int(cols_terminal * .75) 
    alto_barra = int(filas_terminal * .25)
    alto_lista_logs = int(filas_terminal * .85) - ESP_TITULO_Y_ESPS_BLANCOS - alto_barra
    progreso_mostrar = progreso
    
    relleno = lambda fill: f'{Back.BLUE} {Style.RESET_ALL}' if fill else ' '
    if progreso < 0:
        progreso = 0
    if progreso > total:
        progreso = total
    cuanto_relleno = (progreso * tam_barra) // total
    lineas_barra = []
    if alto_barra >= 2:
        mitad_alto_barra = alto_barra // 2
    elif alto_barra == 1:
        mitad_alto_barra = 0
    
    if elemento != None:
        texto_log = MSJ_OBTENCION + elemento
        tam_correcto_log = tam_barra - len(PUNTOS_TEXTO_CORTADO) - len(f'[ {TRAZO} ] ') - 1
        try:
            list(texto_log)[tam_correcto_log]
            texto_log = texto_log[:tam_correcto_log]
            texto_log = ''.join([texto_log, PUNTOS_TEXTO_CORTADO])
        except IndexError:
            pass
        nuevo_log = log(texto_log, TRAZO)
        __logs_descargas.append(nuevo_log)

    logs_centrados = []
    for un_log, tam_log in __logs_descargas:
        log_alineado = alinear_linea_izquierda(
            un_log, 
            tam_barra, 
            tam_log,
            ' '
        )
        log_centrado = centrar_linea(
            log_alineado,
            cols_terminal,
            tam_barra,
            ' '
        )
        logs_centrados.append(log_centrado)
        
    for i_fila_barr in range(alto_barra):
        porce = round(((progreso_mostrar - 1) * 100) / total)
        digs_total_els = len(str(total_els))
        els_complet = str(els_complet).zfill(digs_total_els)
        msj_progreso, len_msj_prog = negativo(f'{porce}% | {els_complet}/{total_els} {nombre_elemento}s')
        if i_fila_barr == mitad_alto_barra:
            tam_izq_barr = (tam_barra-len_msj_prog) // 2
            tam_der_barr = (tam_barra-len_msj_prog) - tam_izq_barr
            izq_barra = "".join([
                relleno(
                    True if pos_barra <= cuanto_relleno else False
                ) 
                for pos_barra in range(tam_izq_barr)
            ])
            der_barra = "".join([
                relleno(
                    True if pos_barra <= (cuanto_relleno - len_msj_prog - tam_izq_barr) else False
                ) 
                for pos_barra in range(tam_der_barr)
            ])
            barra_prog = ''.join([izq_barra, msj_progreso, der_barra])
        else:
            barra_prog = "".join([
                relleno(
                    True if pos_barra <= cuanto_relleno else False
                ) 
                for pos_barra in range(tam_barra)
            ])
        barra_prog = ''.join(['|', barra_prog, '|'])

        linea_nueva = centrar_linea(
            barra_prog,
            cols_terminal,
            len(limpiar_secuencias_ANSI(barra_prog))
        )
        lineas_barra.append(linea_nueva)
       
    tam_logs_centrados = len(logs_centrados) 
    if tam_logs_centrados > alto_lista_logs:
        slice_para_mostrar = slice(tam_logs_centrados - 1 - alto_lista_logs, -1)
    else:
        slice_para_mostrar = slice(0, -1)
        
    encabezados = __formatear_encabezados(cols_terminal)
    titulo_a_mostrar, len_titu = titulo(titulo_carga, 3)
    titulo_a_mostrar = centrar_linea(titulo_a_mostrar, cols_terminal, len_titu)
    cuerpo_pantalla_carga = [
        '',
        '',
        titulo_a_mostrar,
        '',
        '',
        *lineas_barra,
        '',
    ]
    
    lista_logs = '\n'.join(logs_centrados[slice_para_mostrar])
    barra_char = '\n'.join(cuerpo_pantalla_carga)
    regresar_cursor_inicio_pantalla()
    print(encabezados, barra_char, lista_logs, sep='\n')
    

         

if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando desde cli.py')
