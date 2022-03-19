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


from .cli import menu_generico_seleccion as menu_gen
from .cli import pantalla_agregado_centrada as pantalla_para_agregar
from .cli import titulo, sub_titulo, advertencia, error, correcto
from .esquemas import Opcion

# TODO Agregar interfaz para uso en consola


def __agregar_materias_para_consultar(transferencia):
    try:
        transferencia = transferencia['__agregar_materias_para_consultar']
    except KeyError:
        transferencia = []
    transferencia = pantalla_para_agregar(7, 15, 'agregar materias', 'clave', transferencia)
    return transferencia


def __menu_consultar_oferta():
    titulo_menu = 'consultar oferta'
    sub_titulo_menu = 'consulta y procesa la oferta academica'
    opciones = [
        Opcion('agregar materias para consultar', __agregar_materias_para_consultar),
        Opcion('agregar nrcs exclusivos', str),
        Opcion('ver materias agregadas', str),
        Opcion('ver clases', str),
        Opcion('generar posibles horarios', str),
    ]
    returno = menu_gen(opciones, False, titulo_menu, sub_titulo_menu)
    print(returno)
    exit()


def menu_principal():
    titulo_menu = 'menu principal'
    opciones = [
        Opcion('consultar oferta', __menu_consultar_oferta),
        Opcion('consultar centros', str),
        Opcion('consultar carreras (por centro)', str),
        Opcion('consultar materias (por carrera)', str),
        Opcion('* iniciar sesion', str),
        Opcion('consultar mi horario actual', str),
        Opcion('consultar mis carreras', str),
        Opcion('registrar materias', str),
    ]
    menu_gen(opciones, True, titulo_menu)


if __name__ == '__main__':
    menu_principal()