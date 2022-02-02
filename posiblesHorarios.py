from typing import NamedTuple
from tabulate import tabulate
import itertools
import os


class TablasHorario(NamedTuple):
    horario: list
    descripcionesMateria: list


def _hacer_tabla(horario: dict):
    # Desde (1, 1) hasta (15, 6)
    horario_tabla = [['HORA', 'L', 'M', 'I', 'J', 'V', 'S'],
                     ['07:00 am\n07:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['08:00 am\n08:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['09:00 am\n09:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['10:00 am\n10:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['11:00 am\n11:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['12:00 am\n12:55 am', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['01:00 pm\n01:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['02:00 pm\n02:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['03:00 pm\n03:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['04:00 pm\n04:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['05:00 pm\n05:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['06:00 pm\n06:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['07:00 pm\n07:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['08:00 pm\n08:55 pm', ' ', ' ', ' ', ' ', ' ', ' '],
                     ['09:00 pm\n09:55 pm', ' ', ' ', ' ', ' ', ' ', ' ']]

    descripciones = [('NRC', 'CLAVE', 'MATERIA', 'PROFESOR/ES')]

    # print(horario_siiau)

    for nrc, valores in horario.items():
        for rango in valores['rango_por_dia']:
            y = rango[0] + 1
            x = rango[1] + 1
            if horario_tabla[y][x] != '':
                return None
            horario_tabla[y][x] = nrc
        profes = [profe['nombre'] for profe in valores['profesores']]
        descripciones.append(
            [
                nrc,
                valores['clave'],
                valores['nombre'],
                '\n'.join(profes)
            ]
        )

    os.system('clear')
    print(tabulate(horario_tabla, 'firstrow', 'grid'))
    print(tabulate(descripciones, 'firstrow', 'plain'))
    input()

    return TablasHorario(horario_tabla, descripciones)


def combinar_nrcs(nrcs: dict, materias: dict, selProfs: dict):
    posibles_horarios = {}
    nrcs_preparados = [[(clave, nrc_simSim) for nrc_simSim in arreglo]
                       for clave, arreglo in nrcs.items()]

    nrcs_combinados = itertools.product(*nrcs_preparados)

    i = 1
    for horario in nrcs_combinados:
        correcto = True
        for cve, nrc in horario:
            for profe in materias[cve][nrc]['profesores']:
                if profe['nombre'] not in selProfs[cve]:
                    correcto = False
                    break
            if correcto is False:
                break

        if correcto:
            posible_formado = {
                'nrcs': [nrc for cve, nrc in horario],
                'materias': {
                    nrc: {
                        'clave': materias[cve][nrc]['clave'],
                        'nrc': materias[cve][nrc]['nrc'],
                        'seccion': materias[cve][nrc]['seccion'],
                        'nombre': materias[cve][nrc]['nombre'],
                        'profesores': materias[cve][nrc]['profesores'],
                        'rango_por_dia': materias[cve][nrc]['rango_por_dia'],
                    } for cve, nrc in horario
                },
            }
            tablas = _hacer_tabla(posible_formado['materias'])
            if tablas is not None:
                posible_formado['tabla_horario'] = tablas.horario
                posible_formado['tabla_descripciones'] = tablas.descripcionesMateria
                posibles_horarios[f'horario_{i}'] = posible_formado
                i = i + 1

    return posibles_horarios