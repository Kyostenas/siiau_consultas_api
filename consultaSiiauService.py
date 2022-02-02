from utiles import limpiar_html, particionar, convertir_ciclo_a_entero
from bs4 import BeautifulSoup as WebSp
from requests import request, Session
from typing import NamedTuple
import re

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
ESP_FAL_SUB_MATERIA = 4
I_REF_CARRERA_ESTUDIANTE = 0  # Esta es en las carreras registradas del estudiante
RANGO_CICLO_IN_CARR_ES = slice(1, 3)


class RefererSession(Session):
    def rebuild_auth(self, prepared_request, response):
        super().rebuild_auth(prepared_request, response)
        prepared_request.headers['Referer'] = response.url


class MateriaCompleta(NamedTuple):
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


class CarreraCompleta(NamedTuple):
    ref_carrera: str
    nombre_completo: str


class CentroCompleto(NamedTuple):
    id_centro: str
    nombre_completo: str


class CicloCompleto(NamedTuple):
    ref_ciclo: str  # el nombre que maneja siiau (2019 B -> 201920)
    ref_publica_ciclo: str  # la que se muestra en siiau  (202210 -> "2022 A")
    nombre_completo: str  # 2022 A -> "Calendario 22 A"


class HorarioCompletoSiiau(NamedTuple):
    nrc: tuple[str]
    clave: tuple[str]
    nombre_materia: tuple[str]
    seccion: tuple[str]
    creditos: tuple[int]
    horario: tuple[str]
    L: tuple[str]
    M: tuple[str]
    I: tuple[str]
    J: tuple[str]
    V: tuple[str]
    S: tuple[str]
    edificio: tuple[str]
    aula: tuple[str]
    profesor: tuple[str]
    fecha_inicio: tuple[str]
    fecha_fin: tuple[str]


class DatosHorarioSiiau(NamedTuple):
    datos_estudiante: NamedTuple
    horario: HorarioCompletoSiiau


class CarreraEstudiante(NamedTuple):
    ref_carrera: str
    ciclo_inicio: str
    ref_ciclo: int


def convertir_a_identificador_valido(valor: str) -> str:
    valor = valor.split(' ')
    valor = '_'.join(valor).encode('ascii', errors='ignore').decode().lower()
    valor = re.sub('[\W_]+', '', valor)
    return valor


def join_payload_url(url: str, payload: dict):
    payload_string = ''
    for llave, valor in payload.items():
        nuevo_valor = '='.join([llave, f'{valor}'])
        if payload_string == '':
            payload_string = nuevo_valor
        else:
            payload_string = '&'.join([payload_string, nuevo_valor])

    nueva_url = '?'.join([url, payload_string])

    return nueva_url


def websp_findall(response, **findall):
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
    resultados = WebSp(response.text, 'html.parser').find_all(**findall)
    return resultados


