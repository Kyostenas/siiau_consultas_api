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


import json
import re
from .utiles import convertir_a_dict_recursivamente, tam_consola
from .servicio_tabla import tabla_dos_columnas_valores
from .esquemas import Opcion, Teclas, CentroCompleto, CarreraCompleta, ClaseCompleta
from .getch import getch
from .servicio_consulta_siiau import oferta_academica, Siiau, centros, carreras, clases
from .servicio_oferta_siiau import estructurar_oferta_como_horario
from .cli import menu_generico_seleccion as menu_gen, sub_titulo
from .cli import pantalla_agregado_centrada as pantalla_para_agregar
from .cli import titulo, advertencia, error, correcto, ayuda, log, seleccion
from .cli import (pantalla_carga,
                  pantalla_informacion_en_paginas,
                  pantalla_de_mensajes,
                  __leer_tecla)

from typing import List, Tuple
import os
    

# TODO Agregar interfaz para uso en consola

RAIZ_US = os.path.expanduser(f'~')
SEP = os.sep
TEXTO_COLOR = 0
TRAZO = 'siiaucli'

# (o-------------------------- TRANSFERENCIA INTERNA --------------------------o)
info_ejecucion = {}
TIPO = 'tipo'
SELECCIONES = 'selecciones'

# NOMBRES OPCIONES MENU PRINCIPAL
MNU_OFERTA = 'mnu_oferta'
MNU_CENTROS = 'mnu_centros' 

# NOMBRES AGREGADOS
AGR_CLASES = 'clases_agregadas'
AGR_NRCS_EXCLUSIVOS = 'nrcs_exclusivos'

# MENUS SELECCION (SEL -> SELECCION)
MNU_SEL_CENTROS = 'centros_seleccionados'
MNU_SEL_CARRERAS = 'carrera_seleccionadas'
MNU_SEL_CLASES = 'clases_seleccionadas'
# (o-------------------------------------o-------------------------------------o)


# (o------------------------ ALMACENAJE DE INFORMACION ------------------------o)
# NOMBRES CARPETAS (N -> NOMBRE, CARP -> CARPETA)
NCARP_RAIZ = '.siiaucli'
NCARP_USUARIOS = 'usuarios'
NCAPR_CACHE = 'cachetemp'
# carpetas del usuario (US -> USUARIO)
NCARPUS_CARRERAS = 'carreras'
NCARPUS_SEMESTRES = 'semestres'
NCARPUS_OFERTA = 'oferta'

# DIRECCIONES CARPETAS (D -> DIRECTORIO, CARP -> CARPETA)
DCARP_RAIZ = f'{RAIZ_US}{SEP}{NCARP_RAIZ}{SEP}'
DCARP_USUARIOS = f'{DCARP_RAIZ}{NCARP_USUARIOS}{SEP}'
DCARP_CACHE = f'{DCARP_RAIZ}{NCAPR_CACHE}{SEP}'
# carpetas del usuario (US -> USUARIO)
DCARPUS_CARRERAS = lambda usuario: f'{DCARP_USUARIOS}{usuario}{SEP}{NCARPUS_CARRERAS}{SEP}'
DCARPUS_SEMESTRES = lambda usuario: f'{DCARP_USUARIOS}{usuario}{SEP}{NCARPUS_SEMESTRES}{SEP}'
DCARPUS_OFERTA = lambda usuario: f'{DCARP_USUARIOS}{usuario}{SEP}{NCARPUS_OFERTA}{SEP}'
# (o-------------------------------------o-------------------------------------o)


def _crear_opcion(nombre_opcion: str, funcion, *args) -> Opcion:
    argumentos = [*args] if args != None else None
    return Opcion(nombre_opcion, funcion, argumentos)


# (o-------------------------------------o-------------------------------------o)
# |                              CONSULTAR OFERTA                               |
# |:-------------------------------------o-------------------------------------:|
# | inicio                                                               inicio |


def __agregar_clases_para_consultar():
    try:
        transferencia = info_ejecucion[MNU_OFERTA][AGR_CLASES]
    except KeyError:
        transferencia = []
    retorno = pantalla_para_agregar(
        7, 15, 'agregar clases', 'clave', transferencia=transferencia
    )
    info_ejecucion[MNU_OFERTA][AGR_CLASES] = retorno
    

