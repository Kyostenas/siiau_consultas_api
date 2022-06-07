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



from .utiles import (
    limpiar_html, 
    particionar, 
    convertir_ciclo_a_entero, 
    aplanar_lista
)
from .esquemas import (
    DatosHorarioSiiau, 
    DatosSesion, 
    HorarioCompletoSiiau, 
    CarreraEstudiante,
    ClaseCompleta, 
    CarreraCompleta, 
    ClaseOferta, 
    HorarioOferta, 
    ProfesorOferta,
    CentroCompleto, 
    DiasHorarioOferta, 
    CicloCompleto
)

import requests.exceptions
from typing import NamedTuple, Tuple, List, Union
from bs4 import BeautifulSoup as WebSp
from requests import head, request, Session
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
INICIO_TABLA_CLASES = 1  # En el 0 está el nombre de la carrera
RANGO_SUBCLAVE_CLASES = slice(0, 2)
TITULO_CLASE_COMPLETA = 0
I_CICLO_INICIO_CLASE = 8
I_AREA_CLASE = 0
RANGO_DEPS_CARRS_CENTROS = slice(13, 16)
ANCHO_TABLA_HORARIO = 17
ESP_FAL_SUB_CLASE = 4
I_REF_CARRERA_ESTUDIANTE = 0  # Esta es en las carreras registradas del estudiante
RANGO_CICLO_IN_CARR_ES = slice(1, 3)
I_HORARIO_CLASE_OFERTA = 8
I_PROFESORES_CLASE_OFERTA = 7
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
    try:
        tabla_horario_completa = HorarioCompletoSiiau(*tabla_horario_corregida)
    except TypeError:
        tabla_horario_completa = ()
    datos_horarios_siiau = DatosHorarioSiiau(tabla_datos_estudiantes_completa, tabla_horario_completa)

    return datos_horarios_siiau


def __obtener_multicarrera(pidm_p, cookies) -> list:
    url_carrera = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/gupmenug.menu'])
    payload = dict(
        p_sistema_c='ALUMNOS',
        p_sistemaid_n='3',
        p_menupredid_n='3',
        p_pidm_n=pidm_p,
        p_majr_c=pidm_p
    )
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
    resp = request(
        'GET',
        url=url_carrera,
        headers=headers,
        data=payload,
        allow_redirects=True
    )
    carreras_opciones = __websp_findall(resp, name='option')
    carreras_opciones = list(map(limpiar_html, carreras_opciones))
    
    return carreras_opciones


def __obtener_ultimo_ciclo_de_carrera(pidm_p, cookies, ciclo, carrera) -> str:
    """
    Retorna::
    
        {'ultimo_ciclo': str, 'ultimo_ciclo_entero': str}
    """
    datos_horario: DatosHorarioSiiau = horario(
        pidm_p=pidm_p,
        ciclo=ciclo,
        carrera=carrera,
        cookies=cookies
    )
    datos_carrera = datos_horario.datos_estudiante
    ultimo_ciclo = datos_carrera.ltimociclo
    ultimo_ciclo_entero = convertir_ciclo_a_entero(ultimo_ciclo)
    
    return {'ultimo_ciclo': ultimo_ciclo, 'ultimo_ciclo_entero': ultimo_ciclo_entero}
    
    
