from consulta_siiau_service import SesionSIIAU, ConsultaSIIAU
from typing import NamedTuple, Union, List
from os import get_terminal_size
from tabulate import  tabulate
from textwrap import wrap


def es_alguna_instancia(a_comprobar, *instancia_de):
    """
    Comprobar si el valor ingresado es instancia de cualquiera de los tipos
    solicitados, al menos uno de ellos.
    """
    es_instancia = False
    for comprobacion in instancia_de:
        es_instancia = es_instancia or isinstance(a_comprobar, comprobacion)

    return es_instancia


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
    elif subtabla:
        encabezados = tuple(map(lambda x: x.upper(), tupla._asdict().keys()))
        cuerpo = []
        for col in tupla:
            if isinstance(col, bool):
                col = 'si' if col else 'no'
            cuerpo.append(col)
        print(cuerpo)
        return tabulate(tabular_data=[cuerpo],
                        headers=encabezados,
                        tablefmt='plain',
                        numalign='left')


if __name__ == '__main__':
    # sesion = SesionSIIAU(usuario, contra).obtener()
    # pidm_p = sesion.pidmp
    # cookies = sesion.cookies
    # consulta = ConsultaSIIAU(ciclo=ciclo, cookies=cookies, carrera=carrera, pidm_p=pidm_p)
    # oferta = consulta.oferta(materia='I7024', centro='D')
    # centros = consulta.centros()
    # carreras = consulta.carreras(centros[0].id_centro)
    # materias = consulta.materias('INCO')
    # carreras_estudiante = consulta.carrera_s_estudiante()
    # horario_estudiante = consulta.horario()
    # print(named_tuple_a_tabla(centros))
    # print(named_tuple_a_tabla(carreras))
    # print(named_tuple_a_tabla(carreras_estudiante))
    # print(named_tuple_a_tabla(horario_estudiante.horario, por_columnas=True))

    # print(horario_estudiante)
    # print(oferta)
    # horario = consulta.horario()

    # print('='*150)
    # list(map(lambda x: print(dumps(x._asdict(), indent=4)), consulta.oferta(materia='I5377', centro='G')))
    pass