def __agregar_nrcs_exclusivos():
    try:
        mat_agregadas = info_ejecucion[MNU_OFERTA][AGR_CLASES]
    except KeyError:
        pantalla_de_mensajes(
            errores=[
                'No hay clases registradas aun'
            ],
            ayudas=[
                'Primero registra una materia en "agregar clases para consultar"'
            ]
        )
        return
    try:
        materias_anteriores = info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS].keys()
        if mat_agregadas != materias_anteriores:
            for materia in mat_agregadas:
                if materia not in materias_anteriores:
                    info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS][materia] = []        
        transferencia = info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS]
    except KeyError:
        info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS] = {
            llave : [] for llave in mat_agregadas
        }
        transferencia = info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS]
        
    titulo_menu = 'agregar nrcs exclusivos'
    sub_titulo_menu = 'agrega clases exclusivas para tu carrera'
    opciones = list(map(lambda cve_materia: _crear_opcion(
        cve_materia, 
        pantalla_para_agregar, 
        
        # Desde aqui son argumentos para "panta_para_agregar"g
        6, 
        30, 
        f'agregar nrcs exclusivos para {cve_materia}', 
        'nrc exclusivo',
        transferencia[cve_materia],
        True,
        cve_materia
        # Hasta aqui son argumentos para "panta_para_agregar"
        
    ), mat_agregadas))
    retorno = menu_gen(
        opciones,
        False,
        titulo_menu,
        sub_titulo_menu
    )
    for nrcs_excl_una_materia in retorno:
        cve_materia, nrcs_exclusivos = nrcs_excl_una_materia
        info_ejecucion[MNU_OFERTA][AGR_NRCS_EXCLUSIVOS][cve_materia] = nrcs_exclusivos


def __menu_consultar_oferta():
    try:
        info_ejecucion[MNU_OFERTA]
    except KeyError:
        info_ejecucion[MNU_OFERTA] = {}
    titulo_menu = 'consultar oferta'
    sub_titulo_menu = 'consulta y procesa la oferta academica'
    opciones = [
        Opcion('agregar clases para consultar', __agregar_clases_para_consultar, None),
        Opcion('agregar nrcs exclusivos', __agregar_nrcs_exclusivos, None),
        Opcion('ver clases agregadas', str, None),
        Opcion('ver clases', str, None),
        Opcion('generar posibles horarios', str, None),
    ]
    menu_gen(
        opciones, 
        False,
        titulo_menu, 
        sub_titulo_menu, 
    )



# | fin                                                                     fin |
# |:-------------------------------------o-------------------------------------:|
# |                              CONSULTAR OFERTA                               |
# (o-------------------------------------o-------------------------------------o)



# (o-------------------------------------o-------------------------------------o)
# |                             CONSULTAR CENTROS                               |
# |:-------------------------------------o-------------------------------------:|
# | inicio                                                               inicio |


def __menu_centros():
    titulo = 'centros universitarios de la UDG'
    opciones = []
    centros_universitarios = centros()
    for un_centro in centros_universitarios:
        nombre_centro = un_centro.nombre_completo
        def retornar_centro(centro=un_centro): return centro
        nueva_opcion = Opcion(nombre_centro, retornar_centro, None)
        opciones.append(nueva_opcion)
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        regresar_en_seleccion=True,
        cuadricula=True,
    )
    
    if retorno is None:
        return None

    try:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CENTROS][SELECCIONES].append(retorno)
    except KeyError:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CENTROS] = {TIPO: CentroCompleto.__name__}
        info_ejecucion[MNU_CENTROS][MNU_SEL_CENTROS][SELECCIONES] = [retorno]
        