def __obtener_una_carrera(pidm_p, cookies) -> CarreraEstudiante:
    url_carrera_individual = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/SGPPROC.DOBLE_CARRERA'])
    paylad = dict(
        pForma='SGPHIST.BOLETA_DC',
        pParametroPidmAlumno='pidmp',
        pPidmAlumno=pidm_p,
        pParametroCarrera='majrP',
        pParametroCicloAdmision='cicloaP'
    )
    headers = {
        'Content-Type': 'text/html; charset=ISO-8859-1',
        'Cookie': cookies
    }
    url_carrera_individual = __join_payload_url(url_carrera_individual, paylad)
    resp = request(
        'GET',
        url=url_carrera_individual,
        headers=headers,
        data=paylad
    )
    datos_carrera = __websp_findall(resp, name='input')
    datos_filtrados = {}
    for etiqueta_html in datos_carrera:
        if etiqueta_html.attrs['name'] == 'majrP':
            datos_filtrados['ref_carrera'] = etiqueta_html.attrs['value']
        if etiqueta_html.attrs['name'] == 'cicloaP':
            datos_filtrados['ciclo_admision'] = etiqueta_html.attrs['value']
    datos_ultimo_ciclo = __obtener_ultimo_ciclo_de_carrera(
        pidm_p=pidm_p,
        cookies=cookies,
        ciclo=datos_filtrados['ciclo_admision'],
        carrera=datos_filtrados['ref_carrera']
    )
    ciclo_final = datos_ultimo_ciclo['ultimo_ciclo']
    ref_ciclo_final = datos_ultimo_ciclo['ultimo_ciclo_entero']
    carrera_formateada = CarreraEstudiante(
        ref_carrera=datos_filtrados['ref_carrera'],
        ciclo_inicio='',
        ref_ciclo_inicio=datos_filtrados['ciclo_admision'],
        ciclo_final=ciclo_final,
        ref_ciclo_final=ref_ciclo_final
    )
    return carrera_formateada


# FIX no siempre hay opciones con las carreras del estudiante
def carrera_s_estudiante(pidm_p, cookies) -> Tuple[CarreraEstudiante]:
    carreras_opciones = __obtener_multicarrera(pidm_p, cookies)
    if len(carreras_opciones) != 0:
        carreras = carreras_opciones[0].split('\n')
        carreras.remove('')
        carreras_separadas = list(map(lambda x: x.split('-'), carreras))
        carreras_formateadas = []
        for carrera in carreras_separadas:
            ref_carrera = carrera[I_REF_CARRERA_ESTUDIANTE]
            ref_ciclo_inicio = convertir_ciclo_a_entero(
                ''.join(carrera[RANGO_CICLO_IN_CARR_ES])
            )
            datos_ultimo_ciclo = __obtener_ultimo_ciclo_de_carrera(
                pidm_p=pidm_p,
                cookies=cookies,
                ciclo=ref_ciclo_inicio,
                carrera=ref_carrera
            )
            ciclo_final = datos_ultimo_ciclo['ultimo_ciclo']
            ref_ciclo_final = datos_ultimo_ciclo['ultimo_ciclo_entero']
            carrera_formateada = CarreraEstudiante(
                ref_carrera=ref_carrera,
                ciclo_inicio=''.join(carrera[RANGO_CICLO_IN_CARR_ES]),
                ref_ciclo_inicio=ref_ciclo_inicio,
                ciclo_final=ciclo_final,
                ref_ciclo_final=ref_ciclo_final
            )
            carreras_formateadas.append(carrera_formateada)
        return carreras_formateadas
    else:
        una_carrera = tuple([__obtener_una_carrera(pidm_p, cookies)])
        return una_carrera


