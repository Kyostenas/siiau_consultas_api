from typing import NamedTuple, Union, List
from utiles import es_alguna_instancia
from os import get_terminal_size
from tabulate import  tabulate
from textwrap import wrap


def named_tuple_a_tabla(tupla: Union[NamedTuple, List[NamedTuple]],
                        subtabla=False,
                        tam_col=0,
                        por_columnas=False):
    tam_terminal = get_terminal_size().columns
    tam_max_tabla = tam_terminal if not subtabla else tam_col
    tupla_es_named_tuple = hasattr(tupla, '_asdict')
    if por_columnas and tupla_es_named_tuple:
        encabezados = tuple(map(lambda x: ' '.join(x.upper().split('_')), tupla._asdict().keys()))
        columnas_a_filas = list(zip(*tupla))
        cuerpo = []
        for fila in columnas_a_filas:
            nueva_fila = tuple(map(lambda x: '\n'.join([*wrap(str(x), 15)]), fila))
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
                        col = 'si' if col else 'no'
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
                col = 'si' if col else 'no'
            cuerpo.append(col)
        return tabulate(tabular_data=[cuerpo],
                        headers=encabezados,
                        tablefmt='plain',
                        numalign='left')


if __name__ == '__main__':
    print('Esto no se debería mostrar...')


