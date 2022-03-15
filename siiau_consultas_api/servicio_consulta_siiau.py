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



from .utiles import limpiar_html, particionar, convertir_ciclo_a_entero, aplanar_lista
from .esquemas import (DatosHorarioSiiau, DatosSesion, HorarioCompletoSiiau, CarreraEstudiante,
                            ClaseCompleta, CarreraCompleta, ClaseOferta, HorarioOferta, ProfesorOferta,
                            CentroCompleto, DiasHorarioOferta, CicloCompleto)

import requests.exceptions
from typing import NamedTuple, Tuple, List, Union
from bs4 import BeautifulSoup as WebSp
from requests import request, Session
import re

VACIO = '\xa0'
RETORNO = '\n'
DIA_VACIO_HORARIO_OFERTA = '.'

URL_SIIAU_ESTUDIANTE = 'http://siiauescolar.siiau.udg.mx'
URL_CONSULTA_SIIAU = 'http://consulta.siiau.udg.mx'

I_REF_CARRERA = 0
I_NOM_CARRERA = 1
I_ID_CENTRO = 0
I_NOM_CENTRO = 1
I_REF_CICLO = 0
I_NOM_CICLO = 1
ANCHO_TABLA_CARRERAS = 2
INICIO_TABLA_MATERIAS = 1  # En el 0 está el nombre de la carrera
RANGO_SUBCLAVE_MATERIAS = slice(0, 2)
TITULO_MATERIA_COMPLETA = 0
I_CICLO_INICIO_MATERIA = 8
I_AREA_MATERIA = 0
RANGO_DEPS_CARRS_CENTROS = slice(13, 16)
ANCHO_TABLA_HORARIO = 17
ESP_FAL_SUB_CLASE = 4
I_REF_CARRERA_ESTUDIANTE = 0  # Esta es en las carreras registradas del estudiante
RANGO_CICLO_IN_CARR_ES = slice(1, 3)
I_HORARIO_MATERIA_OFERTA = 8
I_PROFESORES_MATERIA_OFERTA = 7
ANCHO_TABLA_PROFES_OFERTA = 2
I_DIAS_HORARIOS_OFERTA = 2
RANGO_DIAS_HORARIO_COLUMNAS = slice(6, 12)


class RefererSession(Session):
    def rebuild_auth(self, prepared_request, response):
        super().rebuild_auth(prepared_request, response)
        prepared_request.headers['Referer'] = response.url


def __convertir_a_identificador_valido(valor: str) -> str:
    valor = valor.split(' ')
    valor = '_'.join(valor).encode('ascii', errors='ignore').decode().lower()
    valor = re.sub('[\W_]+', '', valor)
    return valor


def __join_payload_url(url: str, payload: dict):
    payload_string = ''
    for llave, valor in payload.items():
        nuevo_valor = '='.join([llave, f'{valor}'])
        if payload_string == '':
            payload_string = nuevo_valor
        else:
            payload_string = '&'.join([payload_string, nuevo_valor])

    nueva_url = '?'.join([url, payload_string])

    return nueva_url


def __websp_findall(response, **findall):
    """
    param name: A filter on tag name.
    param attrs: A dictionary of filters on attribute values.
    param recursive: If this is True, find_all() will perform a
        recursive search of this PageElement's children. Otherwise,
        only the direct children will be considered.
    param limit: Stop looking after finding this many results.
    kwargs: A dictionary of filters on attribute values.
    return: A ResultSet of PageElements.
    rtype: bs4.element.ResultSet
    """
    return WebSp(response.text, 'html.parser').find_all(**findall)


def __preparar_para_busqueda(cadena: str) -> str:
    """
    Prepara una cadena para buscar coincidencias convirtiéndola
    a minúscula toda, borrando espacios.

    "Una cadena de texto" => "unacadenadetexto"
    """
    sin_espacios = ''.join(cadena.split(' '))
    minusculas = sin_espacios.lower()

    return minusculas


