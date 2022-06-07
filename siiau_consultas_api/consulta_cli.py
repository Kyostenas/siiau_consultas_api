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

# from .utiles import convertir_a_dict_recursivamente, tam_consola
# from .servicio_tabla import tabla_dos_columnas_valores, tabla_generica
from email.policy import default
from .esquemas import (
    CarreraEstudiante,
    Opcion, 
    Teclas, 
    CentroCompleto, 
    CarreraCompleta, 
    ClaseCompleta,
    DatosSesion,
    DatosHorarioSiiau
)
from .getch import getch
from .servicio_consulta_siiau import (
    grupo_de_clases, 
    oferta_academica, 
    Alumno, 
    centros, 
    carreras, 
    clases
)
from .colores import (
    titulo, 
    advertencia, 
    error, 
    correcto, 
    ayuda, 
    log, 
    seleccion,
    sub_titulo
)
from .utiles import (
    leer_tecla,
    imprimir,
    leer_archivo_dat,
    escribir_archivo_dat,
    leer_json,
    escribir_json,
    escribir_excel
)
from .servicio_tabla import (
    tabla_dos_columnas_valores,
    tabla_generica,
    named_tuple_a_tabla
)
from .servicio_horario_siiau import (
    compactar_horario_por_clases,
    estructurar_horario_por_clases,
)

from typing import List, Tuple
from os import get_terminal_size
import json
import re
import click
import os
    

# TODO Agregar interfaz para uso en consola

RAIZ_US = os.path.expanduser(f'~')
SEP = os.sep
TEXTO_COLOR = 0
TRAZO = 'siiaucli'
LIMPIAR = '\r'
TECLAS = Teclas()
seesion = None
CICLO_GENERICO = 200010

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
NCARP_RAIZ = '.siiau'
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
        if not __existe_directorio(directorio):
            directorios_por_crear.append(directorio)
    return directorios_por_crear

    
def revisar_directorios():
    TECLAS
    directorios_por_crear = __comprobar_directorios(DCARP_USUARIOS, DCARP_CACHE)
    if directorios_por_crear.__len__() > 0:
        char_crear_carpetas = ' '
        incorrecto = False
        preguntar_de_nuevo = True
        imprimir(log('Es necesario crear una serie de carpetas...', TRAZO))
        pregunta = log('¿crear carpetas? (S/N)', TRAZO)
        while True:
            if incorrecto:
                char_rojo = error(char_crear_carpetas, mostrar_pre=False)
                imprimir(f'{LIMPIAR}{pregunta} {char_rojo}', nl=False)
            else:
                imprimir(f'{LIMPIAR}{pregunta} {char_crear_carpetas}', nl=False)
            if preguntar_de_nuevo:
                crear_carpetas, char_crear_carpetas = leer_tecla(retornar_original=True)
                if crear_carpetas in [TECLAS.tec_flecha_ar, TECLAS.tec_flecha_ab]:
                    crear_carpetas = ''
            else:
                preguntar_de_nuevo = True
            if crear_carpetas == TECLAS.com_ctrl_c:
                exit(imprimir('Hasta luego'))
            if char_crear_carpetas in ['N', 'n', 'S', 's']:
                if incorrecto:
                    incorrecto = False
                imprimir(f'{LIMPIAR}{pregunta} {char_crear_carpetas}', nl=False)
                aux = char_crear_carpetas
                enter, char_crear_carpetas = leer_tecla(retornar_original=True)
                if enter in [TECLAS.tec_flecha_ar, TECLAS.tec_flecha_ab]:
                    enter = ''
                if enter == TECLAS.tec_enter:
                    char_crear_carpetas = aux
                    if char_crear_carpetas in ['S', 's']:
                        crear = True
                        break
                    elif char_crear_carpetas in ['N', 'n']:
                        crear = False
                        break
                    else:
                        pass
                elif enter == TECLAS.com_ctrl_c:
                    exit(imprimir('Hasta luego'))
                else:
                    preguntar_de_nuevo = False
            else:
                incorrecto = True

        pregunta = log('¿Crear carpetas?', TRAZO)
        imprimir(LIMPIAR + ' ' * os.get_terminal_size()[0], nl=False)
        imprimir(LIMPIAR + pregunta + ' ' + sub_titulo(char_crear_carpetas))
        
        if crear:
            for directorio in directorios_por_crear:
                os.makedirs(directorio)
                imprimir(log(correcto(f'{directorio} creado'), TRAZO))
        else:
            msj_error = log(error('se requieren los directorios para funcionar'), TRAZO)
            exit(imprimir(msj_error))
    
        imprimir(log('presione ENTER para continuar', TRAZO))
        while True:
            tecla = leer_tecla()
            if tecla == TECLAS.tec_enter:
                break
            elif tecla == TECLAS.com_ctrl_c:
                exit(imprimir('Hasta luego'))
                
                
