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


from typing import NamedTuple, Tuple, Union


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


class Teclas(NamedTuple):
    _1: int = 49
    _2: int = 50
    _3: int = 51
    _4: int = 52
    _5: int = 53
    _6: int = 54
    _7: int = 55
    _8: int = 56
    _9: int = 57
    _0: int = 48
    _a: int = 97
    _b: int = 98
    _c: int = 99
    _d: int = 100
    _e: int = 101
    _f: int = 102
    _g: int = 103
    _h: int = 104
    _i: int = 105
    _j: int = 106
    _k: int = 107
    _l: int = 108
    _m: int = 109
    _n: int = 110
    _o: int = 111
    _p: int = 112
    _q: int = 113
    _r: int = 114
    _s: int = 115
    _t: int = 116
    _u: int = 117
    _v: int = 118
    _w: int = 119
    _x: int = 120
    _y: int = 121
    _z: int = 122
    _ctrl_a: int = 1
    _ctrl_b: int = 2
    _ctrl_c: int = 3
    _ctrl_d: int = 4
    _ctrl_e: int = 5
    _ctrl_f: int = 6
    _ctrl_g: int = 7
    _ctrl_h: int = 8
    _ctrl_i: int = 9
    _ctrl_j: int = 10
    _ctrl_k: int = 11
    _ctrl_l: int = 12
    _ctrl_m: int = 13
    _ctrl_n: int = 14
    _ctrl_o: int = 15
    _ctrl_p: int = 16
    _ctrl_q: int = 17
    _ctrl_r: int = 18
    _ctrl_s: int = 19
    _ctrl_t: int = 20
    _ctrl_u: int = 21
    _ctrl_v: int = 22
    _ctrl_w: int = 23
    _ctrl_x: int = 24
    _ctrl_y: int = 25
    _ctrl_z: int = 26
    _enter : int = 13
    _escape : int = 27
    _retroceso: int = 8,
    _flecha_ar : int = 72
    _flecha_ab: int = 80
    _flecha_iz : int = 75
    _flecha_de : int = 77
    _espacio: int = 32