def horario(pidm_p: str, ciclo: str, carrera: str, cookies: str) -> DatosHorarioSiiau:
    url_horario = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/sfpcoal.horario'])
    payload = dict(pidmP=pidm_p,
                   cicloP=ciclo,
                   majrP=carrera,
                   encaP='0')
    headers = {'Content-Type': 'text/html; charset=ISO-8859-1',
               'Cookie': cookies}
    resp = request('POST',
                   url_horario,
                   headers=headers,
                   data=payload)

    encabezados = __websp_findall(resp, name='th')
    tablas = __websp_findall(resp, name='td')
    encabezados = list(map(limpiar_html, encabezados))
    tablas = list(map(limpiar_html, tablas))
    inicio_dat_es = encabezados.index('DATOS DEL ESTUDIANTE') + 1
    inicio_enc_hor = 0
    for enc in encabezados:
        busqueda = enc.find('Horario de cursos del ciclo')
        if busqueda > -1:
            inicio_enc_hor = encabezados.index(enc) + 1
    if inicio_enc_hor == 0:
        raise IndexError
    encabezados_datos_estudiantes = tuple(encabezados[inicio_dat_es:inicio_enc_hor - 1])
    encabezados_datos_estudiantes = tuple(map(__convertir_a_identificador_valido, encabezados_datos_estudiantes))
    encabezados_horario = tuple(encabezados[inicio_enc_hor:])
    encabezados_horario = tuple(map(__convertir_a_identificador_valido, encabezados_horario))
    tabla_datos_estudiantes = tuple(tablas[:len(encabezados_datos_estudiantes)])
    tabla_horario = tablas[len(encabezados_datos_estudiantes):]

    # Correccion a las filas extra de las clases, que es la misma clase con otro dia u hora,
    # pero, al no tener los datos hasta la hora, en lugar de tener TODOS los espacios vacíos
    # que debería, solo tiene 1. Con esto se agregan los espacios vacíos que deberían estar.
    tabla_horario_corregida = []
    buscador_de_fechas = re.compile('[0-3][0-9]-[0-1][0-9]-[\d][\d][\d][\d]')
    contador_fechas = 0
    for i_dato, dato in enumerate(tabla_horario):
        if re.match(buscador_de_fechas, dato) is not None:
            contador_fechas += 1
        elif contador_fechas == 2:
            contador_fechas = 0
            if dato == '':
                [tabla_horario_corregida.append('') for _ in range(ESP_FAL_SUB_CLASE)]
        tabla_horario_corregida.append(dato)
    tabla_horario_corregida = particionar(tabla_horario_corregida, len(encabezados_horario))
    tabla_horario_corregida = list(zip(*tabla_horario_corregida))  # Se convierte a columnas

    for i_columna, columna in enumerate(tabla_horario_corregida[RANGO_DIAS_HORARIO_COLUMNAS]):
        i_columna_nueva = RANGO_DIAS_HORARIO_COLUMNAS.start + i_columna
        nueva_columna_de_dias = tuple([False if dia == '' else True for dia in columna])
        tabla_horario_corregida[i_columna_nueva] = nueva_columna_de_dias

    campos_tabla_datos_estudiante = ((encabezado, str) for encabezado in encabezados_datos_estudiantes)
    tabla_dat_es_clase = NamedTuple('DatosEstudiante', campos_tabla_datos_estudiante)
    tabla_datos_estudiantes_completa = tabla_dat_es_clase(*tabla_datos_estudiantes)
    tabla_horario_completa = HorarioCompletoSiiau(*tabla_horario_corregida)
    datos_horarios_siiau = DatosHorarioSiiau(tabla_datos_estudiantes_completa, tabla_horario_completa)

    return datos_horarios_siiau

# FIX no siempre hay opciones con las carreras del estudiante
def carrera_s_estudiante(pidm_p, cookies) -> Tuple[CarreraEstudiante]:
    url_carrera = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/gupmenug.menu'])
    payload = dict(p_sistema_c='ALUMNOS',
                   p_sistemaid_n='3',
                   p_menupredid_n='3',
                   p_pidm_n=pidm_p,
                   p_majr_c=pidm_p)
    accept = ['text / html, application / xhtml + xml, application / xml',
              'q = 0.9, image / avif, image / webp, image / apng, * / *',
              'q = 0.8, application / signed - exchange', 'v = b3', 'q = 0.9']
    headers = {'Accept': ';'.join(accept),
               'Accept-Encoding': 'gzip,deflate',
               'Accept-Language': 'es-419,es;q=0.9',
               'Connection': 'keep-alive',
               'Cookie': cookies,
               'Host': 'siiauescolar.siiau.udg.mx',
               'Referer': f'{url_carrera}_sistema?p_pidm_n={pidm_p}',
               'Upgrade-Insecure-Requests': '1'}
    url_carrera = __join_payload_url(url_carrera, payload)
    resp = request('GET',
                   url=url_carrera,
                   headers=headers,
                   data=payload,
                   allow_redirects=True)
    carreras_opciones = __websp_findall(resp, name='option')
    carreras_opciones = list(map(limpiar_html, carreras_opciones))
    carreras = carreras_opciones[0].split('\n')
    carreras.remove('')
    carreras_separadas = list(map(lambda x: x.split('-'), carreras))
    carreras_formateadas = tuple(
        map(lambda x: CarreraEstudiante(x[I_REF_CARRERA_ESTUDIANTE],
                                        ''.join(x[RANGO_CICLO_IN_CARR_ES]),
                                        convertir_ciclo_a_entero(''.join(x[RANGO_CICLO_IN_CARR_ES]))),
            carreras_separadas)
    )

    return carreras_formateadas


