""" 
Funciones o Clases con usos variados de uso puntual o repetitivo.

Por lo general, son necesidades tan simples, que no vale
la pena instalar una libreria o hacer un script sólo 
para suplirla.
"""

import re, io, json, xlwt, os
from xlwt import Workbook
import datetime

VALORES_CICLOS = {
    'A': '10',
    'B': '20'
}


def convertir_ciclo_a_entero(ciclo: str):
    """
    Convierte el ciclo a entero considerando las posibles letras
    que contenga como minusculas y conviertiendolas a su valor entero.

    202010 -> 202010
    2020B -> '202010'
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


def aplanar_lista(tf, i=0, c=0):
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


def particionar(lista, tam_rebanada, relleno=None, retornar_tuplas=True):
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


def particion_arbitraria(lista, *partes, join_string=False):
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


def escribir_txt(texto, dirArchivo):
    with io.open(dirArchivo, 'a', encoding='utf-8') as arcTexto:
        arcTexto.write(texto)
    arcTexto.close()


def escribir_json(datos, dir_archivo):
    directorio_activo = os.getcwd()
    dir_archivo = f'{os.sep}'.join([directorio_activo, dir_archivo])
    with open(dir_archivo, 'w', encoding='utf-8') as arcJson:
        json.dump(datos, arcJson, ensure_ascii=False, indent=2)
    arcJson.close()


def escribir_excel(dir_archivo, *celsNegritas, **tablas):
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


def mk_dir_en_dir_actual(*dirCarpeta):
    directorio_activo = os.getcwd()
    nueva_carpeta = f'{os.sep}'.join([directorio_activo] + list(dirCarpeta))
    try:
        os.makedirs(nueva_carpeta)
    except:
        pass


def cadena_fecha_larga(incluirHora=True, separadorFecha='', separadorHora=''):
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