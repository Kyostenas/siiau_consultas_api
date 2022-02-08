from utiles import limpiar_html, particionar, convertir_ciclo_a_entero, aplanar_lista
from bs4 import BeautifulSoup as WebSp
from requests import request, Session
from typing import NamedTuple, Tuple, List
import re

VACIO = '\xa0'
RETORNO = '\n'

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
I_HORARIO_MATERIA_OFERTA = 8
I_PROFESORES_MATERIA_OFERTA = 7
ANCHO_TABLA_PROFES_OFERTA = 2
I_DIAS_HORARIOS_OFERTA = 2
DIA_VACIO_HORARIO_OFERTA = '.'


class RefererSession(Session):
    def rebuild_auth(self, prepared_request, response):
        super().rebuild_auth(prepared_request, response)
        prepared_request.headers['Referer'] = response.url

class DatosSesion(NamedTuple):
    cookies: str
    pidmp: int


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


class MateriaOferta(NamedTuple):
    nrc: str
    clave: str
    materia: str
    seccion: str
    creditos: int
    cupos: int
    disponibles: int
    profesores: List[ProfesorOferta]
    horarios: List[HorarioOferta]


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
    L: Tuple[str]
    M: Tuple[str]
    I: Tuple[str]
    J: Tuple[str]
    V: Tuple[str]
    S: Tuple[str]
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
    return WebSp(response.text, 'html.parser').find_all(**findall)


def preparar_para_busqueda(cadena: str) -> str:
    """
    Prepara una cadena para buscar coincidencias convirtiéndola
    a minúscula toda, borrando espacios.

    "Una cadena de texto" => "unacadenadetexto"
    """
    sin_espacios = ''.join(cadena.split(' '))
    minusculas = sin_espacios.lower()

    return minusculas


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
        datos_horarios_siiau = DatosHorarioSiiau(tabla_datos_estudiantes_completa, tabla_horario_completa)

        return datos_horarios_siiau

    def oferta(self, materia, centro, con_cupos=False):
        url_oferta = f'{self.url_siiau_estudiante}' \
                     f'/wal/sspseca.consulta_oferta'
        payload = dict(ciclop=self.ciclo,
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
            materias_particionadas[i_fila] = MateriaOferta(*fila)

        return tuple(materias_particionadas)

    def carrera_s_estudiante(self) -> Tuple[CarreraEstudiante]:
        url_carrera = f'{self.url_siiau_estudiante}' \
                      f'/wal/gupmenug.menu'
        payload = dict(p_sistema_c='ALUMNOS',
                       p_sistemaid_n='3',
                       p_menupredid_n='3',
                       p_pidm_n=self.pidm_p,
                       p_majr_c=self.pidm_p)
        accept = ['text / html, application / xhtml + xml, application / xml',
                  'q = 0.9, image / avif, image / webp, image / apng, * / *',
                  'q = 0.8, application / signed - exchange', 'v = b3', 'q = 0.9']
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

    def ciclos(self) -> Tuple[CicloCompleto]:
        url_ciclos = f'{self.url_siiau_estudiante}' \
                     f'/wal/sgpofer.secciones'
        payload = dict(pidmp='',
                       majrp='')
        url_ciclos = join_payload_url(url_ciclos, payload)
        resp = request('GET',
                       url=url_ciclos,
                       data=payload)
        ciclos_opciones = websp_findall(resp, name='select', attrs=dict(id='cicloID'))
        ciclos_opciones = list(map(limpiar_html, ciclos_opciones))[0].split('\n')
        ciclos_opciones_limpios = list(map(lambda cic: cic.split(' - '), ciclos_opciones))
        while [''] in ciclos_opciones_limpios:
            ciclos_opciones_limpios.remove([''])
        ciclos_completos = tuple(map(lambda partido: CicloCompleto(*partido), ciclos_opciones_limpios))

        return ciclos_completos

    def ciclos_por_busqueda(self, busqueda: str) -> Tuple[CicloCompleto]:
        todos_los_ciclos = self.ciclos()
        encontrados: List[CicloCompleto] = []
        patron = preparar_para_busqueda(busqueda)
        for ciclo_sondeado in todos_los_ciclos:
            ref = preparar_para_busqueda(ciclo_sondeado.ref_ciclo)
            nom = preparar_para_busqueda(ciclo_sondeado.nombre_completo)
            busqeda_ref = ref.find(patron)
            busqueda_nom = nom.find(patron)
            if busqeda_ref > -1 or busqueda_nom > -1:
                encontrados.append(ciclo_sondeado)
        empacados = tuple(encontrados)

        return empacados

    def centros(self) -> Tuple[CentroCompleto]:
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
        centros_obtenidos = tuple(map(lambda cen_opc: CentroCompleto(*cen_opc.split(' - ')), centros_opciones))

        return centros_obtenidos

    def carreras(self, centro_cup_id: str) -> Tuple[CarreraCompleta]:
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
        carreras_procesadas = tuple(map(lambda carr_c: CarreraCompleta(*carr_c), lista_carreras_completa))
        return carreras_procesadas

    def materias(self, id_carrera: str) -> Tuple[MateriaCompleta]:
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

    def obtener(self):
        return DatosSesion(cookies=self.__obtener_cookies(),
                           pidmp=self.__obtener_pidm_p())

    def __obtener_cookies(self) -> str:
        masa = self.resp_inicio.cookies.get_dict(self.url_base)
        horneado = [f'{nom}={val}' for nom, val in masa.items()]
        cookies = ';'.join(horneado)

        return cookies

    def __obtener_pidm_p(self) -> int:
        bienvenida = WebSp(self.resp_inicio.text, "html.parser").find_all('input')
        for val in bienvenida:
            if 'p_pidm_n' in str(val):
                bienvenida = str(val)
                break

        limpiador = re.compile('[^\d]+')
        pidm_p = int(re.sub(limpiador, '', str(bienvenida)))

        return pidm_p


if __name__ == '__main__':
    print('Esto no se debería mostrar...')