def _obtener_dato_secreto(mensaje: str) -> str:
    imprimir(f'{mensaje}: ', nl=False)
    tecleado = []
    num_tecla = None
    while num_tecla != TECLAS.tec_enter:
        num_tecla, tecla = leer_tecla(retornar_original=True)
        if num_tecla == TECLAS.tec_retroceso:
            tecleado.pop()
        elif num_tecla != TECLAS.tec_enter:
            tecleado.append(tecla)
    imprimir('')
        
    return ''.join(tecleado)


def _obtener_dato(mensaje: str) -> str:
    return input(f'{mensaje}: ')
         
                
def revisar_archivos_inicio() -> list:
    """
    Retorna::
    
        (sin_extension, arhivos_usuarios)
        
    El primero contiene solo los codigos de los usuarios registrados.
    
    El segundo el nombre de los archivos completos.
    """
    archivos_usuarios = os.listdir(DCARP_USUARIOS)
    sin_extension = map(lambda x: x.split('.')[0], archivos_usuarios)
    return list(sin_extension), archivos_usuarios
                
                
def leer_usuario(archivo_usuario: str) -> dict:
    datos_usuario = leer_archivo_dat(
        f'{DCARP_USUARIOS}{archivo_usuario}'
    )
    
    return datos_usuario


def __reemplazar_carrera_o_ciclo(carrera, ciclo) -> bool:
    return carrera is not None or ciclo is not None


def revisar_sesion(datos_usuario: dict, 
                   carrera_seleccion: str=None, 
                   ciclo_seleccion: str=None):
    usuario = datos_usuario['usuario']
    try:
        datos_sesion: DatosSesion = leer_archivo_dat(
            f'{DCARP_CACHE}_temp__{usuario}.dat'
        )['sesion']
        if __reemplazar_carrera_o_ciclo(carrera_seleccion, ciclo_seleccion):
            ciclo_reemplazo = datos_sesion.ciclo
            carrera_reemplazo = datos_sesion.carrera
            if ciclo_seleccion is not None:
                ciclo_reemplazo = ciclo_seleccion
            if carrera_seleccion is not None:
                carrera_reemplazo = carrera_seleccion
            datos_sesion = DatosSesion(
                cookies=datos_sesion.cookies,
                pidmp=datos_sesion.pidmp,
                ciclo=ciclo_reemplazo,
                carrera=carrera_reemplazo
            )
        sesion = obtener_sesion(sesion_guardada=datos_sesion)
    except FileNotFoundError:
        contra = datos_usuario['contra']
        carreras: Tuple[CarreraEstudiante] = datos_usuario['carreras']
        ciclo_mas_grande = 0
        ultima_carrera = ''
        for carrera in carreras:
            ciclo_a_revisar = carrera.ref_ciclo_final
            if ciclo_a_revisar > ciclo_mas_grande:
                ciclo_mas_grande = ciclo_a_revisar
                ultima_carrera = carrera.ref_carrera
        sesion = obtener_sesion(usuario, contra, ultima_carrera, ciclo_mas_grande)
        escribir_archivo_dat(
            f'{DCARP_CACHE}_temp__{usuario}.dat',
            sesion=sesion.sesion
        )
        if __reemplazar_carrera_o_ciclo(carrera_seleccion, ciclo_seleccion):
            return revisar_sesion(
                datos_usuario,
                carrera_seleccion,
                ciclo_seleccion
            )
        
    return sesion


