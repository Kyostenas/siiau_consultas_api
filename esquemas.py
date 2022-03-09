from typing import NamedTuple, Tuple, List


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