class ConsultaSIIAU(object):

    def __init__(self,
                 ciclo: str = '',
                 cookies: str = '',
                 carrera: str = '',
                 pidm_p: int = 0) -> None:
        self.cookies = cookies
        self.carrera = carrera
        self.ciclo = ciclo
        self.pidm_p = pidm_p
        self.url_siiau_estudiante = 'http://siiauescolar.siiau.udg.mx'
        self.url_consulta_siiau = 'http://consulta.siiau.udg.mx'

    def horario(self) -> DatosHorarioSiiau:
        url_horario = f'{self.url_siiau_estudiante}' \
                      f'/wal/sfpcoal.horario'
        payload = dict(pidmP=self.pidm_p,
                       cicloP=self.ciclo,
                       majrP=self.carrera,
                       encaP='0')
        headers = {'Content-Type': 'text/html; charset=ISO-8859-1',
                   'Cookie': self.cookies}
        resp = request('POST',
                       url_horario,
                       headers=headers,
                       data=payload)

        encabezados = websp_findall(resp, name='th')
        tablas = websp_findall(resp, name='td')
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
        encabezados_datos_estudiantes = tuple(map(convertir_a_identificador_valido, encabezados_datos_estudiantes))
        encabezados_horario = tuple(encabezados[inicio_enc_hor:])
        encabezados_horario = tuple(map(convertir_a_identificador_valido, encabezados_horario))
        tabla_datos_estudiantes = tuple(tablas[:len(encabezados_datos_estudiantes)])
        tabla_horario = tablas[len(encabezados_datos_estudiantes):]
        for i_dato in range(len(tabla_horario)):
            if i_dato % ANCHO_TABLA_HORARIO == 0:
                if tabla_horario[i_dato] == '':
                    [tabla_horario.insert(i_dato + 1, '') for _ in range(ESP_FAL_SUB_MATERIA)]
        tabla_horario = particionar(tabla_horario, len(encabezados_horario))
        tabla_horario = tuple(zip(*tabla_horario))
        campos_tabla_datos_estudiante = ((encabezado, str) for encabezado in encabezados_datos_estudiantes)
        tabla_dat_es_clase = NamedTuple('DatosEstudiante', campos_tabla_datos_estudiante)
        tabla_datos_estudiantes_completa = tabla_dat_es_clase(*tabla_datos_estudiantes)
        tabla_horario_completa = HorarioCompletoSiiau(*tabla_horario)

        return DatosHorarioSiiau(tabla_datos_estudiantes_completa, tabla_horario_completa)

    def oferta(self, materia, centro, conCupos=False):
        url_oferta = f'{self.url_siiau_estudiante}' \
                     f'/wal/sspseca.consulta_oferta'
        payload = dict(ciclop=self.ciclo,
                       cup=centro,
                       majrp=self.carrera,
                       crsep=materia,
                       materiap='',
                       horaip='',
                       horafp='',
                       edifp='',
                       aulap='',
                       dispp=centro if conCupos else '',
                       ordenp='0',
                       mostrarp=f'100000')
        resp = request('POST',
                       url_oferta,
                       data=payload)

        return resp

    def carrera_s_estudiante(self) -> tuple[CarreraEstudiante]:
        url_carrera = f'{self.url_siiau_estudiante}' \
                      f'/wal/gupmenug.menu'
        payload = dict(p_sistema_c='ALUMNOS',
                       p_sistemaid_n='3',
                       p_menupredid_n='3',
                       p_pidm_n=self.pidm_p,
                       p_majr_c=self.pidm_p)
        accept = ['text / html, application / xhtml + xml, application / xml',
                  'q = 0.9, image / avif, image / webp, image / apng, * / *',
                  'q = 0.8, application / signed - exchange',
                  'v = b3',
                  'q = 0.9']
        headers = {'Accept': ';'.join(accept),
                   'Accept-Encoding': 'gzip,deflate',
                   'Accept-Language': 'es-419,es;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': self.cookies,
                   'Host': 'siiauescolar.siiau.udg.mx',
                   'Referer': f'{url_carrera}_sistema?p_pidm_n={self.pidm_p}',
                   'Upgrade-Insecure-Requests': '1'}

        url_carrera = join_payload_url(url_carrera, payload)
        resp = request('GET',
                       url=url_carrera,
                       headers=headers,
                       data=payload,
                       allow_redirects=True)
        carreras_opciones = websp_findall(resp, name='option')
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

    def ciclos(self) -> tuple[CicloCompleto]:
        url_ciclos = f'{self.url_siiau_estudiante}' \
                     f'/wal/sgpofer.secciones'
        payload = dict(pidmp='',
                       majrp='')
        url_ciclos = join_payload_url(url_ciclos, payload)
        resp = request('GET',
                       url=url_ciclos,
                       data=payload)
        ciclos_opciones = websp_findall(resp, name='select', attrs={'id': 'cicloID'})
        ciclos_opciones = tuple(map(limpiar_html, ciclos_opciones))[0].split('\n')
        while '' in ciclos_opciones:
            ciclos_opciones.remove('')
        ciclos = tuple(map(lambda x: tuple(map(lambda z: tuple(z.split(' ')), x.split(' - '))), ciclos_opciones))
        ciclos_completos = []
        limpiar_letras = re.compile('[^\d]+')
        limpar_no_letra_o_numero = re.compile('[^A-Za-z\d]+')
        for ciclo_partido in ciclos:
            if len(ciclo_partido[I_REF_CICLO]) == 1:
                ref_ciclo = ciclo_partido[I_REF_CICLO][0]
            else:
                ref_ciclo = ''.join(ciclo_partido[I_REF_CICLO])
            ref_sin_letras = re.sub(limpiar_letras, '', ref_ciclo)
            ref_publica_ciclo = ''
            for parte_nom_com in ciclo_partido[I_NOM_CICLO]:
                parte_nom_com = re.sub(limpar_no_letra_o_numero, '', parte_nom_com)
                print(parte_nom_com)
                parte_sin_letras = re.sub(limpiar_letras, '', parte_nom_com)
                if len(parte_sin_letras) == 0:
                    pass
                elif len(parte_nom_com) == 2:
                    ref_publica_ciclo = ''.join([ref_ciclo[:2], parte_nom_com])  # Mitad del año ('2022X'[:2] -> 20)
                    break
                elif len(parte_nom_com) == len(ref_sin_letras):
                    print('=====')
                    print(ciclo_partido[I_NOM_CICLO])
                    i_parte_actual = ciclo_partido[I_NOM_CICLO].index(parte_nom_com)
                    ref_publica_ciclo = ''.join([ciclo_partido[I_NOM_CICLO][i_parte_actual],
                                                 ciclo_partido[I_NOM_CICLO][i_parte_actual + 1]])
                    break
                elif len(parte_nom_com) == len(ref_ciclo):
                    ref_publica_ciclo = parte_nom_com
                    break

            nuevo_ciclo_completo = CicloCompleto(ref_ciclo=ref_ciclo,
                                                 ref_publica_ciclo=ref_publica_ciclo,
                                                 nombre_completo=' '.join(ciclo_partido[I_NOM_CICLO]))
            ciclos_completos.append(nuevo_ciclo_completo)

        return tuple(ciclos_completos)

    def centros(self):
        url_centros = f'{self.url_siiau_estudiante}' \
                      f'/wal/sgpofer.secciones'
        payload = dict(pidmp='',
                       majrp='')
        url_centros = join_payload_url(url_centros, payload)
        resp = request('GET',
                       url=url_centros,
                       data=payload)
        centros_opciones = websp_findall(resp, name='select', attrs={'name': 'cup'})
        centros_opciones = tuple(map(limpiar_html, centros_opciones))[0].split('\n')
        while '' in centros_opciones:
            centros_opciones.remove('')
        centros_obtenidos = tuple(map(lambda x: tuple(x.split(' - ')), centros_opciones))

        return centros_obtenidos

    def carreras(self, centro_cup_id: str):
        """
        Recibe el parameter 'cup', que para siiau es el id de los
        centros universitarios. Con esto se pueden consultar
        todas las carreras de ese mismo centro
        """
        url_carreras = f'{self.url_siiau_estudiante}' \
                       f'/wal/sspseca.lista_carreras'
        payload = dict(cup=centro_cup_id)
        url_carreras = join_payload_url(url_carreras, payload)
        resp = request('GET',
                       url=url_carreras,
                       data=payload)
        lista_referencias = websp_findall(resp, name='a')
        lista_carreras = websp_findall(resp, name='td')
        lista_referencias = tuple(map(limpiar_html, lista_referencias))
        lista_carreras = tuple(map(limpiar_html, lista_carreras))
        lista_carreras_completa = particionar(lista_carreras, ANCHO_TABLA_CARRERAS)
        for carrera_c in lista_carreras_completa:
            if carrera_c[I_REF_CARRERA] not in lista_referencias:
                lista_carreras_completa.remove(carrera_c)

        return tuple(lista_carreras_completa)

    def materias(self, id_carrera: str) -> tuple[MateriaCompleta]:
        url_catalogo_materias = f'{self.url_consulta_siiau}' \
                                f'/wco/scpcata.cataxcarr'
        payload = dict(carrerap=id_carrera,
                       ordenp=1,
                       mostrarp=5,
                       tipop='T')
        url_catalogo_materias = join_payload_url(url_catalogo_materias, payload)
        resp = request('GET',
                       url=url_catalogo_materias,
                       data=payload)
        tabla_materias = websp_findall(resp, name='td')
        encabezados = websp_findall(resp, name='th')
        tabla_materias = list(map(limpiar_html, tabla_materias))[INICIO_TABLA_MATERIAS:]
        encabezados = list(map(limpiar_html, encabezados))[INICIO_TABLA_MATERIAS:]
        ancho_tabla = len(encabezados)
        tabla_materias = particionar(tabla_materias, ancho_tabla)

        materias_completas = []
        for renglon_materia in tabla_materias:
            if None not in renglon_materia:  # Ultimo renglón tiene "(c) 2002 Universidad de Guadalajara ..."
                materia_completa, _ = self._obtener_materia_completa(*renglon_materia[RANGO_SUBCLAVE_MATERIAS])
                materias_completas.append(materia_completa)

        return tuple(materias_completas)

    def _obtener_materia_completa(self, area, clave_materia, ciclo_inicio=''):
        url_materia_completa = f'{self.url_consulta_siiau}' \
                               f'/wco/scpcata.detmate'
        subclave = ','.join([area, clave_materia, ciclo_inicio])
        payload = dict(subclavep=subclave,
                       pEntra='OAP')  # TODO Encontrar qué es esto
        url_materia_completa = join_payload_url(url_materia_completa, payload)
        resp = request('GET',
                       url=url_materia_completa,
                       data=payload)
        tabla_materia_completa = websp_findall(resp, name='td')
        encabezados = websp_findall(resp, name='th')
        encabezados = list(map(limpiar_html, encabezados))
        titulo = encabezados.pop(TITULO_MATERIA_COMPLETA)
        tabla_materia_completa = list(map(limpiar_html, tabla_materia_completa))[:len(encabezados)]

        if tabla_materia_completa[I_AREA_MATERIA] == '':
            ciclo_inicio = tabla_materia_completa[I_CICLO_INICIO_MATERIA]
            _, tabla_materia_completa = self._obtener_materia_completa(area, clave_materia, ciclo_inicio)
        else:
            tabla_materia_completa.insert(TITULO_MATERIA_COMPLETA, titulo)

        return MateriaCompleta(*tabla_materia_completa), tabla_materia_completa


