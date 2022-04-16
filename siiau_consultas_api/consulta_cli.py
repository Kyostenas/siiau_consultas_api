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


from .utiles import barra_progreso, tam_consola
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
# NOMBRES OPCIONES MENU PRINCIPAL
MNU_OFERTA = 'MNU_OFERTA'
MNU_CENTROS = 'MNU_CENTROS' 

# NOMBRES AGREGADOS
AGR_CLASES = 'AGR_CLASES'
AGR_NRCS_EXCLUSICOS = 'AGR_NRCS_EXCLUSICOS'

# MENUS SELECCION (SEL -> SELECCION)
MNU_SEL_CENTROS = 'MNU_SEL_CENTROS'
MNU_SEL_CARRERAS = 'MNU_SEL_CARRERAS'
MNU_SEL_CLASES = 'MNU_SEL_CLASES'
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


def _crear_opcion(nombre_opcion: str, funcion):
    return Opcion(nombre_opcion, funcion, nombre_opcion)


# (o-------------------------------------o-------------------------------------o)
# |                              CONSULTAR OFERTA                               |
# |:-------------------------------------o-------------------------------------:|
# | inicio                                                               inicio |


def __agregar_nrcs_exclusivos(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = {}
    try:
        transf_mat_agregadas = memoria_total[MNU_OFERTA][AGR_CLASES]
    except KeyError:
        pantalla_de_mensajes(
            errores=[
                'No hay clases registradas aun'
            ],
            ayudas=[
                'Primero registra una materia en "agregar clases para consultar"'
            ]
        )
        return transferencia_memoria
    opciones = list(map(lambda x: _crear_opcion(
        x, pantalla_para_agregar(6, 1, 'agregar nrcs exclusivos', 'nrc exclusivo')
    ), transf_mat_agregadas))
    
    
def __agregar_clases_para_consultar(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = []
    transferencia_memoria = pantalla_para_agregar(
        7, 15, 'agregar clases', 'clave', transferencia_memoria
    )
    
    return transferencia_memoria


def __menu_consultar_oferta(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = {}
    titulo_menu = 'consultar oferta'
    sub_titulo_menu = 'consulta y procesa la oferta academica'
    opciones = [
        Opcion('agregar clases para consultar', __agregar_clases_para_consultar, AGR_CLASES),
        Opcion('agregar nrcs exclusivos', __agregar_nrcs_exclusivos, AGR_NRCS_EXCLUSICOS),
        Opcion('ver clases agregadas', str, ''),
        Opcion('ver clases', str, ''),
        Opcion('generar posibles horarios', str, ''),
    ]
    transferencia_memoria = menu_gen(
        opciones, 
        False,
        memoria_total,
        titulo_menu, 
        sub_titulo_menu, 
        transferencia_memoria
        )

    return transferencia_memoria


# | fin                                                                     fin |
# |:-------------------------------------o-------------------------------------:|
# |                              CONSULTAR OFERTA                               |
# (o-------------------------------------o-------------------------------------o)



# (o-------------------------------------o-------------------------------------o)
# |                             CONSULTAR CENTROS                               |
# |:-------------------------------------o-------------------------------------:|
# | inicio                                                               inicio |


def __menu_centros() -> CentroCompleto:
    titulo = 'centros universitarios de la UDG'
    opciones = []
    centros_universitarios = centros()
    for un_centro in centros_universitarios:
        nombre_centro = un_centro.nombre_completo
        def retornar_centro(centro=un_centro): return centro
        nueva_opcion = Opcion(nombre_centro, retornar_centro, MNU_SEL_CENTROS)
        opciones.append(nueva_opcion)
    memoria_total = {}
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        memoria_total=memoria_total,
        regresar_en_seleccion=True,
        cuadricula=True,
        
    )
    try:
        centro = retorno[MNU_SEL_CENTROS]
    except KeyError:
        centro = None
    
    return centro


def __menu_carreras(centro: CentroCompleto) -> CarreraCompleta:
    titulo = f'carreras de {centro.nombre_completo}'
    opciones = []
    carreras_centro = carreras(centro.id_centro)
    for una_carrera in carreras_centro:
        ref_carrera = una_carrera.ref_carrera
        def retornar_carrera(carrera=una_carrera): return carrera
        nueva_opcion = Opcion(ref_carrera, retornar_carrera, MNU_SEL_CARRERAS)
        opciones.append(nueva_opcion)
    memoria_total = {}
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        memoria_total=memoria_total,
        regresar_en_seleccion=True,
        cuadricula=True
    )
    try:
        carrera = retorno[MNU_SEL_CARRERAS]
    except KeyError:
        carrera = None
        
    
    return carrera


def __menu_clases(carrera: CarreraCompleta) -> ClaseCompleta:
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
                nueva_opcion = Opcion(nombre_materia, retornar_materia, MNU_SEL_CLASES)
                opciones.append(nueva_opcion)
    memoria_total = {}
    retorno = menu_gen(
        opciones, 
        principal=False, 
        titulo_menu=titulo, 
        memoria_total=memoria_total,
        regresar_en_seleccion=True,
        cuadricula=True
    )
    try:
        clase = retorno[MNU_SEL_CLASES]
    except KeyError:
        clase = None
    
    return clase


def __consultar_centros(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = []
    historial = []
    cols_terminal, _ = tam_consola()

    centro = __menu_centros()
    carrera = None
    clase = None
    if centro != None:
        carrera = __menu_carreras(centro)
    if carrera != None:
        clase = __menu_clases(carrera)
    if clase != None:
        tabla_materia = tabla_dos_columnas_valores(clase, cols_terminal)
        pantalla_informacion_en_paginas(
            titulo_pantalla='INFORMACION DE MATERIA',
            paginas=[(clase.clave, tabla_materia)]
        )
        
    return transferencia_memoria 


# | fin                                                                     fin |
# |:-------------------------------------o-------------------------------------:|
# |                             CONSULTAR CENTROS                               |
# (o-------------------------------------o-------------------------------------o)


def menu_principal():
    titulo_menu = 'menu principal'
    opciones = [
        Opcion('consultar oferta', __menu_consultar_oferta, MNU_OFERTA),
        Opcion('consultar centros', __consultar_centros, MNU_CENTROS),
        Opcion('* iniciar sesion', str, ''),
        Opcion('consultar mi horario actual', str, ''),
        Opcion('consultar mis carreras', str, ''),
        Opcion('consultar mis horarios generados', str, ''),
        Opcion('registrar clases', str, ''),
    ]
    
    memoria_total = {}
    retorno_final = menu_gen(
        opciones, 
        True, 
        titulo_menu=titulo_menu, 
        memoria_total=memoria_total
    )
    
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

