""" MODULO PRINCIPAL """

from typing import NamedTuple
from siiau_consultas_api.consultaSiiauService import SesionSIIAU, ConsultaSIIAU
from semestreSiiau import HorarioSiiau
from ofertaSegunSeleccion import Oferta
from posiblesHorarios import combinar_nrcs

CENTROS = {
    1: {'simbolo': '3', 'nombre': 'C. U. DE TLAJOMULCO'},
    2: {'simbolo': 'A', 'nombre': 'C.U. DE ARTE, ARQ. Y DISEÑO'},
    3: {'simbolo': 'B', 'nombre': 'C.U. DE CS. BIOLOGICO Y AGR.'},
    4: {'simbolo': 'C', 'nombre': 'C.U. DE CS. ECONOMICO-ADMINISTRATIVAS.'},
    5: {'simbolo': 'D', 'nombre': 'C.U. DE CS. EXACTAS E ING.'},
    6: {'simbolo': 'E', 'nombre': 'C.U. DE CS. DE LA SALUD'},
    7: {'simbolo': 'F', 'nombre': 'C.U. DE CS. SOCIALES Y HUM.'},
    8: {'simbolo': 'G', 'nombre': 'C.U. DE LOS ALTOS'},
    9: {'simbolo': 'H', 'nombre': 'C.U. DE LA CIENEGA'},
    10: {'simbolo': 'I', 'nombre': 'C.U. DE LA COSTA'},
    11: {'simbolo': 'J', 'nombre': 'C.U. DE LA COSTA SUR'},
    12: {'simbolo': 'K', 'nombre': 'C.U. DEL SUR'},
    13: {'simbolo': 'M', 'nombre': 'C. U. DE LOS VALLES'},
    14: {'simbolo': 'N', 'nombre': 'C.U. DEL NORTE'},
    15: {'simbolo': 'O', 'nombre': 'CUCEI SEDE VALLES'},
    16: {'simbolo': 'P', 'nombre': 'CUCSUR SEDE VALLES'},
    17: {'simbolo': 'Q', 'nombre': 'CUCEI SEDE NORTE'},
    18: {'simbolo': 'R', 'nombre': 'CUALTOS SEDE NORTE'},
    19: {'simbolo': 'S', 'nombre': 'CUCOSTA SEDE NORTE'},
    20: {'simbolo': 'T', 'nombre': 'SEDE TLAJOMULCO'},
    21: {'simbolo': 'U', 'nombre': 'C. U. DE LOS LAGOS'},
    22: {'simbolo': 'V', 'nombre': 'CICLO DE VERANO'},
    23: {'simbolo': 'W', 'nombre': 'CUCEA SEDE VALLE'},
    24: {'simbolo': 'X', 'nombre': 'SISTEMA DE UNIVERSIDAD VIRTUAL'},
    25: {'simbolo': 'Y', 'nombre': 'ESCUELAS INCORPORADAS'},
    26: {'simbolo': 'Z', 'nombre': 'C. U. DE TONALA'}
}


class Sesion(NamedTuple):
    cookies: str
    pidm_p: int


class DatosSemestre(NamedTuple):
    datos_completos: dict
    carrera: str
    ciclo_horario: str
    ciclo_actual: str


def iniciar_sesion(codigo, clave):
    # print('INICIO DE SESION')
    # codigo = input('codigo (obligatorio): ')
    # clave = input('clave (obligatorio): ')

    sesion = SesionSIIAU(codigo, clave)
    # sesion.validar()
    cookies = sesion.obtener_cookies()
    pidm_p = sesion.obtener_pidm_p()

    return Sesion(cookies, pidm_p)


