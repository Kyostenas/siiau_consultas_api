from __future__ import annotations

from typing import NamedTuple, List
from bs4 import BeautifulSoup as WebSp
from utiles import limpiar_html
from unidecode import unidecode
from textwrap import wrap
import datetime

CORRECCION_RANGO_HORAS = 5
DURACION_UNA_CLASE = 55


# TODO Decidir si sera solo consulta de horario o de semestre completo


class Semestre(NamedTuple):
    ciclo: str
    carrera: str
    creditos: int
    horario: List[dict]
    horario_tabla: dict


class DiasClase(NamedTuple):
    L: dict
    M: dict
    I: dict
    J: dict
    V: dict
    S: dict


class HorarioSemestre(NamedTuple):
    creditos_semestre: int
    clases: list | tuple


class Clase(NamedTuple):
    nrc: str
    clave: str
    nombre: str  # previamente "materia"
    seccion: str
    creditos: int
    dias_clase: dict  # previamente "horario_materia"
    edificio: dict
    aula: dict
    profesores: dict  # TODO corregir guardado de profesores, fechas, dias clase , edificio, aula, ref
    fecha_inicio: dict
    fecha_final: dict
    fecha_inicio_completa: dict
    fecha_final_completa: dict
    referencia_horario_tabla: dict  # previamente "ref_horario_compacto"


class Formados(NamedTuple):
    horario_tabla: dict
    horario: dict


class HorarioTabla(NamedTuple):
    HORARIO: List[str]
    L: List[str]
    M: List[str]
    I: List[str]
    J: List[str]
    V: List[str]
    S: List[str]


class HorasClase(NamedTuple):
    dia: str
    rango_horas: list[str]


class Tabla(NamedTuple):
    encabezado: list
    cuerpo: list


def _part_mats(materias, tam):
    materias = list(materias)
    desordenado = [materias[i::tam] for i in range(tam)]
    _ord = [x + ['' for _ in range(len(desordenado[0]) - len(x))]
            for x in desordenado]
    return tuple(zip(*_ord))


def _corregir_datos(paso, datos):
    indice_nrc = 0
    datos = datos[:]
    while indice_nrc < len(datos):
        if datos[indice_nrc] == '':
            [datos.insert(indice_nrc, '') for _ in range(4)]
        indice_nrc += paso

    return datos


def _rango_horas(inicio: int, fin: int, paso: int, correcion: int = CORRECCION_RANGO_HORAS):
    """
    Recibe inicio=1700, fin=1855, paso=100
    Retorna generador que crea: (('1700, '1755'), ('1800', '1855))
    """
    for paso_hora in range(inicio, fin + correcion, paso):
        aumento = ''
        if len(str(paso_hora)) == 3:
            aumento = '0'
        yield f'{aumento}{paso_hora}', f'{aumento}{paso_hora + DURACION_UNA_CLASE}'


def _obtener_dias_de_clase(rango_dias_clase: list, hora: str):
    return DiasClase(
        L=__revisar_dia(rango_dias_clase[0], hora),
        M=__revisar_dia(rango_dias_clase[1], hora),
        I=__revisar_dia(rango_dias_clase[2], hora),
        J=__revisar_dia(rango_dias_clase[3], hora),
        V=__revisar_dia(rango_dias_clase[4], hora),
        S=__revisar_dia(rango_dias_clase[5], hora)
    )._asdict()


def __revisar_dia(recuadro_dia: str, hora) -> dict:
    if recuadro_dia != '':
        return {0: hora}
    return {}


def _generar_ref_clase(seccion: str, edificio: str, aula: str):
    return f'{seccion} - {edificio} {aula}'