def oferta_academica(centro, ciclo, materia, con_cupos=False):
    url_oferta = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/sspseca.consulta_oferta'])
    payload = dict(ciclop=ciclo,
                   cup=centro,
                   majrp='',
                   crsep=materia,
                   materiap='',
                   horaip='',
                   horafp='',
                   edifp='',
                   aulap='',
                   ordenp='0',
                   mostrarp=f'100000')
    resp = request('POST',
                   url_oferta,
                   data=payload)
    tabla_oferta_html = WebSp(resp.content, 'html.parser')

    materias_crudas = tabla_oferta_html.select('td.tddatos')
    materias_limpias = list(map(lambda x: limpiar_html(x).replace(RETORNO*2, RETORNO).splitlines(keepends=False), materias_crudas))
    for i_trozo in range(len(materias_limpias)):
        while '' in materias_limpias[i_trozo]:
            materias_limpias[i_trozo].remove('')

    # cuenta las columnas con más de 1 elemento, pues en las materias solo hay 1 por fila (profesores)
    conteo_filas = sum(list(map(lambda columna: 1 if len(columna) > 1 else 0, materias_limpias)))

    tam_filas = int(len(materias_limpias) / conteo_filas)
    materias_particionadas = particionar(materias_limpias, tam_filas, retornar_tuplas=False)
    for i_fila, fila in enumerate(materias_particionadas):
        puros_profes = materias_particionadas[i_fila].pop(I_PROFESORES_MATERIA_OFERTA)
        profes_particionados = particionar(puros_profes, ANCHO_TABLA_PROFES_OFERTA)
        nueva_lista_profes = []
        for profe in profes_particionados:
            nueva_lista_profes.append(ProfesorOferta(*profe))
        materias_particionadas[i_fila] = aplanar_lista(fila)
        materias_particionadas[i_fila].insert(I_PROFESORES_MATERIA_OFERTA, tuple(nueva_lista_profes))

    horarios_crudos = tabla_oferta_html.select('table.td1')
    horarios_limpios = []
    for fila in horarios_crudos:
        lista_fila = []
        for sub_fila in fila:
            lista_sub_fila = []
            for sub_columna in sub_fila:
                sub_columna_limpia = limpiar_html(sub_columna)
                if sub_columna_limpia == VACIO:  # \xa0 aparece cuando es una celda vacia
                    sub_columna_limpia = ' '
                if sub_columna_limpia != RETORNO:
                    lista_sub_fila.append(sub_columna_limpia)
            if len(lista_sub_fila) > 0:
                lista_fila.append(lista_sub_fila)
        horarios_limpios.append(lista_fila)

    for i_fila, fila in enumerate(horarios_limpios):
        for i_sub_fila, sub_fila in enumerate(fila):
            dias = sub_fila[I_DIAS_HORARIOS_OFERTA].split(' ')
            nuevos_dias = []
            for dia in dias:
                if dia == DIA_VACIO_HORARIO_OFERTA:
                    nuevos_dias.append(False)
                else:
                    nuevos_dias.append(True)
            horarios_limpios[i_fila][i_sub_fila][I_DIAS_HORARIOS_OFERTA] = DiasHorarioOferta(*nuevos_dias)
            horarios_limpios[i_fila][i_sub_fila] = HorarioOferta(*sub_fila)

    for i_fila, fila in enumerate(materias_particionadas):
        horarios_correspondientes = tuple(horarios_limpios[i_fila])
        materias_particionadas[i_fila].insert(I_HORARIO_MATERIA_OFERTA, horarios_correspondientes)
        materias_particionadas[i_fila] = ClaseOferta(*fila)

    return tuple(materias_particionadas)


