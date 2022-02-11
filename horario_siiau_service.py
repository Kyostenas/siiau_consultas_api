from __future__ import annotations

import inspect

from consulta_siiau_service import SesionSIIAU, ConsultaSIIAU, HorarioCompletoSiiau
from typing import NamedTuple, Union, Type, List
from tabla_service import named_tuple_a_tabla
from utiles import es_alguna_instancia
from inspect import getmembers
import datetime

CORRECCION_RANGO_HORAS = 5
DURACION_UNA_CLASE = 55
FORMATO_VESPERTINO = 'p.m.'
FORMATO_MATUTINO = 'a.m.'
HORA_INICIO_MATERIAS = 0
HORA_FINAL_MATERIAS = 1
NOMBRE_DE_MIEMBRO = 0
VALOR_DE_MIEMBRO = 1
HORA_SEP = '\\'
MATERIA_SIN_HORARIO = 'Sin Hora'
I_LUNES = 0
I_MARTES = 1
I_MIERCOES = 2
I_JUEVES = 3
I_VIERNES = 4
I_SABADO = 5  # clases en sábado :(

NOMBRES_DIAS = {1: 'Lunes',  2: 'Martes',  3: 'Miércoles',
                4: 'Jueves', 5: 'Viernes', 6: 'Sábado',
                7: 'Domingo'}  # Domingo porque en virtuales pueden comenzar en Domingo D:
NOMBRES_MESES = {1: 'Enero',    2: 'Febrero',    3: 'Marzo',
                 4: 'Abril',    5: 'Mayo',       6: 'Junio',
                 7: 'Julio',    8: 'Agosto',     9: 'Septiembre',
                 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

class DiaClase(NamedTuple):
    hora_inicio: str
    hora_final: str
    hora_inicio_completa: str
    hora_final_completa: str
    profesor: str
    edificio: str
    aula: str
    rango_horas: tuple


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


def _generar_ref_clase(seccion: str, edificio: str, aula: str):
    return f'{seccion} - {edificio} {aula}'


def __convertir_formato_24000_a_12h(hora: str):
        """
        Recibe hora en formato hhmm y retorna hh:mm f.f
        Ejemplo: '0800'  ->  '8:00 a.m.'

        Si la hora cae fuera del rango 7:00 - 21:55, retorna None
        """
        hora_entera = int(hora)
        if 699 < hora_entera < 1300:  # 7:00 a.m. - 12:59 a.m.
            hora_con_formato = f'{hora[:2]}:{hora[2:]} {FORMATO_MATUTINO}'
        elif 1259 < hora_entera < 2200:  # 1:00 p.m - 9:59 p.m.
            hora_restada = int(hora[:2]) - 12
            hora_con_formato = f'{hora_restada}:{hora[2:]} {FORMATO_VESPERTINO}'
        else:
            return None

        return hora_con_formato


def __formatear_hora(una_hora: tuple):
    mitades_formateadas = []
    for mitad in una_hora:
        hora_en_formato_12h = __convertir_formato_24000_a_12h(mitad)
        if hora_en_formato_12h is None:
            return None
        mitades_formateadas.append(hora_en_formato_12h)
    return f'{HORA_SEP}'.join(mitades_formateadas)


def __procesar_rango_horas(inicio: str, final: str):
    """
    Recibe hora en formato hhmm-hhmm y retorna hh:mm f.f \\n hh:mm f.f.
    Ademas, genera un rango de 55 minutos por cada hora abarcada en
    el rango total recibido.

    Ejemplo: '1700-2055'  ->  ['5:00 p.m.\\n 5:55 p.m.', '6:00 p.m.\\n 6:55 p.m.',
    '7:00 p.m.\\n 7:55 p.m.', '8:00 p.m.\\n 8:55 p.m.']

    Ejemplo: '0011-0011'  ->  'Sin\\nhora'
    """
    mitades_de_hora = [inicio, final]
    horas_de_clase = _rango_horas(*map(int, mitades_de_hora), 100)
    horas_de_clase_formateadas = []
    for horas_de_un_espacio in horas_de_clase:
        horas_de_un_espacio_formateadas = __formatear_hora(horas_de_un_espacio)
        if horas_de_un_espacio_formateadas is None:
            horas_de_clase_formateadas.append(MATERIA_SIN_HORARIO)
        else:
            horas_de_clase_formateadas.append(horas_de_un_espacio_formateadas)
    horas_de_clase_formateadas = tuple(horas_de_clase_formateadas)

    return horas_de_clase_formateadas


def __obtener_fecha_completa(fecha: str):
        # Fechas en horario siiau son: dd-mm-aa
        dia, mes, year = tuple(map(int, fecha.split('-')))
        dia_semana = datetime.date(year, mes, dia).weekday()
        nombre_dia = NOMBRES_DIAS[dia_semana + 1]
        nombre_mes = NOMBRES_MESES[mes]

        # Ej. de frase: 'Sábado 1 de Enero, 2022'  (Happy new year!)
        frase = f'{nombre_dia} {dia} de {nombre_mes}, {year}'

        return frase


def __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas: HorarioCompletoSiiau, i_actual):
    datos_dia = dict()

    datos_dia['hora_inicio'] = hora_inicio
    datos_dia['hora_final'] = hora_final
    datos_dia['hora_inicio_completa'] = __convertir_formato_24000_a_12h(hora_inicio)
    datos_dia['hora_final_completa'] = __convertir_formato_24000_a_12h(hora_final)
    datos_dia['edificio'] = horario_por_columnas.edificio[i_actual]
    datos_dia['aula'] = horario_por_columnas.aula[i_actual]
    datos_dia['profesor'] = horario_por_columnas.profesor[i_actual]
    datos_dia['rango_horas'] = __procesar_rango_horas(hora_inicio, hora_final)

    return datos_dia


