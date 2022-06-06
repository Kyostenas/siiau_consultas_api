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


""" 
Funciones o Clases con usos variados de uso puntual o repetitivo.

Por lo general, son necesidades tan simples, que no vale
la pena instalar una libreria o hacer un script sólo 
para suplirla.
"""

from typing import NamedTuple, Tuple
import re, io, json, xlwt, os
from xlwt import Workbook
from click import echo
import datetime
import pickle
import click

from .getch import getch


VALORES_CICLOS = {
    'A': '10',
    'B': '20'
}

# Busca las secuencias de color ANSI que se ven como:
#   \x1b[47m
# Estas son las que maneja colorama, utilizado en el cli.
ELIMINADOR_ANSI = re.compile(r'\x1b\[[\d]*m')

ESC_CODE = '\x1b'


def convertir_ciclo_a_entero(ciclo: str) -> int:
    """
    Convierte el ciclo a entero considerando las posibles letras
    que contenga como minusculas y conviertiendolas a su valor entero::

        '202010' -> '202010'
        '2020B' -> '202010'
    """
    quitar_letras = re.compile('[^\d]')
    quitar_numeros = re.compile('[\d]')
    entero = re.sub(pattern=quitar_letras, repl='', string=ciclo)
    letra = re.sub(pattern=quitar_numeros, repl='', string=ciclo)
    if letra != '':
        if letra in VALORES_CICLOS.keys():
            letra = VALORES_CICLOS[letra]
        else:
            letra = str(ord(letra))
    return int(''.join([entero, letra]))


def aplanar_lista(tf, i=0, c=0) -> list:
    c += 1
    if i < len(tf):
        if isinstance(tf[i], list):
            temp = tf.pop(i)
            for x in range(len(temp)):
                tf.insert(i + x, temp[x])
            return aplanar_lista(tf, i, c)
        else:
            return aplanar_lista(tf, i + 1, c)
    else:
        return tf
    

def particionar(lista, tam_rebanada, relleno=None, retornar_tuplas=True) -> list:
    """
    Particionar una lista en rebanadas del largo deseado.
    """
    lista = list(lista)
    desordenado = [lista[i::tam_rebanada] for i in range(tam_rebanada)]
    arreglado = [x + [relleno for _ in range(len(desordenado[0]) - len(x))]
                 for x in desordenado]
    if retornar_tuplas:
        tuplas = list(zip(*arreglado))
        return tuplas
    else:
        listas = list(map(list, zip(*arreglado)))
        return listas


def particion_arbitraria(lista, *partes, join_string=False) -> list:
    """ 
    Particionar una lista, pero indicar el tamaño de cada
    particion manualmente.
    """
    # print(partes)
    lista = list(lista)
    anterior = 0
    particiones = []
    for derecha in partes:
        rebanada = slice(anterior, anterior + derecha)
        anterior = anterior + derecha
        if join_string:
            particiones.append(
                ''.join(lista[rebanada])
            )
        else:
            particiones.append(lista[rebanada])

    return particiones


def limpiar_html(html):
    limpiador = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return re.sub(limpiador, '', str(html))


def escribir_txt(texto, dirArchivo) -> None:
    with io.open(dirArchivo, 'a', encoding='utf-8') as arcTexto:
        arcTexto.write(texto)
    arcTexto.close()


def escribir_json(datos, dir_archivo) -> None:
    # directorio_activo = os.getcwd()
    # dir_archivo = f'{os.sep}'.join([directorio_activo, dir_archivo])
    with open(dir_archivo, 'w', encoding='utf-8') as archivo_json:
        json.dump(datos, archivo_json, ensure_ascii=False, indent=4)
    archivo_json.close()
    

def escribir_archivo_dat(dir_archivo, **datos) -> None:
    """
    Escribir archivo de datos en formato .dat
    """
    with open(dir_archivo, 'wb') as archivo_dat:
        archivo_dat.write(pickle.dumps(datos))
    archivo_dat.close()


def leer_archivo_dat(dir_archivo) -> dict:
    """
    Leer archivo de datos en formato .dat
    """
    with open(dir_archivo, 'rb') as archivo_dat:
        datos = pickle.loads(archivo_dat.read())
    archivo_dat.close()
    return datos


def leer_json(dir_archivo) -> dict:
    with open(dir_archivo, 'r', encoding='utf-8') as archivo_json:
        datos = json.load(archivo_json)
    archivo_json.close()
    return datos


# basado en https://stackoverflow.com/a/21035861/13132076
def modificar_json(dir_archivo, valores_modificados: dict) -> None:
    with open(dir_archivo, 'r+', encoding='utf-8') as archivo_json:
        datos = json.load(archivo_json)
        for llave, valor in valores_modificados:
            datos[llave] = valor
        archivo_json.seek(0)
        json.dump(datos, archivo_json, ensure_ascii=False, indent=4)
        archivo_json.truncate()
        
    archivo_json.close()


