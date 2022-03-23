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


from typing import Any, NamedTuple, Tuple, Union


class DatosSesion(NamedTuple):
    cookies: str
    pidmp: int
    ciclo: str
    carrera: str


class ClaseCompleta(NamedTuple):
    titulo: str
    area: str
    clave: str
    creditos: int
    creditos_teoria: int
    creditos_practica: int
    tipo_materia: str
    nivel: str
    extraordinario: str
    ciclo_inicio: str
    ciclo_fin: str
    estatus: str
    prerrequisitos: str
    correquisitos: str
    departamenos: str
    carreras: str
    centros_universitarios: str


class ProfesorOferta(NamedTuple):
    sesion: str
    nombre: str


class DiasHorarioOferta(NamedTuple):
    L: bool
    M: bool
    I: bool
    J: bool
    V: bool
    S: bool

class HorarioOferta(NamedTuple):
    sesion: str
    hora: str
    dias: DiasHorarioOferta
    edif: str
    aula: str
    periodo: Tuple[str]


class ClaseOferta(NamedTuple):
    nrc: str
    clave: str
    materia: str
    seccion: str
    creditos: int
    cupos: int
    disponibles: int
    profesores: Tuple[ProfesorOferta]
    horarios: Tuple[HorarioOferta]


class CarreraCompleta(NamedTuple):
    ref_carrera: str
    nombre_completo: str


class CentroCompleto(NamedTuple):
    id_centro: str
    nombre_completo: str


class CicloCompleto(NamedTuple):
    ref_ciclo: str  # el nombre que maneja siiau (2019 B -> 201920)
    nombre_completo: str  # 2022 A -> "Calendario 22 A"


class HorarioCompletoSiiau(NamedTuple):
    nrc: Tuple[str]
    clave: Tuple[str]
    nombre_materia: Tuple[str]
    seccion: Tuple[str]
    creditos: Tuple[int]
    horario: Tuple[str]
    L: Tuple[bool]
    M: Tuple[bool]
    I: Tuple[bool]
    J: Tuple[bool]
    V: Tuple[bool]
    S: Tuple[bool]
    edificio: Tuple[str]
    aula: Tuple[str]
    profesor: Tuple[str]
    fecha_inicio: Tuple[str]
    fecha_fin: Tuple[str]


class DatosHorarioSiiau(NamedTuple):
    datos_estudiante: NamedTuple
    horario: HorarioCompletoSiiau


class CarreraEstudiante(NamedTuple):
    ref_carrera: str
    ciclo_inicio: str
    ref_ciclo: int


class DiaClase(NamedTuple):
    hora_inicio: str
    hora_final: str
    hora_inicio_completa: str
    hora_final_completa: str
    profesor: str
    edificio: str
    aula: str
    rango_horas: tuple
    rango_horas_hhmm: tuple


class Clase(NamedTuple):
    nrc: str
    clave_materia: str
    nombre: str
    seccion: str
    creditos: int
    dia_lu: Union[DiaClase, None]
    dia_ma: Union[DiaClase, None]
    dia_mi: Union[DiaClase, None]
    dia_ju: Union[DiaClase, None]
    dia_vi: Union[DiaClase, None]
    dia_sa: Union[DiaClase, None]
    fecha_inicio: str
    fecha_final: str
    fecha_inicio_completa: str
    fecha_final_completa: str
    # referencia_horario_tabla: dict


class HorarioCompacto(NamedTuple):
    horas: list
    lunes: list
    martes: list
    miercoles: list
    jueves: list
    viernes: list
    sabado: list