def __menu_carreras():
    try:
        centro: CentroCompleto = (
            info_ejecucion[MNU_CENTROS][MNU_SEL_CENTROS][SELECCIONES][-1]
        )
        if centro is None:
            return None
    except KeyError:
        return None
    
    titulo = f'carreras de {centro.nombre_completo}'
    opciones = []
    carreras_centro = carreras(centro.id_centro)
    for una_carrera in carreras_centro:
        ref_carrera = una_carrera.ref_carrera
        def retornar_carrera(carrera=una_carrera): return carrera
        nueva_opcion = Opcion(ref_carrera, retornar_carrera, None)
        opciones.append(nueva_opcion)
    memoria_total = {}
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        regresar_en_seleccion=True,
        cuadricula=True
    )
    
    try:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CARRERAS][SELECCIONES].append(retorno)
    except KeyError:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CARRERAS] = {TIPO: CarreraCompleta.__name__}
        info_ejecucion[MNU_CENTROS][MNU_SEL_CARRERAS][SELECCIONES] = [retorno]
        


def __menu_clases():
    try:
        carrera: CarreraCompleta = (
            info_ejecucion[MNU_CENTROS][MNU_SEL_CARRERAS][SELECCIONES][-1]
        )
        if carrera is None:
            return None
    except KeyError:
        return None
    
    titulo = f'clases de {carrera.nombre_completo} ({carrera.ref_carrera})'
    titulo_barra = f'descargando y procesando clases de {carrera.ref_carrera}'
    opciones = []
    clases_carrera = clases(carrera.ref_carrera)
    for progreso, total, obtenidas, ref_elemento, els_comp, els_totales in clases_carrera:
        if obtenidas == None:
            pantalla_carga(
                total, 
                progreso,
                els_totales,
                els_comp, 
                titulo_barra, 
                'materia', 
                ref_elemento
            )
        else:
            for una_materia in obtenidas:
                una_materia: ClaseCompleta
                if len(una_materia.titulo) <= 15:
                    titulo_materia = una_materia.titulo
                else:
                    titulo_materia = una_materia.titulo[:15] + "..."
                nombre_materia = f'{una_materia.clave} {titulo_materia}'
                def retornar_materia(materia=una_materia): return materia
                nueva_opcion = Opcion(nombre_materia, retornar_materia, None)
                opciones.append(nueva_opcion)
    memoria_total = {}
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        regresar_en_seleccion=True,
        cuadricula=True
    )
    
    try:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CLASES][SELECCIONES].append(retorno)
    except KeyError:
        info_ejecucion[MNU_CENTROS][MNU_SEL_CLASES] = {TIPO: ClaseCompleta.__name__}
        info_ejecucion[MNU_CENTROS][MNU_SEL_CLASES][SELECCIONES] = [retorno]


def __consultar_centros():
    cols_terminal, _ = tam_consola()
    info_ejecucion[MNU_CENTROS] = {}
    
    __menu_centros()
    centro = True
    carrera = True
    clase = True
    while True:
        if centro:
            __menu_carreras()
            centro = False
        if carrera:
            __menu_clases()
            carrera = False
        if clase:
            try:
                clase_obtenida = (
                    info_ejecucion[MNU_CENTROS][MNU_SEL_CLASES][SELECCIONES][-1]
                )
                if clase_obtenida is None:
                    return None
            except KeyError:
                return None
            
            tabla_materia = tabla_dos_columnas_valores(clase_obtenida, cols_terminal)
            pantalla_informacion_en_paginas(
                titulo_pantalla='INFORMACION DE MATERIA',
                paginas=[(clase_obtenida.clave, tabla_materia)]
            )
            clase = False

            return


# | fin                                                                     fin |
# |:-------------------------------------o-------------------------------------:|
# |                             CONSULTAR CENTROS                               |
# (o-------------------------------------o-------------------------------------o)


def menu_principal():
    titulo_menu = 'menu principal'
    opciones = [
        Opcion('consultar oferta', __menu_consultar_oferta, None),
        Opcion('consultar centros', __consultar_centros, None),
        Opcion('* iniciar sesion', str, None),
        Opcion('consultar mi horario actual', str, None),
        Opcion('consultar mis carreras', str, None),
        Opcion('consultar mis horarios generados', str, None),
        Opcion('registrar clases', str, None),
    ]
    
    # memoria_total = {}
    menu_gen(
        opciones, 
        True, 
        titulo_menu=titulo_menu, 
    )
    
    info_final = convertir_a_dict_recursivamente(info_ejecucion)
    print(json.dumps(info_final, indent=4))
    
    # exit(print(retorno_final, '\n', memoria_total))