class SesionSIIAU(object):

    def __init__(self, codigo: str, clave: str) -> None:
        self.codigo = codigo
        self.clave = clave
        self.data = dict(p_codigo_c=self.codigo,
                         p_clave_c=self.clave)
        self.url_base = 'siiauescolar.siiau.udg.mx'
        self.url_inicio = (
            f'http://{self.url_base}'
            '/wus/gupprincipal.valida_inicio'
        )
        self.resp_inicio = request('POST',
                                   self.url_inicio,
                                   headers={},
                                   files=[],
                                   data=self.data)

    def obtener_cookies(self) -> str:
        masa = self.resp_inicio.cookies.get_dict(self.url_base)
        horneado = [f'{nom}={val}' for nom, val in masa.items()]
        cookies = ';'.join(horneado)

        return cookies

    def obtener_pidm_p(self) -> int:
        bienvenida = WebSp(self.resp_inicio.text, "html.parser").find_all('input')
        for val in bienvenida:
            if 'p_pidm_n' in str(val):
                bienvenida = str(val)
                break

        limpiador = re.compile('[^\d]+')
        pidm_p = re.sub(limpiador, '', str(bienvenida))

        return int(pidm_p)


if __name__ == '__main__':


    sesion = SesionSIIAU(usuario, contra)
    pidm_p = sesion.obtener_pidm_p()
    cookies = sesion.obtener_cookies()
    consulta = ConsultaSIIAU(ciclo=ciclo, cookies=cookies, carrera=carrera, pidm_p=pidm_p, )
    #
    # print(consulta.carrera_s_estudiante())
    list(map(print, consulta.ciclos()))
    # centros = consulta.centros()
    #
    # for centro in centros:
    #     print(f'\n{centro[I_NOM_CENTRO]}\n{"="*15}\n')
    #     carreras_centro = consulta.carreras(centro[I_ID_CENTRO])
    #     for c in carreras_centro:
    #         print(c)
    #         materias_carrera = consulta.materias(c[I_REF_CARRERA])
    #         for materia in materias_carrera:
    #             datos_materia = (materia.clave, materia.titulo)
    #             print(f'\t{datos_materia}')

    # print(consulta.horario())