# TODO revisar diferencias de codigos en Windows, Linux y Otros 
class Teclas(NamedTuple):
    tec_1: int = 49
    tec_2: int = 50
    tec_3: int = 51
    tec_4: int = 52
    tec_5: int = 53
    tec_6: int = 54
    tec_7: int = 55
    tec_8: int = 56
    tec_9: int = 57
    tec_0: int = 48
    tec_a: int = 97
    tec_b: int = 98
    tec_c: int = 99
    tec_d: int = 100
    tec_e: int = 101
    tec_f: int = 102
    tec_g: int = 103
    tec_h: int = 104
    tec_i: int = 105
    tec_j: int = 106
    tec_k: int = 107
    tec_l: int = 108
    tec_m: int = 109
    tec_n: int = 110
    tec_o: int = 111
    tec_p: int = 112
    tec_q: int = 113
    tec_r: int = 114
    tec_s: int = 115
    tec_t: int = 116
    tec_u: int = 117
    tec_v: int = 118
    tec_w: int = 119
    tec_x: int = 120
    tec_y: int = 121
    tec_z: int = 122
    tec_A: int = 65
    tec_B: int = 66
    tec_C: int = 67
    tec_D: int = 68
    tec_E: int = 69
    tec_F: int = 70
    tec_G: int = 71
    tec_H: int = 72
    tec_I: int = 73
    tec_J: int = 74
    tec_K: int = 75
    tec_L: int = 76
    tec_M: int = 77
    tec_N: int = 78
    tec_O: int = 79
    tec_P: int = 80
    tec_Q: int = 81
    tec_R: int = 82
    tec_S: int = 83
    tec_T: int = 84
    tec_U: int = 85
    tec_V: int = 86
    tec_W: int = 87
    tec_X: int = 88
    tec_Y: int = 89
    tec_Z: int = 90
    tec_enter : int = 13
    tec_escape : int = 27
    tec_retroceso: int = 127
    tec_flecha_ar : int = 183
    tec_flecha_ab: int = 184
    tec_flecha_iz : int = 186
    tec_flecha_de : int = 185
    tec_espacio: int = 32
    com_ctrl_a: int = 1
    com_ctrl_b: int = 2
    com_ctrl_c: int = 3
    com_ctrl_d: int = 4
    com_ctrl_e: int = 5
    com_ctrl_f: int = 6
    com_ctrl_g: int = 7
    com_ctrl_h: int = 8
    com_ctrl_i: int = 9
    com_ctrl_j: int = 10
    com_ctrl_k: int = 11
    com_ctrl_l: int = 12
    com_ctrl_m: int = 13
    com_ctrl_n: int = 14
    com_ctrl_o: int = 15
    com_ctrl_p: int = 16
    com_ctrl_q: int = 17
    com_ctrl_r: int = 18
    com_ctrl_s: int = 19
    com_ctrl_t: int = 20
    com_ctrl_u: int = 21
    com_ctrl_v: int = 22
    com_ctrl_w: int = 23
    com_ctrl_x: int = 24
    com_ctrl_y: int = 25
    com_ctrl_z: int = 26

tc_ = Teclas()
LETRAS = tc_[10:62]
NUMEROS = tc_[0:10]


LETRAS_DIC = {
    97: "a",
    98: "b",
    99: "c",
    100: "d",
    101: "e",
    102: "f",
    103: "g",
    104: "h",
    105: "i",
    106: "j",
    107: "k",
    108: "l",
    109: "m",
    110: "n",
    111: "o",
    112: "p",
    113: "q",
    114: "r",
    115: "s",
    116: "t",
    117: "u",
    118: "v",
    119: "w",
    120: "x",
    121: "y",
    122: "z",
    65: "A",
    66: "B",
    67: "C",
    68: "D",
    69: "E",
    70: "F",
    71: "G",
    72: "H",
    73: "I",
    74: "J",
    75: "K",
    76: "L",
    77: "M",
    78: "N",
    79: "O",
    80: "P",
    81: "Q",
    82: "R",
    83: "S",
    84: "T",
    85: "U",
    86: "V",
    87: "W",
    88: "X",
    89: "Y",
    90: "Z",
}


NUMEROS_DIC = {
    49: '1',
    50: '2',
    51: '3',
    52: '4',
    53: '5',
    54: '6',
    55: '7',
    56: '8',
    57: '9',
    48: '0',
}


class Opcion(NamedTuple):
    mensaje: str
    funcion: Any
    nombretransf: Any