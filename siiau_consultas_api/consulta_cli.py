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
from .esquemas import Opcion

# TODO Agregar interfaz para uso en consola



def menu_principal():
    titulo_menu = 'MENU PRINCIPAL'
    opciones = [
    Opcion('Consultar oferta', str),
    Opcion('Consultar centros', str),
    Opcion('Consultar carreras (por centro)', str),
    Opcion('Consultar materias (por carrera)', str),
    Opcion('* Iniciar sesion', str),
    Opcion('Consultar mi horario actual', str),
    Opcion('Consultar mis carreras', str),
    Opcion('Registrar materias', str),
    ]
    menu_gen(opciones, titulo_menu)
    

if __name__ == '__main__':
    menu_principal()