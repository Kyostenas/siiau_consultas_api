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


from colorama import Style, Back, Fore, init
init()  # Para que colorama funcione en Windows


def advertencia(texto: str, msj: str = 'ADVE'):
    pre = f'{Style.BRIGHT}{Back.YELLOW}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.YELLOW}{texto}{Style.RESET_ALL}'


def error(texto: str, msj: str = ' ERR', mostrar_pre = True):
    if mostrar_pre:
        pre = f'{Style.BRIGHT}{Back.RED}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL} '
    else:
        pre = ''
    return f'{pre}{Style.BRIGHT}{Fore.RED}{texto}{Style.RESET_ALL}'


def correcto(texto: str, msj: str = '  OK'):
    pre = f'{Style.BRIGHT}{Back.GREEN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.GREEN}{texto}{Style.RESET_ALL}'


def ayuda(texto: str, msj: str = 'AYUD'):
    pre = f'{Style.DIM}{Back.CYAN}{Style.NORMAL}{Fore.BLACK}{msj}{Style.RESET_ALL}'
    return f'{pre} {Style.BRIGHT}{Fore.CYAN}{texto}{Style.RESET_ALL}'


def seleccion(texto: str, cursor: str):
    seleccionado = f'{Style.BRIGHT}{Back.WHITE}{Fore.BLACK}{texto}{Style.RESET_ALL}'
    return f'{seleccionado}', 


# def seleccion_modificable(texto: str, cursor: str):
#     caret = f'{Style.BRIGHT}{Fore.CYAN}{CARET}{Style.RESET_ALL}'
#     seleccionado = (
#         f'{Style.BRIGHT}{Back.WHITE}{Fore.BLACK}{texto}{Style.RESET_ALL}{caret}'
#     )
#     return f'{seleccionado}'


def titulo(texto: str, margen: int = 1):
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.CYAN}{" "*margen}{texto.upper()}{" "*margen}{Style.RESET_ALL}'


def negativo(texto: str, margen: int = 1):
    return f'{Style.BRIGHT}{Fore.WHITE}{Back.BLACK}{" "*margen}{texto}{" "*margen}{Style.RESET_ALL}'

    
def definicion(concepto: str, definicion: str, margen: int = 1):
    concepto_marcado = f'{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA}{" "*margen}{concepto}{" "*margen}{Style.RESET_ALL}'
    concepto_y_definicion = f'{concepto_marcado} {definicion}'
    return concepto_y_definicion


def sub_titulo(texto: str):
    return f'{Style.BRIGHT}{Fore.CYAN}{texto}{Style.RESET_ALL}'


def log(texto: str, trazo: str, margen: int = 1):
    espacio = ' ' * margen
    pre = f'{Fore.WHITE}[{espacio}{trazo}{espacio}]{Style.RESET_ALL}'
    texto = comentario(texto)
    return f'{pre} {texto}'


def log2(texto: str, trazo: str, margen: int = 1):
    espacio = ' ' * margen
    pre = f'{Back.BLACK}{Style.BRIGHT}{Fore.BLUE}{espacio}{trazo}{espacio}{Style.RESET_ALL}'
    texto = comentario(texto)
    return f'{pre} {texto}'


def comentario(texto: str):
    return f'{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{texto}{Style.RESET_ALL}'


if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando desde cli.py')