def __existe_directorio(directorio: str) -> bool:
    """
    Comprueba si exsite directorio. Si no
    existe, lo hace.
    """
    if os.path.isdir(directorio):
        return True
    else:
        return False
    

def __comprobar_directorios(*directorios) -> List[str]:
    directorios_por_crear = []
    for directorio in directorios:
        if __existe_directorio(directorio):
            print(log(correcto(f'"{directorio}" encontrado')[TEXTO_COLOR], TRAZO)[TEXTO_COLOR])
        else:
            print(log(advertencia(f'"{directorio}" no existe')[TEXTO_COLOR], TRAZO)[TEXTO_COLOR])
            directorios_por_crear.append(directorio)
    return directorios_por_crear

    
def main():
    teclas = Teclas()
    print(titulo('INICIALIZANDO SIIAU-CLI')[TEXTO_COLOR], end='\n\n')
    print(log('comprobando directorios', TRAZO)[TEXTO_COLOR])
    directorios_por_crear = __comprobar_directorios(DCARP_USUARIOS, DCARP_CACHE)
    if directorios_por_crear.__len__() > 0:
        char_crear_carpetas = ' '
        incorrecto = False
        preguntar_de_nuevo = True
        pregunta = log('¿crear carpetas? (S/N)', TRAZO)[TEXTO_COLOR]
        while True:
            if incorrecto:
                char_rojo = error(char_crear_carpetas, mostrar_pre=False)[TEXTO_COLOR]
                print(f'{pregunta} {char_rojo}', flush=True, end='\r')
            else:
                print(f'{pregunta} {char_crear_carpetas}', flush=True, end='\r')
            if preguntar_de_nuevo:
                crear_carpetas, char_crear_carpetas = __leer_tecla(retornar_original=True)
                if crear_carpetas in [teclas.tec_flecha_ar, teclas.tec_flecha_ab]:
                    crear_carpetas = ''
            else:
                preguntar_de_nuevo = True
            if crear_carpetas == teclas.com_ctrl_c:
                exit(print('Hasta luego'))
            if char_crear_carpetas in ['N', 'n', 'S', 's']:
                if incorrecto:
                    incorrecto = False
                print(f'{pregunta} {char_crear_carpetas}', flush=True, end='\r')
                aux = char_crear_carpetas
                enter, char_crear_carpetas = __leer_tecla(retornar_original=True)
                if enter in [teclas.tec_flecha_ar, teclas.tec_flecha_ab]:
                    enter = ''
                if enter == teclas.tec_enter:
                    char_crear_carpetas = aux
                    if char_crear_carpetas in ['S', 's']:
                        crear = True
                        break
                    elif char_crear_carpetas in ['N', 'n']:
                        crear = False
                        break
                    else:
                        pass
                elif enter == teclas.com_ctrl_c:
                    exit(print('Hasta luego'))
                else:
                    preguntar_de_nuevo = False
            else:
                incorrecto = True

        pregunta = log('¿Crear carpetas?', TRAZO)[TEXTO_COLOR]
        print(' ' * os.get_terminal_size()[0], flush=True, end='\r')
        print(pregunta, sub_titulo(char_crear_carpetas)[TEXTO_COLOR], flush=True)
        
        if crear:
            for directorio in directorios_por_crear:
                os.makedirs(directorio)
                print(log(correcto(f'{directorio} creado')[TEXTO_COLOR], TRAZO)[TEXTO_COLOR])
        else:
            msj_error = log(error(
                'se requieren los directorios para funcionar'
            )[TEXTO_COLOR], TRAZO)[TEXTO_COLOR]
            exit(print(msj_error))
    
    print(log('presione ENTER para comenzar', TRAZO)[TEXTO_COLOR])
    while True:
        tecla = __leer_tecla()
        if tecla == teclas.tec_enter:
            break
        elif tecla == teclas.com_ctrl_c:
            exit(print('Hasta luego'))
    
    menu_principal()