def ciclos() -> Tuple[CicloCompleto]:
    url_ciclos = ''.join([URL_CONSULTA_SIIAU, '/wal/sgpofer.secciones'])
    payload = dict(pidmp='',
                   majrp='')
    url_ciclos = __join_payload_url(url_ciclos, payload)
    resp = request('GET',
                   url=url_ciclos,
                   data=payload)
    ciclos_opciones = __websp_findall(resp, name='select', attrs=dict(id='cicloID'))
    ciclos_opciones = list(map(limpiar_html, ciclos_opciones))[0].split('\n')
    ciclos_opciones_limpios = list(map(lambda cic: cic.split(' - '), ciclos_opciones))
    while [''] in ciclos_opciones_limpios:
        ciclos_opciones_limpios.remove([''])
    ciclos_completos = tuple(map(lambda partido: CicloCompleto(*partido), ciclos_opciones_limpios))

    return ciclos_completos


def ciclos_por_busqueda(busqueda: str) -> Tuple[CicloCompleto]:
    todos_los_ciclos = ciclos()
    encontrados: List[CicloCompleto] = []
    patron = __preparar_para_busqueda(busqueda)
    for ciclo_sondeado in todos_los_ciclos:
        ref = __preparar_para_busqueda(ciclo_sondeado.ref_ciclo)
        nom = __preparar_para_busqueda(ciclo_sondeado.nombre_completo)
        busqeda_ref = ref.find(patron)
        busqueda_nom = nom.find(patron)
        if busqeda_ref > -1 or busqueda_nom > -1:
            encontrados.append(ciclo_sondeado)
    empacados = tuple(encontrados)

    return empacados


def centros() -> Tuple[CentroCompleto]:
    url_centros = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/sgpofer.secciones'])
    payload = dict(pidmp='',
                   majrp='')
    url_centros = __join_payload_url(url_centros, payload)
    resp = request('GET',
                   url=url_centros,
                   data=payload)
    centros_opciones = __websp_findall(resp, name='select', attrs={'name': 'cup'})
    centros_opciones = tuple(map(limpiar_html, centros_opciones))[0].split('\n')
    while '' in centros_opciones:
        centros_opciones.remove('')
    centros_obtenidos = tuple(map(lambda cen_opc: CentroCompleto(*cen_opc.split(' - ')), centros_opciones))

    return centros_obtenidos


def carreras(centro_cup_id: str) -> Tuple[CarreraCompleta]:
    """
    Recibe el parameter 'cup', que para siiau es el id de los
    centros universitarios. Con esto se pueden consultar
    todas las carreras de ese mismo centro
    """
    url_carreras = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/sspseca.lista_carreras'])
    payload = dict(cup=centro_cup_id)
    url_carreras = __join_payload_url(url_carreras, payload)
    resp = request('GET',
                   url=url_carreras,
                   data=payload)
    lista_referencias = __websp_findall(resp, name='a')
    lista_carreras = __websp_findall(resp, name='td')
    lista_referencias = tuple(map(limpiar_html, lista_referencias))
    lista_carreras = tuple(map(limpiar_html, lista_carreras))
    lista_carreras_completa = particionar(lista_carreras, ANCHO_TABLA_CARRERAS)
    for carrera_c in lista_carreras_completa:
        if carrera_c[I_REF_CARRERA] not in lista_referencias:
            lista_carreras_completa.remove(carrera_c)
    carreras_procesadas = tuple(map(lambda carr_c: CarreraCompleta(*carr_c), lista_carreras_completa))

    return carreras_procesadas