class HorarioSiiau(object):

    def __init__(self, consulta, carrera) -> None:
        self.consulta = consulta
        self.carrera = carrera
        self.datos_crudos_estudiante: Tabla
        self.datos_crudos_horario: Tabla
        self.datos_estudiante = ()
        self.horario_siiau = ()
        self.columnas_horario = ()
        self.horario_tabla = {}
        self.horario = {}
        self.ciclo_del_horario = ''
        self.ciclo_actual = ''
        self.creditos = 0

    @property
    def i_nrc(self):
        return 0

    @property
    def i_clave_materia(self):
        return 1

    @property
    def i_nombre_materia(self):
        return 2

    @property
    def i_seccion(self):
        return 3

    @property
    def i_creditos(self):
        return 4

    @property
    def i_hora_clase(self):
        return 5

    @property
    def rango_dias(self):
        return slice(6, 12)

    @property
    def i_edificio(self):
        return 12

    @property
    def i_aula(self):
        return 13

    @property
    def i_profesor(self):
        return 14

    @property
    def i_fecha_inicio(self):
        return 15

    @property
    def i_fecha_final(self):
        return 16

    @property
    def i_ciclo_actual(self):
        return 5

    @property
    def i_carrera(self):
        return 6

    @property
    def dias_cortos(self):
        return ['L', 'M', 'I', 'J', 'V', 'S']

    @property
    def i_dias_cortos(self):
        return dict(L=0, M=1, I=2, J=3, V=4, S=5)

    @property
    def formato_matutino(self):
        return 'a.m.'

    @property
    def formato_vespertino(self):
        return 'p.m.'

    @property
    def hora_sep(self):
        return '\\'

    @property
    def materia_sin_horario(self):
        return f'Sin{self.hora_sep}hora'

    @property
    def nombres_dias(self):
        return {1: 'Lunes', 2: 'Martes', 3: 'Miércoles',
                4: 'Jueves', 5: 'Viernes', 6: 'Sábado',
                7: 'Domingo'}

    @property
    def nombres_meses(self):
        return {1: 'Enero', 2: 'Febrero', 3: 'Marzo',
                4: 'Abril', 5: 'Mayo', 6: 'Junio',
                7: 'Julio', 8: 'Agosto', 9: 'Septiembre',
                10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

    @property
    def horas_completas_horario_24(self):
        return ['07:00\n07:55', '08:00\n08:55', '09:00\n09:55',
                '10:00\n10:55', '11:00\n11:55', '12:00\n12:55',
                '13:00\n13:55', '14:00\n14:55', '15:00\n15:55',
                '16:00\n16:55', '17:00\n17:55', '18:00\n18:55',
                '19:00\n19:55', '20:00\n20:55', '21:00\n21:55']

    def obtener(self):
        self._datos_crudos()
        encabezado_horario = self.datos_crudos_horario.encabezado
        cuerpo_horario = self.datos_crudos_horario.cuerpo
        cuerpo_horario = _corregir_datos(len(encabezado_horario), cuerpo_horario)
        self.horario_siiau = (tuple(encabezado_horario),
                              *_part_mats(cuerpo_horario, len(encabezado_horario)))
        self.columnas_horario = tuple(zip(*self.horario_siiau[1:]))
        self.horario = self._hacer_dic()
        self.horario_tabla = self._compactar()

        return Semestre(ciclo=self.ciclo_del_horario,
                        carrera=self.carrera,
                        creditos=self.creditos,
                        horario=self.horario,
                        horario_tabla=self.horario_tabla)._asdict()

    def _datos_crudos(self):
        html = WebSp(self.consulta.horario().text, 'html.parser')
        encabezados_crudos = html.find_all('th')
        cuerpo_crudo = html.find_all('td')
        encabezados_limpios = []
        cuerpo_limpio = []
        for encabezado in encabezados_crudos:
            encl = limpiar_html(encabezado)
            encl = unidecode(encl.replace(':', '').upper())
            encabezados_limpios.append(encl)
        for linea in cuerpo_crudo:
            cuerpo_limpio.append(limpiar_html(linea))
        encabezados_limpios.pop(0)
        ciclo_horario = encabezados_limpios.pop(9)
        ciclo_horario = ciclo_horario.split(' ')[-1]
        self.ciclo_del_horario = ciclo_horario
        division = encabezados_limpios.index('NRC')
        encabezados_dat_es = encabezados_limpios[:division]
        encabezados_horario = encabezados_limpios[division:]
        cuerpo_dat_es = cuerpo_limpio[:division]
        cuerpo_horario = cuerpo_limpio[division:]
        # if self.carrera == 'BGC':
        #     encabezados_dat_es.pop(-1)
        #     cuerpo_dat_es.pop(-1)
        self.datos_crudos_estudiante = Tabla(encabezados_dat_es, cuerpo_dat_es)
        self.datos_crudos_horario = Tabla(encabezados_horario, cuerpo_horario)
        self.ciclo_actual = self.datos_crudos_estudiante.cuerpo[self.i_ciclo_actual]
        carrera = self.datos_crudos_estudiante.cuerpo[self.i_carrera]
        carrera = carrera.split(' ')[-1]
        carrera = carrera.replace('(', '').replace(')', '')
        self.carrera = carrera

    def _hacer_dic(self) -> list[dict]:
        creditos = [int(creditos) for creditos in self.columnas_horario[self.i_creditos][0:]
                    if creditos.isnumeric()]
        creditos = sum(creditos)
        self.creditos = creditos
        clases = []
        for fila_clase in self.horario_siiau[1:]:
            if fila_clase[self.i_nrc] == '':
                self.__combinar_multiples_clases(clases, fila_clase)
            else:
                nueva_clase = self.__llenar_datos_de_clase(fila_clase)
                clases.append(nueva_clase._asdict())

        return clases

    def _compactar(self):
        filas_sin_horas = 0
        horario_compacto = dict()
        for clase in self.horario:
            horas_clases = self.__obtener_rangos_de_horas(clase['dias_clase'])
            for horas_de_una_clase in horas_clases:
                for i_hora, una_hora in enumerate(horas_de_una_clase.rango_horas):
                    posicion_en_fila = self.dias_cortos.index(horas_de_una_clase.dia)
                    nombre_clase = clase['nombre']
                    # nombre_clase = '\n'.join(list(wrap(clase['nombre'], 15)))
                    if i_hora + 1 == len(horas_de_una_clase.rango_horas):
                        # final = f'\n\n{clase["referencia_horario_tabla"]}'
                        final = f'\\{clase["referencia_horario_tabla"]}'
                    else:
                        final = ''
                    try:
                        horario_compacto[una_hora][posicion_en_fila] = ''.join([nombre_clase, final])
                    except KeyError:
                        nueva_fila = ['', '', '', '', '', '']
                        nueva_fila[posicion_en_fila] = ''.join([nombre_clase, final])
                        horario_compacto[una_hora] = nueva_fila
        ordenado_y_reestructurado = self.__reestructurar_a_columnas(dict(sorted(horario_compacto.items())))
        return ordenado_y_reestructurado

    def __combinar_multiples_clases(self, clases: list[dict], fila_sin_nrc: list):
        """
        Esta function modifica la lista de clases que se asigne al parametro clases.

        Su propósito es agregar a la ultima clase las horas de clase del renglón o
        renglones del horario de siiau siguientes que no tengan nrc.

        NOTA: Estos renglones sin nrc forman parte de la misma materia, solo que se
        imparten en otra hora o salon.
        """
        dias_clase = _obtener_dias_de_clase(rango_dias_clase=fila_sin_nrc[self.rango_dias],
                                            hora=fila_sin_nrc[self.i_hora_clase])
        # for dia in self.dias_cortos:
        #     for nueva_hora in dias_clase:
        #         nuevo_i = len(clases[-1]['dias_clase'][dia])
        #         clases[-1]['dias_clase'][dia][nuevo_i] =

        print(dias_clase)

    def __obtener_rangos_de_horas(self, dias_clase: dict):
        horas_clase_por_dia = list()
        for dia, horas in dias_clase.items():
            if len(horas) > 0:
                horas_con_formato = []
                for hora in horas:
                    horas_con_formato += self.__procesar_hora(hora)
                horas_clase_por_dia.append(
                    HorasClase(dia=dia, rango_horas=horas_con_formato)
                )

        return horas_clase_por_dia

    def __llenar_datos_de_clase(self, fila_clase: list):
        fecha_inicio = fila_clase[self.i_fecha_inicio]
        fecha_final = fila_clase[self.i_fecha_final]
        creditos = fila_clase[self.i_creditos]
        seccion = fila_clase[self.i_seccion]
        edficio = fila_clase[self.i_edificio]
        aula = fila_clase[self.i_aula]
        return Clase(
            nrc=fila_clase[self.i_nrc],
            clave=fila_clase[self.i_clave_materia],
            nombre=fila_clase[self.i_nombre_materia],
            seccion=seccion,
            creditos=creditos,
            dias_clase=_obtener_dias_de_clase(rango_dias_clase=fila_clase[self.rango_dias],
                                              hora=fila_clase[self.i_hora_clase]),
            edificio=edficio,
            aula=aula,
            profesores={0: fila_clase[self.i_profesor].title()},
            fecha_inicio={0: fecha_inicio},
            fecha_final={0: fecha_final},
            fecha_inicio_completa={0: self.__obtener_fecha_completa(fecha=fecha_inicio)},
            fecha_final_completa={0: self.__obtener_fecha_completa(fecha=fecha_final)},
            referencia_horario_tabla={0: _generar_ref_clase(seccion=seccion,
                                                            edificio=edficio,
                                                            aula=aula)}
        )

    def __obtener_fecha_completa(self, fecha: str):
        # Fechas en horario siiau son: dd-mm-aa
        dia, mes, year = tuple(map(int, fecha.split('-')))
        dia_semana = datetime.date(year, mes, dia).weekday()
        nombre_dia = self.nombres_dias[dia_semana + 1]
        nombre_mes = self.nombres_meses[mes]

        # Ej. de frase: 'Sábado 1 de Enero, 2022'  (Happy new year!)
        frase = f'{nombre_dia} {dia} de {nombre_mes}, {year}'

        return frase

    def __obtener_nombre_completo(self, indice_fila: int, materia_actual: str):
        nombre = self.columnas_horario[self.i_nombre_materia][indice_fila]
        if nombre == '':
            nombre = materia_actual
        ref_horario_compacto = self.horario[indice_fila]['referencia_horario_tabla']
        nombre_completo = '\n'.join(wrap(nombre, 15) + ['', ref_horario_compacto])

        return nombre_completo, nombre

    def __reestructurar_a_columnas(self, horario: dict):
        """
        Recibe: {'5:00 p.m\\n5:55p.m.': ['', 'METODOS MATEMATICOS II', '', '', '', ''], ...}
        Retorna: {'HORARIO': ['5:00 p.m\\n5:55p.m.', ...], 'L': ['', ...], 'M': ['METODOS MATEMATICOS II', ...], ...}
        """
        horas = tuple(horario.keys())
        columnas_materias_por_dia = tuple(zip(*horario.values()))
        horario_reestructurado = dict(HORARIO=horas)
        for i, columna_dia in enumerate(columnas_materias_por_dia):
            horario_reestructurado[self.dias_cortos[i]] = columna_dia

        return horario_reestructurado

    def __procesar_hora(self, hora_sin_formato: str):
        """
        Recibe hora en formato hhmm-hhmm y retorna hh:mm f.f \\n hh:mm f.f.
        Ademas, genera un rango de 55 minutos por cada hora abarcada en
        el rango total recibido.

        Ejemplo: '1700-2055'  ->  ['5:00 p.m.\\n 5:55 p.m.', '6:00 p.m.\\n 6:55 p.m.',
        '7:00 p.m.\\n 7:55 p.m.', '8:00 p.m.\\n 8:55 p.m.']

        Ejemplo: '0011-0011'  ->  'Sin\\nhora'
        """
        mitades_de_hora = hora_sin_formato.split('-')
        horas_de_clase = _rango_horas(*map(int, mitades_de_hora), 100)
        horas_de_clase_formateadas = []
        for horas_de_un_espacio in horas_de_clase:
            horas_de_un_espacio_formateadas = self.__formatear_hora(horas_de_un_espacio)
            if horas_de_un_espacio_formateadas is None:
                horas_de_clase_formateadas.append(self.materia_sin_horario)
            else:
                horas_de_clase_formateadas.append(horas_de_un_espacio_formateadas)

        return horas_de_clase_formateadas

    def __formatear_hora(self, una_hora: tuple):
        mitades_formateadas = []
        for mitad in una_hora:
            hora_en_formato_12h = self.__convertir_formato_24h_a_12h(mitad)
            if hora_en_formato_12h is None:
                return None
            mitades_formateadas.append(hora_en_formato_12h)
        return f'{self.hora_sep}'.join(mitades_formateadas)

    def __convertir_formato_24h_a_12h(self, hora: str):
        """
        Recibe hora en formato hhmm y retorna hh:mm f.f
        Ejemplo: '0800'  ->  '8:00 a.m.'

        Si la hora cae fuera del rango 7:00 - 21:55, retorna None
        """
        hora_entera = int(hora)
        if 699 < hora_entera < 1300:  # 7:00 a.m. - 12:59 a.m.
            hora_con_formato = f'{hora[:2]}:{hora[2:]} {self.formato_matutino}'
        elif 1259 < hora_entera < 2200:  # 1:00 p.m - 9:59 p.m.
            hora_restada = int(hora[:2]) - 12
            hora_con_formato = f'{hora_restada}:{hora[2:]} {self.formato_vespertino}'
        else:
            return None

        return hora_con_formato