def oferta_academica(centro, ciclo, clase, con_cupos=False):
    url_oferta = ''.join([URL_SIIAU_ESTUDIANTE, '/wal/sspseca.consulta_oferta'])
    payload = dict(ciclop=ciclo,
                   cup=centro,
                   majrp='',
                   crsep=clase,
                   clasep='',
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

    clases_crudas = tabla_oferta_html.select('td.tddatos')
    clases_limpias = list(map(lambda x: limpiar_html(x).replace(RETORNO*2, RETORNO).splitlines(keepends=False), clases_crudas))
    for i_trozo in range(len(clases_limpias)):
        while '' in clases_limpias[i_trozo]:
            clases_limpias[i_trozo].remove('')

    # cuenta las columnas con más de 1 elemento, pues en las clases solo hay 1 por fila (profesores)
    conteo_filas = sum(list(map(lambda columna: 1 if len(columna) > 1 else 0, clases_limpias)))

    tam_filas = int(len(clases_limpias) / conteo_filas)
    clases_particionadas = particionar(clases_limpias, tam_filas, retornar_tuplas=False)
    for i_fila, fila in enumerate(clases_particionadas):
        puros_profes = clases_particionadas[i_fila].pop(I_PROFESORES_CLASE_OFERTA)
        profes_particionados = particionar(puros_profes, ANCHO_TABLA_PROFES_OFERTA)
        nueva_lista_profes = []
        for profe in profes_particionados:
            nueva_lista_profes.append(ProfesorOferta(*profe))
        clases_particionadas[i_fila] = aplanar_lista(fila)
        clases_particionadas[i_fila].insert(I_PROFESORES_CLASE_OFERTA, tuple(nueva_lista_profes))

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

    for i_fila, fila in enumerate(clases_particionadas):
        horarios_correspondientes = tuple(horarios_limpios[i_fila])
        clases_particionadas[i_fila].insert(I_HORARIO_CLASE_OFERTA, horarios_correspondientes)
        clases_particionadas[i_fila] = ClaseOferta(*fila)

    return tuple(clases_particionadas)


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


def grupo_de_clases(id_carrera: str, claves_materias: List[str]):
    print(claves_materias)
    tabla_clases = __tabla_clases(id_carrera)
    clases_completas = []
    prog_compl = 0
    mat_compl = 0
    clases_total = len(claves_materias)
    progreso_total = clases_total + (11 * clases_total)
    ignorar = False
    for renglon_clase in tabla_clases:
        # Ultimo renglón tiene "(c) 2002 Universidad de Guadalajara ..."
        if None in renglon_clase:
            continue
        for i in claves_materias:
            if i not in renglon_clase:
                if ignorar is False:
                    ignorar = True
        if ignorar:
            continue
        else:
            try:
                progreso = __obtener_clase_completa(*renglon_clase[RANGO_SUBCLAVE_CLASES])
                for paso, total_mat_com, clase_obtenida, _ in progreso:
                    ref_elemento_clase = None
                    if clase_obtenida != None:
                        clase_completa = clase_obtenida
                        ref_elemento_clase =  f'{clase_completa.clave} {clase_completa.titulo}'
                    prog_compl += 1
                    yield (
                        prog_compl, 
                        progreso_total, 
                        None, 
                        ref_elemento_clase, 
                        mat_compl, 
                        clases_total
                    )
            except:
                prog_compl += 1
                mat_compl += 1
                yield prog_compl, progreso_total, False, None, mat_compl, clases_total
            clases_completas.append(clase_completa)
            prog_compl += 1
            mat_compl += 1
            yield prog_compl, progreso_total, None, None, mat_compl, clases_total
    else:
        exit()
        yield (
            prog_compl, 
            progreso_total,
            tuple(clases_completas), 
            None, 
            mat_compl, 
            clases_total
        )


def __tabla_clases(id_carrera):
    url_catalogo_clases = ''.join([URL_CONSULTA_SIIAU, '/wco/scpcata.cataxcarr'])
    payload = dict(carrerap=id_carrera,
                   ordenp=1,
                   mostrarp=5,
                   tipop='T')
    url_catalogo_clases = __join_payload_url(url_catalogo_clases, payload)
    resp = request('GET',
                   url=url_catalogo_clases,
                   data=payload)
    tabla_clases = __websp_findall(resp, name='td')
    encabezados = __websp_findall(resp, name='th')
    tabla_clases = list(map(limpiar_html, tabla_clases))[INICIO_TABLA_CLASES:]
    encabezados = list(map(limpiar_html, encabezados))[INICIO_TABLA_CLASES:]
    ancho_tabla = len(encabezados)
    tabla_clases = particionar(tabla_clases, ancho_tabla)

    return tabla_clases


def __obtener_clase_completa(area, clave_clase, ciclo_inicio=''):
    url_clase_completa = ''.join([URL_CONSULTA_SIIAU, '/wco/scpcata.detmate'])
    yield 1, 11, None, None
    subclave = ','.join([area, clave_clase, ciclo_inicio])
    yield 2, 11, None, None
    payload = dict(subclavep=subclave,
                   pEntra='OAP')  # TODO Encontrar qué es esto
    yield 3, 11, None, None
    url_clase_completa = __join_payload_url(url_clase_completa, payload)
    resp = request('GET',
                   url=url_clase_completa,
                   data=payload)
    yield 4, 11, None, None
    tabla_clase_completa = __websp_findall(resp, name='td')
    yield 5, 11, None, None
    encabezados = __websp_findall(resp, name='th')
    yield 6, 11, None, None
    encabezados = list(map(limpiar_html, encabezados))
    yield 7, 11, None, None
    titulo = encabezados.pop(TITULO_CLASE_COMPLETA)
    yield 8, 11, None, None
    tabla_clase_completa = list(map(limpiar_html, tabla_clase_completa))[:len(encabezados)]
    yield 9, 11, None, None

    if tabla_clase_completa[I_AREA_CLASE] == '':
        ciclo_inicio = tabla_clase_completa[I_CICLO_INICIO_CLASE]
        progreso = __obtener_clase_completa(area, clave_clase, ciclo_inicio)
        for paso, total, _, tabla in progreso:
            if tabla != None:
                tabla_clase_completa = tabla
    else:
        tabla_clase_completa.insert(TITULO_CLASE_COMPLETA, titulo)
    yield 10, 11, None, None
    yield 11, 11, ClaseCompleta(*tabla_clase_completa), tabla_clase_completa



def clases(id_carrera: str):
    tabla_clases = __tabla_clases(id_carrera)
    clases_completas = []
    prog_compl = 0
    mat_compl = 0
    nones = [1 for renglon_clase in tabla_clases if None in renglon_clase]
    nones = sum(nones)
    clases_total = (len(tabla_clases) - nones)
    progreso_total = clases_total + (11 * clases_total)
    for renglon_clase in tabla_clases:
        if None not in renglon_clase:  # Ultimo renglón tiene "(c) 2002 Universidad de Guadalajara ..."
            progreso = __obtener_clase_completa(*renglon_clase[RANGO_SUBCLAVE_CLASES])
            for paso, total_mat_com, clase_obtenida, _ in progreso:
                ref_elemento_clase = None
                if clase_obtenida != None:
                    clase_completa = clase_obtenida
                    ref_elemento_clase =  f'{clase_completa.clave} {clase_completa.titulo}'
                prog_compl += 1
                yield prog_compl, progreso_total, None, ref_elemento_clase, mat_compl, clases_total
            clases_completas.append(clase_completa)
            prog_compl += 1
            mat_compl += 1
            yield prog_compl, progreso_total, None, None, mat_compl, clases_total
    else:
        yield prog_compl, progreso_total, tuple(clases_completas), None, mat_compl, clases_total


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


class Alumno:

    def __init__(self, codigo='', clave='', carrera='', ciclo='', sesion=None):
        if sesion is None:
            self.sesion: DatosSesion = obtener_sesion(codigo, clave, carrera, ciclo)
        else:
            self.sesion: DatosSesion = sesion

    def horario(self) -> DatosHorarioSiiau:
        cookies, pidm_p, ciclo, carrera = self.sesion
        return horario(pidm_p, ciclo, carrera, cookies)

    def carreras(self) -> Tuple[CarreraEstudiante]:
        cookies, pidm_p, _, __ = self.sesion
        return carrera_s_estudiante(pidm_p, cookies)

    def oferta(self, centro='', ciclo='', clase='', con_cupos=False) -> Tuple[ClaseOferta]:
        if ciclo == '':
            ciclo = self.sesion.ciclo
        return oferta_academica(centro, ciclo, clase, con_cupos)


if __name__ == '__main__':
    print('Esto no se deberia mostrar. Ejecutando consulta_siiau_service.')

