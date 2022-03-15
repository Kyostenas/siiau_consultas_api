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


from .servicio_oferta_siiau import estructurar_oferta_como_horario
from .servicio_horario_siiau import compactar_horario_por_clases
from .servicio_tabla import named_tuple_a_tabla
from .esquemas import ClaseOferta
from .utiles import simplificar_lista

from typing import Tuple
from itertools import product


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
                yield estructurada, se_solapan, i_clases_solapadas
        else:
            if se_solapan:
                yield estructurada, se_solapan, i_clases_solapadas
            else:
                yield estructurada, se_solapan, i_clases_solapadas
    


if __name__ == '__main__':
    print('Ejecutando desde posibles_horarios. Esto no se deberia ver.')



        