def __obtener_materia_completa(area, clave_materia, ciclo_inicio='') -> Union[Tuple[ClaseCompleta], Union[list, any]]:
    url_materia_completa = ''.join([URL_CONSULTA_SIIAU, '/wco/scpcata.detmate'])
    subclave = ','.join([area, clave_materia, ciclo_inicio])
    payload = dict(subclavep=subclave,
                   pEntra='OAP')  # TODO Encontrar qué es esto
    url_materia_completa = __join_payload_url(url_materia_completa, payload)
    resp = request('GET',
                   url=url_materia_completa,
                   data=payload)
    tabla_materia_completa = __websp_findall(resp, name='td')
    encabezados = __websp_findall(resp, name='th')
    encabezados = list(map(limpiar_html, encabezados))
    titulo = encabezados.pop(TITULO_MATERIA_COMPLETA)
    tabla_materia_completa = list(map(limpiar_html, tabla_materia_completa))[:len(encabezados)]

    if tabla_materia_completa[I_AREA_MATERIA] == '':
        ciclo_inicio = tabla_materia_completa[I_CICLO_INICIO_MATERIA]
        _, tabla_materia_completa = __obtener_materia_completa(area, clave_materia, ciclo_inicio)
    else:
        tabla_materia_completa.insert(TITULO_MATERIA_COMPLETA, titulo)

    return ClaseCompleta(*tabla_materia_completa), tabla_materia_completa



def materias(self, id_carrera: str) -> Tuple[ClaseCompleta]:
    url_catalogo_materias = ''.join([URL_CONSULTA_SIIAU, '/wco/scpcata.cataxcarr'])
    payload = dict(carrerap=id_carrera,
                   ordenp=1,
                   mostrarp=5,
                   tipop='T')
    url_catalogo_materias = __join_payload_url(url_catalogo_materias, payload)
    resp = request('GET',
                   url=url_catalogo_materias,
                   data=payload)
    tabla_materias = __websp_findall(resp, name='td')
    encabezados = __websp_findall(resp, name='th')
    tabla_materias = list(map(limpiar_html, tabla_materias))[INICIO_TABLA_MATERIAS:]
    encabezados = list(map(limpiar_html, encabezados))[INICIO_TABLA_MATERIAS:]
    ancho_tabla = len(encabezados)
    tabla_materias = particionar(tabla_materias, ancho_tabla)

    materias_completas = []
    for renglon_materia in tabla_materias:
        if None not in renglon_materia:  # Ultimo renglón tiene "(c) 2002 Universidad de Guadalajara ..."
            materia_completa: ClaseCompleta
            materia_completa, _ = self._obtener_materia_completa(*renglon_materia[RANGO_SUBCLAVE_MATERIAS])
            materias_completas.append(materia_completa)

    return tuple(materias_completas)


def __obtener_cookies(resp_inicio) -> str:
    masa = resp_inicio.cookies.get_dict()
    horneado = [f'{nom}={val}' for nom, val in masa.items()]
    cookies = ';'.join(horneado)

    return cookies


def __obtener_pidm_p(resp_inicio) -> int:
    bienvenida = __websp_findall(resp_inicio, name='input')
    for val in bienvenida:
        if 'p_pidm_n' in str(val):
            bienvenida = str(val)
            break
    limpiador = re.compile('[^\d]+')
    pidm_p = int(re.sub(limpiador, '', str(bienvenida)))

    return pidm_p


def obtener_sesion(codigo, clave, carrera, ciclo):
    url_inicio = ''.join([URL_SIIAU_ESTUDIANTE, '/wus/gupprincipal.valida_inicio'])
    data = dict(p_codigo_c=codigo,
                p_clave_c=clave)
    try:
        resp_inicio = request('POST',
                              url_inicio,
                              headers={},
                              files=[],
                              data=data)
        return DatosSesion(cookies=__obtener_cookies(resp_inicio),
                           pidmp=__obtener_pidm_p(resp_inicio),
                           carrera=carrera,
                           ciclo=ciclo)
    except requests.exceptions.ConnectionError:
        raise ConnectionError('No se pudo iniciar sesion en siiau')


class Siiau:

    def __init__(self, codigo, clave, carrera, ciclo):
        self.sesion: DatosSesion = obtener_sesion(codigo, clave, carrera, ciclo)

    def horario(self) -> DatosHorarioSiiau:
        cookies, pidm_p, ciclo, carrera = self.sesion
        return horario(pidm_p, ciclo, carrera, cookies)

    def carreras(self) -> Tuple[CarreraEstudiante]:
        cookies, pidm_p, _, __ = self.sesion
        return carrera_s_estudiante(pidm_p, cookies)

    def oferta(self, centro='', ciclo='', materia='', con_cupos=False) -> Tuple[ClaseOferta]:
        if ciclo == '':
            ciclo = self.sesion.ciclo
        return oferta_academica(centro, ciclo, materia, con_cupos)


if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando consulta_siiau_service.')

