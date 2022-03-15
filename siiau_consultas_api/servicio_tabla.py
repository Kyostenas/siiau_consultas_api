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


from .utiles import es_alguna_instancia

from textwrap import wrap
from tabulate import  tabulate
from typing import NamedTuple, Union, List
from os import get_terminal_size

MAX_TAM_FILA = 15

# TODO mejorar para que pueda recibir tam desado de columnas
# TODO separar named_tuple_a_tabla en funciones mas legibles
# TODO agregar calculo personalizable del tam de las filas

# FIX para horario compacto requiere que "por_columnas" y "horario_compacto" sean verdaderas 
# FIX tabla de oferta no se forma con ofertas muy grandes, pudiendo ser materias en especifico
# Traceback (most recent call last):
#   File "horario_siiau_service.py", line 355, in <module>
#     oferta_tabla = named_tuple_a_tabla(tupla=oferta, por_columnas=True)
#   File "/home/mentalselfthink/siiau_consultas_workspace/siiau_consultas_api/tabla_service.py", line 55, in named_tuple_a_tabla
#     n_sub_tabla = named_tuple_a_tabla(col, subtabla=True, tam_col= 10)
#   File "/home/mentalselfthink/siiau_consultas_workspace/siiau_consultas_api/tabla_service.py", line 48, in named_tuple_a_tabla
#     encabezados = tuple(map(lambda x: ' '.join(x.upper().split('_')), tupla[0]._asdict().keys()))
# IndexError: tuple index out of range



def named_tuple_a_tabla(tupla: Union[NamedTuple, List[NamedTuple]],
                        subtabla=False,
                        tam_col=0,
                        por_columnas=False,
                        horario_compacto=False):
    tam_terminal = get_terminal_size().columns
    tam_max_tabla = tam_terminal if not subtabla else tam_col
    tupla_es_named_tuple = hasattr(tupla, '_asdict')
    if por_columnas and tupla_es_named_tuple:
        encabezados = tuple(map(lambda x: ' '.join(x.upper().split('_')), tupla._asdict().keys()))
        columnas_a_filas = list(zip(*tupla))
        cuerpo = []
        for fila in columnas_a_filas:

            # Cortar filas a un maximo tam.
            if horario_compacto:
                nueva_fila = list()
                for x in fila:
                    if '\\' in x:
                        partes = x.split('\\')
                        formar_sub_tabla_informativa = False
                        cuerpo_sub_tabla_informativa = []
                        indice_para_insertar = 0
                        for i_parte, parte in enumerate(partes):
                            if '>' in parte:
                                parte = parte.replace('>', '')
                                if not formar_sub_tabla_informativa:
                                    formar_sub_tabla_informativa = True
                                if indice_para_insertar == 0:
                                    indice_para_insertar = i_parte
                                partes_de_la_parte = parte.split('%')
                                cuerpo_sub_tabla_informativa.append(partes_de_la_parte)
                            if len(parte) > MAX_TAM_FILA:
                                partes[i_parte] = '\n'.join(wrap(parte, MAX_TAM_FILA))
                        if formar_sub_tabla_informativa:
                            i_parte = 0
                            while i_parte < len(partes) + 1:
                                try:
                                    if '>' in partes[i_parte]:
                                        partes.pop(i_parte)
                                        i_parte = 0
                                    else:
                                        i_parte += 1
                                except IndexError:
                                    i_parte += 1
                            subtabla_informativa = tabulate(tabular_data=cuerpo_sub_tabla_informativa,
                                                            tablefmt='presto')
                            partes.append(subtabla_informativa)
                        nuevo_elemento = '\n'.join(partes)
                    else:
                        nuevo_elemento = '\n'.join(wrap(x, MAX_TAM_FILA))
                    nueva_fila.append(nuevo_elemento)
                nueva_fila = tuple(nueva_fila)
            else:
                nueva_fila = []
                for col in fila:
                    if isinstance(col, bool):
                        col = 'si' if col else ''
                    if '\\' in col:
                        col = col.replace('\\', '\n')
                    else:
                        col = '\n'.join([*wrap(col, MAX_TAM_FILA)])
                    nueva_fila.append(col)
                nueva_fila = tuple(nueva_fila)
            cuerpo.append(nueva_fila)
        return tabulate(headers=encabezados,
                        tabular_data=cuerpo,
                        tablefmt='grid',
                        numalign='left')
    elif es_alguna_instancia(tupla, tuple, list) and not tupla_es_named_tuple:
        encabezados = tuple(map(lambda x: ' '.join(x.upper().split('_')), tupla[0]._asdict().keys()))
        cuerpo = []
        for fila in tupla:
            nueva_fila = []
            for col in [*fila]:
                col_es_named_tuple = hasattr(tupla, '_asdict')
                if es_alguna_instancia(col, tuple, list) or col_es_named_tuple:
                    n_sub_tabla = named_tuple_a_tabla(col, subtabla=True, tam_col= 10)
                    nueva_fila.append(n_sub_tabla)
                else:
                    if isinstance(col, bool):
                        col = 'si' if col else ''
                    nueva_fila.append('\n'.join([*wrap(str(col), 15)]))
            cuerpo.append(nueva_fila)
        formato = 'grid' if not subtabla else 'simple'
        return tabulate(tabular_data=cuerpo,
                        headers=encabezados,
                        tablefmt=formato,
                        numalign='left')
    elif subtabla and tupla_es_named_tuple:
        encabezados = tuple(map(lambda x: x.upper(), tupla._asdict().keys()))
        cuerpo = []
        for col in tupla:
            if isinstance(col, bool):
                col = 'si' if col else ''
            cuerpo.append(col)
        return tabulate(tabular_data=[cuerpo],
                        headers=encabezados,
                        tablefmt='plain',
                        numalign='left')


if __name__ == '__main__':
    print('Esto no se debería mostrar...')


