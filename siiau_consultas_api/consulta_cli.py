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


from token import TYPE_COMMENT
from .cli import menu_generico_seleccion as menu_gen, sub_titulo
from .cli import pantalla_agregado_centrada as pantalla_para_agregar
from .cli import pantalla_de_mensajes, __leer_tecla
from .cli import titulo, advertencia, error, correcto, ayuda, log, seleccion
from .esquemas import Opcion, Teclas
from .getch import getch

from typing import List
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
AGR_MATERIAS = 'AGR_MATERIAS'
AGR_NRCS_EXCLUSICOS = 'AGR_NRCS_EXCLUSICOS'
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


def __agregar_nrcs_exclusivos(transferencia_memoria, memoria_total, ruta):
    if transferencia_memoria is None:
        transferencia_memoria = {}
    try:
        transf_mat_agregadas = memoria_total[MNU_OFERTA][AGR_MATERIAS]
    except KeyError:
        pantalla_de_mensajes(
            errores=[
                'No hay materias registradas aun'
            ],
            ayudas=[
                'Primero registra una materia en "agregar materias para consultar"'
            ]
        )
        return transferencia_memoria
    opciones = list(map(lambda x: _crear_opcion(
        x, pantalla_para_agregar(6, 1, 'agregar nrcs exclusivos', 'nrc exclusivo')
    ), transf_mat_agregadas))
    
    
def __agregar_materias_para_consultar(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = []
    transferencia_memoria = pantalla_para_agregar(
        7, 15, 'agregar materias', 'clave', transferencia_memoria
    )
    
    return transferencia_memoria


def __menu_consultar_oferta(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = {}
    titulo_menu = 'consultar oferta'
    sub_titulo_menu = 'consulta y procesa la oferta academica'
    opciones = [
        Opcion('agregar materias para consultar', __agregar_materias_para_consultar, AGR_MATERIAS),
        Opcion('agregar nrcs exclusivos', __agregar_nrcs_exclusivos, AGR_NRCS_EXCLUSICOS),
        Opcion('ver materias agregadas', str, ''),
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


def __consultar_centros(transferencia_memoria, memoria_total):
    if transferencia_memoria is None:
        transferencia_memoria = {}
    
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
        Opcion('registrar materias', str, ''),
    ]
    
    memoria_total = {}
    retorno_final = menu_gen(opciones, True, titulo_menu=titulo_menu, memoria_total=memoria_total)
    
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