def obtener_sesion(usuario='', clave='', carrera='', ciclo='', sesion_guardada=None):
    if sesion_guardada is not None:
        nuevo_inicio_siiau = Alumno(sesion=sesion_guardada)
    else:
        nuevo_inicio_siiau = Alumno(
            codigo=usuario, 
            clave=clave, 
            carrera=carrera, 
            ciclo=ciclo
        )
        
    return nuevo_inicio_siiau


def agregar_datos_de_inicio():
    usuario = _obtener_dato('Usuario (ID estudiante)')
    contra = _obtener_dato_secreto('Clave de SIIAU')
    sesion = obtener_sesion(usuario, contra)
    try:
        carreras = sesion.carreras()
        sesion_para_nombre = obtener_sesion(
            usuario=usuario, 
            clave=contra, 
            carrera=carreras[-1].ref_carrera,
        )
        datos_est = sesion_para_nombre.horario().datos_estudiante
        nombre_est = datos_est.nombre.title()
        escribir_archivo_dat(
            f'{DCARP_USUARIOS}{usuario}.dat',
            usuario=usuario,
            contra=contra,
            carreras=carreras,
            nombre=nombre_est
        )
    except (IndexError, ValueError):
        imprimir(log(error('Datos incorrectos'), TRAZO))
        exit()
        

def mostrar_estatus(arhivo_usuario: str, mostrar_todo):
    datos_usuario = leer_usuario(arhivo_usuario)
    if mostrar_todo:
        carreras = tuple(map(
            lambda carr: carr.ref_carrera, datos_usuario['carreras']
        ))
    else:
        carreras = [None]
    for carrera in carreras:
        sesion_revisada = revisar_sesion(
            datos_usuario=datos_usuario,
            carrera_seleccion=carrera
        )
        datos_horario: DatosHorarioSiiau = sesion_revisada.horario()
        tabla_datos = tabla_dos_columnas_valores(
            datos=datos_horario.datos_estudiante,
            estilo='grid_eheader'
        )
        imprimir(tabla_datos)
    
    
def mostrar_datos_de_sesion(archivo_usuario: str):
    datos_usuarios = leer_usuario(archivo_usuario)
    carreras = datos_usuarios['carreras']
    refs_carreras = ', '.join(map(lambda carr: carr.ref_carrera, carreras))
    imprimir(
        'Sesion iniciada como:'
        f'\n\tUsuario: {datos_usuarios["usuario"]}'
        f'\n\tNombre: {datos_usuarios["nombre"]}'
        f'\n\tCarreras: {refs_carreras}'
    )
    
    
def revisar_archivos(ver_directorios=True) -> dict:
    """
    Retorna::
    
        {'usuarios': list, 'archivos_usuarios': list}
    """
    if ver_directorios:
        revisar_directorios()
    usuarios, archivos_usuarios = revisar_archivos_inicio()
    return {'usuarios': usuarios, 'archivos_usuarios': archivos_usuarios}


def mostrar_horario(compacto: str, 
                    carrera: str, 
                    ciclo: str, 
                    archivos_usuarios: str):
    datos_usuario = leer_usuario(archivos_usuarios[0])
    sesion_revisada = revisar_sesion(
        datos_usuario=datos_usuario,
        carrera_seleccion=carrera,
        ciclo_seleccion=ciclo
    )
    datos_horario: DatosHorarioSiiau = sesion_revisada.horario()
    horario = datos_horario.horario
    if compacto:
        estructurado = estructurar_horario_por_clases(horario)
        compactado = compactar_horario_por_clases(estructurado)
        tabla = named_tuple_a_tabla(
            compactado, 
            por_columnas=True, 
            horario_compacto=True
        )
    else:
        tabla = named_tuple_a_tabla(horario, por_columnas=True)
    
    imprimir(tabla)