def obtener_horario_del_alumno(sesion: Sesion | dict, ciclo: str, carrera: str) -> DatosSemestre:
    """
    Lo que retorna HorarioSiiau:

    Formados(NamedTuple):
       horario_tabla: dict | Horario por columna
       horario: dict | Informacion completa del horario
    """
    try:
        cookies_siiau = sesion.cookies
        pidmp_siiau = sesion.pidm_p
    except AttributeError:
        cookies_siiau = sesion['cookies']
        pidmp_siiau = sesion['pidm_p']

    consulta_horario = ConsultaSIIAU(ciclo,
                                     carrera,
                                     cookies_siiau,
                                     pidmp_siiau)
    objeto_horario = HorarioSiiau(consulta_horario, carrera)
    horario_semestre = objeto_horario.obtener()
    ciclo_actual = objeto_horario.ciclo_actual
    ciclo_horario = objeto_horario.ciclo_del_horario
    carrera_actual = objeto_horario.carrera

    return DatosSemestre(datos_completos=horario_semestre,
                         carrera=carrera_actual,
                         ciclo_horario=ciclo_horario,
                         ciclo_actual=ciclo_actual)


def obtener_oferta_academica():
    print('\nOFERTA ACADEMICA')

    # seleccionadas = [
    #     (0, 1),  (0, 3),  (0, 4),  (1, 1),  (1, 3),  (1, 4),
    #     (2, 1),  (2, 3),  (2, 4),  (3, 1),  (3, 3),  (3, 4),
    #     (4, 1),  (4, 3),  (4, 4),  (5, 1),  (5, 3),  (5, 4),
    #     (6, 1),  (6, 3),  (6, 4),  (7, 1),  (7, 3),  (7, 4),
    #     (8, 1),  (8, 3),  (8, 4),  (9, 1),  (9, 3),  (9, 4),
    #     (10, 0), (10, 1), (10, 2), (10, 3), (11, 0), (11, 1),
    #     (11, 2), (11, 3), (12, 0), (12, 1), (12, 2), (12, 3),
    #     (13, 0), (13, 1), (13, 2), (13, 3), (14, 0), (14, 1),
    #     (14, 2), (14, 3), (5, 0),  (5, 1),  (5, 2),  (5, 3),
    #     (5, 4),  (5, 5),  (5, 6),  (5, 7),  (5, 8),  (5, 9),
    #     (5, 10), (5, 11), (5, 12), (5, 13), (5, 14),
    #     ]

    seleccionadas = [(x, y) for x in range(16) for y in range(9)]
    # carrera = input('carrera (opcional): ')
    ciclo = input('ciclo (obligatorio): ')
    materias = []
    while True:
        nueva = input('materias (opcional): ')
        materias.append(nueva)
        if nueva == '0':
            break

    print('Centros a escoger:')
    for num, vals in CENTROS.items():
        print(f'\t{num} - {vals["nombre"]}')
    centro = int(input('centro (obligatorio): '))
    centro = CENTROS[centro]['simbolo']
    consulta_oferta = ConsultaSIIAU(ciclo)
    oferta = Oferta(consulta_oferta, *materias, centro=centro)
    oferta = oferta.buscar(seleccionadas)

    return oferta


def hacer_posibles_horarios(oferta):
    sel_prof = {}
    for materia, profes in oferta.profesores.items():
        print(materia, oferta.materias[materia]['nombre'])
        for profe in range(len(profes)):
            print(f'\t{profe + 1} - {profes[profe]}')

        seleccion = input(f'Seleccione los profes de {materia}: ').split(' ')
        profes_seleccionados = []
        for sel in seleccion:
            profes_seleccionados.append(profes[int(sel) - 1])
        sel_prof[materia] = profes_seleccionados

    horarios = combinar_nrcs(oferta.nrcs, oferta.materias, sel_prof)

    return horarios, sel_prof


def main():
    try:
        sesion = iniciar_sesion()
    except:
        print('No se pudo iniciar sesión.')
        return
    obtener_horario_semestre(sesion)
    oferta = obtener_oferta_academica()
    hacer_posibles_horarios(oferta)


if __name__ == '__main__':
    main()