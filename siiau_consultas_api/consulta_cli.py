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
    convertir_ciclo_a_entero,
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
SELECCION_USUARIO_DEFECTO = 0

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

DIR_PARAMETROS = f'{DCARP_RAIZ}parametros.json'
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


def _obtener_indice_usuario_seleccionado() -> int:
    parametros = leer_json(DIR_PARAMETROS)
    i_usuario_seleccionado = parametros['usuario_seleccionado']
    return i_usuario_seleccionado
         
                
def revisar_archivos_inicio() -> list:
    """
    Retorna::
    
        arhivos_usuario: list
        
    El nombre de los archivos de usuario.
    """
    archivos_usuarios = os.listdir(DCARP_USUARIOS)
    return archivos_usuarios
                
                
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
    except (IndexError, ValueError, KeyError):
        imprimir(log(error('No se pudo iniciar sesion. Revise los datos'), TRAZO))
        imprimir(log(error('ingresados o su conexion a internet.'), TRAZO))
        exit()
        

def mostrar_estatus(arhivo_usuario: str, mostrar_todo: bool, carrera_sel: str):
    datos_usuario = leer_usuario(arhivo_usuario)
    if mostrar_todo:
        carreras = tuple(map(
            lambda carr: carr.ref_carrera, datos_usuario['carreras']
        ))
    else:
        if carrera_sel is not None:
            carreras = [carrera_sel]
        else:
            carreras = [None]
    for carrera in carreras:
        try:
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
        except ValueError:
            imprimir(log(error('Carrera no encontrada.'), TRAZO))
            exit()
        
    
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
    

def revisar_archivo_parametros() -> None:
    try:
        leer_json(DIR_PARAMETROS)
    except FileNotFoundError:
        escribir_json(
            datos={
                'usuario_seleccionado': None,
            },
            dir_archivo=DIR_PARAMETROS
        )
    
    
def revisar_archivos():
    # El orden de estos dos importa
    revisar_directorios()
    revisar_archivo_parametros()


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
    try:
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
    except IndexError:
        imprimir(log(error('Horario no encontrado. Revise los datos.'), TRAZO))
        exit()
    
    imprimir(tabla)


def mostrar_usuarios_registrados(archivos_usuarios, i_usuario_sel):
    i_usuario_sel = _obtener_indice_usuario_seleccionado()
    usuarios_obtenidos = []
    encabezados = ['USUARIO', 'NOMBRE', 'ACTIVO']
    for i_usuario, archivo_usuario in enumerate(archivos_usuarios):
        datos_usuario = leer_usuario(archivo_usuario)
        if i_usuario_sel == i_usuario:
            usuario_sel = '<-----'
        else:
            usuario_sel = ''
        usuarios_obtenidos.append(
            [datos_usuario['usuario'], datos_usuario['nombre'], usuario_sel]
        )
    tabla = tabla_generica(
        datos=usuarios_obtenidos,
        encabezados=encabezados,
        estilo='simple_head',
        mostrar_indice=True,
        inicio_indice=1
    )

    imprimir(tabla)
    
    
def cambiar_seleccion_usuario(archivos_usuarios, i_usuario_sel):
    mostrar_usuarios_registrados(archivos_usuarios, i_usuario_sel)
    imprimir(f'\nSeleccione uno de los {len(archivos_usuarios)} usuarios.')
    nuevo_indice = 0
    while True:
        while True:
            nuevo_indice = _obtener_dato('Ingrese su numero')
            try:
                nuevo_indice = int(nuevo_indice) - 1
                if nuevo_indice < 0:
                    continue
            except ValueError:
                continue
            break
        try:
            archivos_usuarios[nuevo_indice]
        except IndexError:
            continue
        break
    parametros = leer_json(DIR_PARAMETROS)
    parametros['usuario_seleccionado'] = nuevo_indice
    escribir_json(parametros, DIR_PARAMETROS)
    

def evaluar_opciones_estatus_siiau(estatus,
                                   mostrar_todo,
                                   mostrar_usuarios,
                                   sel_usuario,
                                   carrera,
                                   archivos_usuarios):
    i_usuario_sel = _obtener_indice_usuario_seleccionado()
    archivo_usuario = archivos_usuarios[i_usuario_sel]
    if estatus or mostrar_todo:
        mostrar_estatus(archivo_usuario, mostrar_todo, carrera)
    elif mostrar_usuarios:
        mostrar_usuarios_registrados(archivos_usuarios, i_usuario_sel)
    elif sel_usuario:
        cambiar_seleccion_usuario(archivos_usuarios, i_usuario_sel)
    else:
        mostrar_datos_de_sesion(archivo_usuario)
        

def revisar_si_existe_usuario():
    parametros = leer_json(DIR_PARAMETROS)
    usuario_seleccionado = parametros['usuario_seleccionado']
    if usuario_seleccionado is None:
        imprimir(log(error('No hay usuario seleccionado.'), TRAZO))
        imprimir(log('Utilize "siiau -nu" para agregar un usuario.', TRAZO))
        exit()
        
        
def nuevo_usuario_siiau():
    agregar_datos_de_inicio()
    
    # Aqui se obtienen los parametros completos (en lugar de usar las
    # funciones para obtener sus valores) por si necesitan reescribir.
    parametros = leer_json(DIR_PARAMETROS)
    usuario_seleccionado = parametros['usuario_seleccionado']
    if usuario_seleccionado is None:
        parametros['usuario_seleccionado'] = SELECCION_USUARIO_DEFECTO
        escribir_json(parametros, DIR_PARAMETROS)



# +--------------------------------------------------------------------------+
# |                               Comandos                                   |
# +--------------------------------------------------------------------------+

@click.command()
@click.option(
    '--estatus',
    '-e',
    is_flag=True,
    default=False,
    help='Mostrar el estatus de la ultima carrera del usuario seleccionado.'
)
@click.option(
    '--mostrar-todo',
    '-t',
    is_flag=True,
    default=False,
    help='Mostrar estatus de todas las carreras del usuario seleccionado.'
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
    is_flag=True,
    default=False,
    help='Seleccionar el usuario activo.'
)
@click.option(
    '--carrera',
    '-c',
    type=(str),
    help='Especificar la carrera a revisar.'
)
def estatus_siiau(estatus, 
                  mostrar_todo, 
                  mostrar_usuarios, 
                  nuevo_usuario,
                  sel_usuario,
                  carrera):
    """
    Muestra y modofica la informacion actual sobre la sesion de siiau.
    """
    revisar_archivos()
    if not nuevo_usuario:
        revisar_si_existe_usuario()
    else:
        # Este es un caso especial y no se incluye en
        # "evaluar_opciones_estatus_siiau"
        nuevo_usuario_siiau()
    archivos_usuarios = revisar_archivos_inicio()
    evaluar_opciones_estatus_siiau(
        estatus,
        mostrar_todo,
        mostrar_usuarios,
        sel_usuario,
        carrera,
        archivos_usuarios,
    )
  
    
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
    if not isinstance(ciclo, int) and ciclo is not None:
        try:
            ciclo = convertir_ciclo_a_entero(ciclo)
        except (ValueError, TypeError):
            imprimir(log(error('Ciclo invalido.'), TRAZO))
            exit()
    revisar_archivos()
    revisar_si_existe_usuario()
    archivos_usuarios = revisar_archivos_inicio()
    mostrar_horario(compacto, carrera, ciclo, archivos_usuarios)