# +--------------------------------------------------------------------------+
# |                               Comandos                                   |
# +--------------------------------------------------------------------------+

@click.command()
@click.option(
    '--estatus',
    '-e',
    is_flag=True,
    default=False,
    help='Muestra el estatus de la ultima carrera.'
)
@click.option(
    '--mostrar-todo',
    '-t',
    is_flag=True,
    default=False,
    help='Mostrar estatus de todas las carreras.'
)
@click.option(
    '--mostrar-usuarios',
    '-mu',
    is_flag=True,
    default=False,
    help='Mostrar los usuarios registrados.'
)
@click.option(
    '--nuevo-usuario',
    '-nu',
    is_flag=True,
    default=False,
    help='Agregar un nuevo usuario.'
)
@click.option(
    '--sel-usuario',
    '-u',
    type=(int),
    help='Selecciona el usuario.'
)
@click.option(
    '--carrera',
    '-c',
    type=(str),
    help='Especifica la carrera a revisar.'
)
def estatus_siiau(estatus, 
                  mostrar_todo, 
                  mostrar_usuarios, 
                  nuevo_usuario, 
                  carrera, 
                  sel_usuario):
    """
    Muestra y modofica la informacion actual sobre la sesion de siiau.
    """
    datos_inicio = revisar_archivos()
    usuarios = datos_inicio['usuarios']
    archivos_usuarios = datos_inicio['archivos_usuarios']
    if len(usuarios) == 0:
        agregar_datos_de_inicio()
        datos_inicio = revisar_archivos()
        archivos_usuarios = datos_inicio['archivos_usuarios']
        if estatus or mostrar_todo:
            mostrar_estatus(archivos_usuarios[0], mostrar_todo)
        else:
            archivos_usuarios = datos_inicio['archivos_usuarios']
            mostrar_datos_de_sesion(archivos_usuarios[0])
    elif len(usuarios) == 1:
        if estatus or mostrar_todo:
            mostrar_estatus(archivos_usuarios[0], mostrar_todo)
        else:
            mostrar_datos_de_sesion(archivos_usuarios[0])
    else:
        pass
    
    
@click.command()
@click.option(
    '--compacto', 
    '-c',
    is_flag=True,
    default=False,
    help='Mostrar el horario en una tabla compacta que tiene horas por fila.'
)
@click.option(
    '--carrera',
    type=(str),
    help=(
        'Cambiar la carrera de la cual obtener el horario. Por defecto se obtiene '
        'la ultima carrera registrada del usuario activo.'
    )
)
@click.option(
    '--ciclo',
    type=(str),
    help=(
        'Cambiar el ciclo del cual obtener el horario. Por defecto se obtiene '
        'el ultimo ciclo de la ultima carrera registrada del usuario activo ' 
        'o la seleccionada.'
    )
)
def horario_siiau(compacto, carrera, ciclo):
    """
    Obten tu horario de siiau.
    """
    datos_inicio = revisar_archivos()
    usuarios = datos_inicio['usuarios']
    if len(usuarios) == 0:
        agregar_datos_de_inicio()
        datos_inicio = revisar_archivos()
        archivos_usuarios = datos_inicio['archivos_usuarios']
        mostrar_horario(compacto, carrera, ciclo, archivos_usuarios)
    elif len(usuarios) == 1:
        archivos_usuarios = datos_inicio['archivos_usuarios']
        mostrar_horario(compacto, carrera, ciclo, archivos_usuarios)
    else:
        pass