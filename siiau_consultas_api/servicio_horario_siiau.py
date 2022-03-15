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


from .servicio_consulta_siiau import HorarioCompletoSiiau
from .esquemas import Clase, DiaClase, HorarioCompacto
from .utiles import aplanar_lista

import datetime

CORRECCION_RANGO_HORAS = 5
DURACION_UNA_CLASE = 55
FORMATO_VESPERTINO = 'p.m.'
FORMATO_MATUTINO = 'a.m.'
HORA_INICIO_MATERIAS = 0
HORA_FINAL_MATERIAS = 1
NOMBRE_DE_MIEMBRO = 0
VALOR_DE_MIEMBRO = 1
SEP = '\\'
SEP_DAT_MAT = '%'
INDIC_DAT_MAT = '>'
MATERIA_SIN_HORARIO = 'Sin Hora'
I_LUNES = 0
I_MARTES = 1
I_MIERCOES = 2
I_JUEVES = 3
I_VIERNES = 4
I_SABADO = 5  # clases en sábado :(
DIFERENCIA_24H = 12
HORAS_DIA = 24
MINUTOS_HORA = 60
CANT_DIGS_HORA_HHMM = 4
HORAS_DIA_HHMM = 2400
INICO_DIA_HHMM = 0
MEDIO_DIA_HHMM = 1200
FINAL_DIA_HMMM = 2359
MITAD_HORA_HHMM = 2
MITAD_HORA_RANGO_HHMM = 0



NOMBRES_DIAS = {1: 'Lunes',  2: 'Martes',  3: 'Miercoles',
                4: 'Jueves', 5: 'Viernes', 6: 'Sabado',
                7: 'Domingo'}  # Domingo porque en virtuales pueden comenzar en Domingo D:
NOMBRES_MESES = {1: 'Enero',    2: 'Febrero',    3: 'Marzo',
                 4: 'Abril',    5: 'Mayo',       6: 'Junio',
                 7: 'Julio',    8: 'Agosto',     9: 'Septiembre',
                 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
CLAVE_DIAS = {0: 'dia_lu',
              1: 'dia_ma',
              2: 'dia_mi',
              3: 'dia_ju',
              4: 'dia_vi',
              5: 'dia_sa'}



def __rango_horas_hhmm(inicio: int, fin: int, paso: int, correcion: int = CORRECCION_RANGO_HORAS):
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
        Recibe hora en formato hhmm y retorna hh:mm f.f.
        Ejemplo: '0800'  ->  '8:00 a.m.'

        El formato siempre debe ser "hhmm" y caber en la medicion
        normal de la hora, en caso contrario no se acepta.
        correcto: 1555
        correcto: 0015
        correcto: 2359
        incorrecto: 66
        incorrecto: 1090
        incorrecto: 4515
        incorrecto: -1055
        """
        hora_entera = int(hora)
        try:
            hora_in_entera = int(hora[:MITAD_HORA_HHMM])
        except ValueError:
            hora_in_entera = 0
        try:
            hora_fin_entera = int(hora[MITAD_HORA_HHMM:])
        except ValueError:
            hora_fin_entera = 0
        para_restar = (DIFERENCIA_24H if hora_in_entera > DIFERENCIA_24H else 0)
    
        if hora_entera < INICO_DIA_HHMM:
            return None
        if hora_in_entera > HORAS_DIA:
            return None
        if hora_fin_entera > MINUTOS_HORA:
            return None
        if len(hora) != CANT_DIGS_HORA_HHMM: 
            return None
        if hora_entera >= HORAS_DIA_HHMM:  # Por si acaso las 12 se manejaran como 24 en lugar de 0
            hora_in_entera = INICO_DIA_HHMM
        if INICO_DIA_HHMM < hora_entera < MEDIO_DIA_HHMM:  # 12:00 a.m. - 12:59 a.m.
            hora_con_formato = f'{hora_in_entera:02d}:{hora_fin_entera:02d} {FORMATO_MATUTINO}'
        elif MEDIO_DIA_HHMM - 1 < hora_entera < FINAL_DIA_HMMM:  # 1:00 p.m - 11:59 a.m.
            hora_restada = hora_in_entera - para_restar
            hora_con_formato = f'{hora_restada:02d}:{hora_fin_entera:02d} {FORMATO_VESPERTINO}'
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
    return f'{SEP}'.join(mitades_formateadas)


def __procesar_rango_horas(inicio: str, final: str):
    """
    Recibe hora en formato hhmm-hhmm y retorna hh:mm f.f \\n hh:mm f.f.
    Ademas, genera un rango de 55 minutos por cada hora abarcada en
    el rango total recibido.

    Ejemplo: '1700-2055'  ->  ['5:00 p.m.\\n 5:55 p.m.', '6:00 p.m.\\n 6:55 p.m.',
    '7:00 p.m.\\n 7:55 p.m.', '8:00 p.m.\\n 8:55 p.m.']

    Ejemplo: '66'  ->  'Sin\\nhora'
    Ejemplo: '11'  ->  'Sin\\nhora'
    Ejemplo: '5065-4012'  ->  'Sin\\nhora'
    """
    mitades_de_hora = [inicio, final]
    rango_horas_clase = __rango_horas_hhmm(*map(int, mitades_de_hora), 100)
    rango_horas_de_clase_formateadas = []
    for horas_de_un_espacio in rango_horas_clase:
        horas_de_un_espacio_formateadas = __formatear_hora(horas_de_un_espacio)
        if horas_de_un_espacio_formateadas is None:
            rango_horas_de_clase_formateadas.append(MATERIA_SIN_HORARIO)
        else:
            rango_horas_de_clase_formateadas.append(horas_de_un_espacio_formateadas)
    rango_horas_de_clase_formateadas = tuple(rango_horas_de_clase_formateadas)

    return rango_horas_de_clase_formateadas


def __obtener_fecha_completa(fecha: str, separador: str):
        # Fechas en horario siiau son: dd-mm-aa
        dia, mes, year = tuple(map(int, fecha.split(separador)))
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
    datos_dia['rango_horas_hhmm'] =  __rango_horas_hhmm(int(hora_inicio), int(hora_final), paso=100)

    return datos_dia


def _procesar_dias_clase(datos_clase: dict, horario_por_columnas: HorarioCompletoSiiau, i_horario: int):
    hora_formato_siiau = horario_por_columnas.horario[i_horario].split('-')
    hora_inicio = hora_formato_siiau[HORA_INICIO_MATERIAS]
    hora_final = hora_formato_siiau[HORA_FINAL_MATERIAS]
    if horario_por_columnas.L[i_horario]:
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_lu'] = nuevo_dia
    else:
        datos_clase['dia_lu'] = None
    if horario_por_columnas.M[i_horario]:
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_ma'] = nuevo_dia
    else:
        datos_clase['dia_ma'] = None
    if horario_por_columnas.I[i_horario]:
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_mi'] = nuevo_dia
    else:
        datos_clase['dia_mi'] = None
    if horario_por_columnas.J[i_horario]:
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_ju'] = nuevo_dia
    else:
        datos_clase['dia_ju'] = None
    if horario_por_columnas.V[i_horario]:
        datos_dia = __procesar_un_dia(hora_inicio, hora_final, horario_por_columnas, i_horario)
        nuevo_dia = DiaClase(**datos_dia)
        datos_clase['dia_vi'] = nuevo_dia
    else:
        datos_clase['dia_vi'] = None
    if horario_por_columnas.S[i_horario]:
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
    datos_clase['fecha_inicio_completa'] = __obtener_fecha_completa(fecha_inicio, '-')
    datos_clase['fecha_final_completa'] = __obtener_fecha_completa(fecha_final, '-')

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
    clases = tuple(clases)
    
    return clases


def _agregar_horas_y_nombres(h_por_horas: dict,
                             dia: DiaClase,
                             nombre_clase: str,
                             edificio_clase: str,
                             aula_clase: str,
                             clave_clase: str,
                             seccion_clase: str,
                             nrc_clase,
                             i_dia):
    rango_horas_hmm = tuple(dia.rango_horas_hhmm)
    for i_hora_clase, hora_clase in enumerate(dia.rango_horas):
        # hora en formato 1555 en entero para ordenar las clases
        # de modo que arriba quede la hora menor (mas temprano)
        # y abajo la mayor (mas tarde)
        # 1000 : {'10:00 a.m.\\10:55 a.m.: ...}
        # 1100 : {'11:00 a.m.\\11:55 a.m.: ...}
        # . . .
        hora_entera_hhmm = int(rango_horas_hmm[i_hora_clase][MITAD_HORA_RANGO_HHMM])
        try:
            # METODOS MATEMATICOS  --> nombre
            # 
            # >DEDR-A001           --> edificio - aula
            # >I5896-D17           --> clave    - seccion
            # >57302-              --> nrc      -
            h_por_horas[hora_entera_hhmm][hora_clase][i_dia] = ''.join([
                nombre_clase, SEP, SEP, 
                INDIC_DAT_MAT, edificio_clase, SEP_DAT_MAT, aula_clase, SEP, 
                INDIC_DAT_MAT, clave_clase, SEP_DAT_MAT, seccion_clase, SEP, 
                INDIC_DAT_MAT, nrc_clase, SEP_DAT_MAT
                ])
        except KeyError:
            # Si no existe la fila de esa hora, agregarla
            nuevo_interno = dict()
            nuevo_interno[hora_clase] = ['', '', '', '', '', '']  # cada cadena vacia es un día
            h_por_horas[hora_entera_hhmm] = nuevo_interno
            h_por_horas[hora_entera_hhmm][hora_clase][i_dia] = ''.join([
                nombre_clase, SEP, SEP, 
                INDIC_DAT_MAT, edificio_clase, SEP_DAT_MAT, aula_clase, SEP, 
                INDIC_DAT_MAT, clave_clase, SEP_DAT_MAT, seccion_clase, SEP, 
                INDIC_DAT_MAT, nrc_clase, SEP_DAT_MAT
                ])
    

def compactar_horario_por_clases(clases):

    horario_por_horas = dict()

    for clase in clases:
        if clase.dia_lu is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_lu,
                                     clase.nombre,
                                     clase.dia_lu.edificio,
                                     clase.dia_lu.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_LUNES)
        if clase.dia_ma is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_ma,
                                     clase.nombre,
                                     clase.dia_ma.edificio,
                                     clase.dia_ma.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_MARTES)
        if clase.dia_mi is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_mi,
                                     clase.nombre,
                                     clase.dia_mi.edificio,
                                     clase.dia_mi.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_MIERCOES)
        if clase.dia_ju is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_ju,
                                     clase.nombre,
                                     clase.dia_ju.edificio,
                                     clase.dia_ju.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_JUEVES)
        if clase.dia_vi is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_vi,
                                     clase.nombre,
                                     clase.dia_vi.edificio,
                                     clase.dia_vi.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_VIERNES)
        if clase.dia_sa is not None:
            _agregar_horas_y_nombres(horario_por_horas,
                                     clase.dia_sa,
                                     clase.nombre,
                                     clase.dia_sa.edificio,
                                     clase.dia_sa.aula,
                                     clase.clave_materia,
                                     clase.seccion,
                                     clase.nrc,
                                     I_SABADO)

    horario_por_horas_ordenado = dict(sorted(horario_por_horas.items()))
    horas = [list(fila.keys()) for h_entera, fila in horario_por_horas_ordenado.items()]
    horas = aplanar_lista(horas)
    clases_compactas_por_filas = map(lambda x: aplanar_lista(list(x.values())), list(horario_por_horas_ordenado.values()))
    clases_compactas_por_columna = list(zip(*clases_compactas_por_filas))
    horario_compactado = HorarioCompacto(horas, *clases_compactas_por_columna)

    return horario_compactado


if __name__ == '__main__':
    print('Esto no deberia mostrarse. Ejecutando desde horario_siiau_service.')


















