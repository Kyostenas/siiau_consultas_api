from servicio_oferta_siiau import estructurar_oferta_como_horario
from servicio_horario_siiau import compactar_horario_por_clases
from servicio_tabla import named_tuple_a_tabla
from esquemas import ClaseOferta
from typing import Tuple

from itertools import product

from utiles import simplificar_lista

I_CONJUNTO = 0
I_INDICE_CLASE = 1


def __obtener_indices(conjuntos_clases: Tuple[Tuple[ClaseOferta]]):
    for i_conjunto, conjunto in enumerate(conjuntos_clases):
        yield ((i_conjunto, i_clase) for i_clase, _ in enumerate(conjunto))


def combinar_clases(conjuntos_clases: Tuple[Tuple[ClaseOferta]], evitar_solapadas=True):
    indices = __obtener_indices(conjuntos_clases)
    conjuntos_indices = tuple(map(tuple, indices))
    conjuntos_combinados = list(product(*conjuntos_indices))

    for combinacion in conjuntos_combinados:
        clases_combinacion = []
        for indicador_clase in combinacion:
            i_conjunto = indicador_clase[I_CONJUNTO]
            i_clase = indicador_clase[I_INDICE_CLASE]
            clases_combinacion.append(conjuntos_clases[i_conjunto][i_clase])
        estructurada, se_solapan, i_clases_solapadas = estructurar_oferta_como_horario(
            clases_combinacion
        )
        if evitar_solapadas:
            if se_solapan:
                pass
            else:
                yield estructurada
        else:
            if se_solapan:
                yield estructurada, se_solapan, i_clases_solapadas
            else:
                yield estructurada
    


if __name__ == '__main__':
    from servicio_consulta_siiau import oferta_academica
    from os import environ as env
    from dotenv import load_dotenv
    from utiles import limpiar_pantalla
    load_dotenv()
    usuario: str = env['USUARIO_Y']
    contra: str = env['CONTRA_Y']
    carrera: str = env['CARRERA_Y']
    ciclo: str = env['CICLO_ACTUAL_Y']
    MATERIAS_INCO=['I7024','I7023','I5886','I5887','I5896','I5897']

    conjuntos_oferta = tuple(map(lambda materia: oferta_academica('D', '202210', materia), MATERIAS_INCO))
    combinadas = combinar_clases(conjuntos_oferta)

    for x in combinadas:
        compacta = compactar_horario_por_clases(x)
        print(named_tuple_a_tabla(compacta, horario_compacto=True, por_columnas=True))
        input()
        limpiar_pantalla()


        