def _procesar_dias_clase(datos_clase: dict, horario_por_columnas: HorarioCompletoSiiau, i_horario: int):
    hora_formato_siiau = horario_por_columnas.horario[i_horario].split('-')
    hora_inicio = hora_formato_siiau[HORA_INICIO_MATERIAS]
    hora_final = hora_formato_siiau[HORA_FINAL_MATERIAS]
    if horario_por_columnas.L[i_horario] == 'L':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_lu'] = nuevo_dia
    else:
        datos_clase['dia_lu'] = None
    if horario_por_columnas.M[i_horario] == 'M':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_ma'] = nuevo_dia
    else:
        datos_clase['dia_ma'] = None
    if horario_por_columnas.I[i_horario] == 'I':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_mi'] = nuevo_dia
    else:
        datos_clase['dia_mi'] = None
    if horario_por_columnas.J[i_horario] == 'J':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_ju'] = nuevo_dia
    else:
        datos_clase['dia_ju'] = None
    if horario_por_columnas.V[i_horario] == 'V':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_vi'] = nuevo_dia
    else:
        datos_clase['dia_vi'] = None
    if horario_por_columnas.S[i_horario] == 'S':
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_sa'] = nuevo_dia
    else:
        datos_clase['dia_sa'] = None


def _procesar_clase(horario_por_columnas: HorarioCompletoSiiau, nrc_clase, i_datos_materia, i_horario):
    fecha_inicio = horario_por_columnas.fecha_inicio[i_horario]
    fecha_final = horario_por_columnas.fecha_fin[i_horario]

    datos_clase = dict()

    datos_clase['nrc'] = nrc_clase
    datos_clase['clave_materia'] = horario_por_columnas.clave[i_datos_materia]
    datos_clase['nombre'] = horario_por_columnas.nombre_materia[i_datos_materia]
    datos_clase['seccion'] = horario_por_columnas.seccion[i_datos_materia]
    datos_clase['creditos'] = horario_por_columnas.creditos[i_datos_materia]
    _procesar_dias_clase(datos_clase, horario_por_columnas, i_horario)
    datos_clase['fecha_inicio'] = fecha_inicio
    datos_clase['fecha_final'] = fecha_final
    datos_clase['fecha_inicio_completa'] = __obtener_fecha_completa(fecha_inicio)
    datos_clase['fecha_final_completa'] = __obtener_fecha_completa(fecha_final)

    return datos_clase


def estructurar_horario_por_clases(horario_por_columnas: HorarioCompletoSiiau):
    clases = []
    ultimo_nrc = ''
    ultimo_i = 0
    nrcs = horario_por_columnas.nrc

    for i_renglon, nrc_clase in enumerate(nrcs):
        if nrc_clase != '':
            datos_clase = _procesar_clase(horario_por_columnas, nrc_clase, i_renglon, i_renglon)
            ultimo_nrc = nrc_clase
            ultimo_i = i_renglon
        else:
            datos_clase = _procesar_clase(horario_por_columnas, ultimo_nrc, ultimo_i, i_renglon)

        clases.append(Clase(**datos_clase))

    return clases


def _agregar_horas_y_nombres(h_por_horas: dict, dia: DiaClase, nombre_clase: str, i_dia):
    for hora_clase in dia.rango_horas:
        try:
            h_por_horas[hora_clase][i_dia] = nombre_clase
        except KeyError:
            # Si no existe la fila de esa hora, agregarla
            h_por_horas[hora_clase] = ['', '', '', '', '', '']  # cada cadena vacia es un día
            h_por_horas[hora_clase][i_dia] = nombre_clase


def compactar_horario_por_clases(clases):

    horario_por_horas = dict()

    for clase in clases:
        if clase.dia_lu is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_lu, clase.nombre, I_LUNES)
        if clase.dia_ma is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_ma, clase.nombre, I_MARTES)
        if clase.dia_mi is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_mi, clase.nombre, I_MIERCOES)
        if clase.dia_ju is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_ju, clase.nombre, I_JUEVES)
        if clase.dia_vi is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_vi, clase.nombre, I_VIERNES)
        if clase.dia_sa is not None:
            _agregar_horas_y_nombres(horario_por_horas, clase.dia_sa, clase.nombre, I_SABADO)

    horario_por_horas_ordenado = dict(sorted(horario_por_horas.items()))

    horas = list(horario_por_horas_ordenado.keys())
    clases_compactas_por_filas = list(horario_por_horas_ordenado.values())
    clases_compactas_por_columna = list(zip(*clases_compactas_por_filas))
    horario_compactado = HorarioCompacto(horas, *clases_compactas_por_columna)

    return horario_compactado


if __name__ == '__main__':
    from os import environ as env
    usuario = env['USUARIO_Y']
    contra = env['CONTRA_Y']
    carrera = env['CARRERA_Y']
    ciclo = env['CICLO_ACTUAL']


    sesion = SesionSIIAU(usuario, contra).obtener()
    pidm_p = sesion.pidmp
    cookies = sesion.cookies
    consulta = ConsultaSIIAU(ciclo=ciclo, cookies=cookies, carrera=carrera, pidm_p=pidm_p)
    datos_horario = consulta.horario()

    # print(named_tuple_a_tabla(datos_horario.horario, por_columnas=True))
    # exit()

    horario_por_clases = estructurar_horario_por_clases(datos_horario.horario)
    horario_compacto = compactar_horario_por_clases(horario_por_clases)

    print(named_tuple_a_tabla(horario_compacto, por_columnas=True))



    # print(horario_compacto)


