def escribir_excel(dir_archivo, *celsNegritas, **tablas) -> None:
    wb = Workbook()
    negrita = xlwt.easyxf('font: bold 1')
    directorio_activo = os.getcwd()
    dir_archivo = f'{os.sep}'.join([directorio_activo, dir_archivo])

    for nombre, datos in tablas.items():
        hoja = wb.add_sheet(sheetname=f'{nombre.upper()}')
        for linea in range(len(datos)):
            for columna in range(len(datos[linea])):
                if (linea, columna) in celsNegritas:
                    hoja.write(linea, columna, datos[linea][columna], negrita)
                else:
                    hoja.write(linea, columna, datos[linea][columna])

    wb.save(f'{dir_archivo}')


def mk_dir_en_dir_actual(*dirCarpeta) -> None:
    directorio_activo = os.getcwd()
    nueva_carpeta = f'{os.sep}'.join([directorio_activo] + list(dirCarpeta))
    try:
        os.makedirs(nueva_carpeta)
    except:
        pass


def cadena_fecha_larga(incluirHora=True, separadorFecha='', separadorHora='') -> str:
    def evaluar(num):
        extra = ''
        if num < 10:
            extra = '0'

        return ''.join([extra, str(num)])

    fecha = datetime.datetime.now()
    dia = evaluar(fecha.day)
    mes = evaluar(fecha.month)
    year = evaluar(fecha.year)
    hora = evaluar(fecha.hour)
    minuto = evaluar(fecha.minute)
    segundo = evaluar(fecha.second)
    microsegundo = evaluar(fecha.microsecond)

    fecha_completa = f'{separadorFecha}'.join([dia, mes, year])
    if incluirHora:
        hora_completa = f'{separadorHora}'.join([hora, minuto, segundo, microsegundo])
        string_terminada = '_'.join([fecha_completa, hora_completa])
        return string_terminada
    else:
        return fecha_completa


def es_alguna_instancia(a_comprobar, *instancia_de) -> bool:
    """
    Comprobar si el valor ingresado es instancia de cualquiera de los tipos
    solicitados, al menos uno de ellos.
    """
    es_instancia = False
    for comprobacion in instancia_de:
        es_instancia = es_instancia or isinstance(a_comprobar, comprobacion)

    return es_instancia


def simplificar_lista(lista: list) -> list:
    """
    Revisa una lista y elimina todos los elementos repetidos en ella.
    Retorna la lista revisada.
    """
    revisada = []
    [revisada.append(elemento) for elemento in lista if elemento not in revisada]

    return revisada


def limpiar_pantalla() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def regresar_cursor_inicio_pantalla() -> None:
    print('\x1b[H')


def print_actualizable(*cadenas, sep=' ') -> None:
    """
    Puede seguir imprimiendo en la misma linea sin borrar lo
    anterior. Da el efecto de que se actualiza la linea.
    """
    print(*cadenas, sep=sep, end='\r', flush=True)


def limpiar_secuencias_ANSI(cadena, reemplazo=''):
    """
    Limpia todas las secuencias ANSI de una cadena de texto.
    """
    return ELIMINADOR_ANSI.sub(reemplazo, cadena)
    #          ^                ^            ^     
    # Buscador de               |            |
    # coincidencias             |            | 
    #                           |            |     
    # La cadena que reemplaza --+            |
    # las coincidencias                      |
    #                                        |
    # La cadena que sera limpiada -----------+


def tam_consola() -> dict:
    """
    retorna::
        
        {'cols': int, 'filas': int}
    """
    cols_terminal, filas_terminal = os.get_terminal_size()
    return {'cols': cols_terminal, 'filas': filas_terminal}


def barra_progreso(total, progreso, imprimir=False, mensaje='cargando'):
    tam_barra= 30
    progreso_mostrar = progreso
    total_mostrar = total
    if progreso < 0:
        progreso = 0
    if progreso > total:
        progreso = total
    cuanto_relleno = (progreso * tam_barra) // total
    cuanto_vacio = tam_barra - cuanto_relleno
    barra_char = ''.join([f'{"/"*cuanto_relleno}', f'{" "*cuanto_vacio}'])
    barra_prog = ''.join([mensaje, ' [', barra_char, '] ', str(progreso), '|', str(total)])
    if imprimir:
        print_actualizable(barra_prog)
    else:
        return barra_prog
    

def convertir_a_dict_recursivamente(objeto):
    """
    Convierte un objeto en un diccionario, recursivamente.
    """
    if isinstance(objeto, dict):
        return {k: convertir_a_dict_recursivamente(v) for k, v in objeto.items()}
    if isinstance(objeto, list):
        return [convertir_a_dict_recursivamente(v) for v in objeto]
    if isinstance(objeto, tuple):
        # Si es tupla, probablemente es "NamedTuple"
        try:
            return objeto._asdict()
        except AttributeError:
            return tuple([convertir_a_dict_recursivamente(v) for v in objeto])
    else:
        return objeto
    
    
def __limpar_cli():
    limpiar_pantalla()
    regresar_cursor_inicio_pantalla()
    
 
def __soobreescribir_cli():
    cols_consola, filas_consola = tam_consola()
    barra_vacia = ' ' * (cols_consola - 1)
    cuadro_vacio = '\n'.join([barra_vacia for _ in range(filas_consola - 1)])
    print(cuadro_vacio)


def leer_tecla(retornar_original = False):
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
        

def imprimir(texto, nl=True, **kwargs):
    """
    Imprime un mensaje en la consola.
    """
    click.echo(message=texto, nl=nl, **kwargs)

    