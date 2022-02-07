from typing import NamedTuple
from bs4 import BeautifulSoup

from utiles import particionar, particion_arbitraria, limpiar_html


class OfertaFormada(NamedTuple):
    # Materias ordenadas por Clave, ej.
    # {'I7024' : { 'nrc': {}, ...}, ...}
    materias: dict

    # Nrc de materias por Clave, ej.
    # {'I7024 : ['nrc', ...], ...}
    nrcs: dict

    # Profesores de materias por Clave, ej.
    # {'I7024': ['profesores', ...], ...}
    profesores: dict


class Profesor(NamedTuple):
    ses: str  # Identificador raro de SIIAU
    nombre: str  # Nombre del o los profesores


class HorarioCompleto(NamedTuple):
    ses: str  # Identificador usado en SIIAU (¿Para qué sirve?)
    duracion: str  # Horas de clase
    dias: str  # Dias de clase
    ubicacion: str  # Edificio y Aula (Por ahora unidos, mientras se soluciona)
    periodo: str  # Fecha Inicio - Fin


class MateriaCompleta(NamedTuple):
    nrc: str  # Nrc de la materia
    clave: str  # Clave de la materia
    nombre: str  # Nombre de la materia
    seccion: str  # Seccion a la que corresponde la materia
    creditos: int  # Creditos que otorga pasar la materia
    cupos: int  # Cupos que permite
    cupo_disponible: int  # Cupos actualmente disponibles
    horarios: list[str]  # HorarioSiiau/s y lugares en los que se imparte la clase
    profesores: list  # Conjunto de profesores/es que imparte/n la clase

    # Horas por dia de la materia (para la tabla
    # ordenada del horario_siiau). Es un rango que marca
    # en cuales horas de una columna (dia), poner
    # la materia
    rango_por_dia: list


class Oferta(object):

    def __init__(self, consulta, *materia, centro='') -> None:
        self.matAConsultar = materia
        self.consulta = consulta
        self.centro = centro
        self.horarios_crudos = []
        self.materias_crudas = []  # Incluyen profesores, pero no horarios
        self.horarios = []
        self.materias = []
        self.completa = []
        self.filtrada = []
        self.nombres_materias = {}
        self.nrcs = {}
        self.profes = {}
        self.procesada = {}

    @property
    def dias_semana(self):
        return ['L', 'M', 'I', 'J', 'V', 'S']

    @property
    def horas_horario_completas(self):
        return ['0700-0755', '0800-0855', '0900-0955',
                '1000-1055', '1100-1155', '1200-1255',
                '1300-1355', '1400-1455', '1500-1555',
                '1600-1655', '1700-1755', '1800-1855',
                '1900-1955', '2000-2055', '2100-2155']

    @property
    def horas_horario(self):
        return ['0700', '0800', '0900',
                '1000', '1100', '1200',
                '1300', '1400', '1500',
                '1600', '1700', '1800',
                '1900', '2000', '2100']

    @property
    def clave_horario(self):
        return {'nrc': 0,
                'dur': 1,
                'dias': 2,
                'ubi': 3,
                'per': 4}

    @property
    def clave_oferta(self):
        return {'nrc': 0,
                'cve': 1,
                'nom': 2,
                'sec': 3,
                'cred': 4,
                'cup': 5,
                'disp': 6,
                'prof': 7}

    def _ordenar_horarios(self):
        horarios = []
        for linea in self.horarios_crudos:
            horarios.append(limpiar_html(linea))

        horarios_limpios = []
        for horario in horarios:
            horario = horario.replace(' ', '').splitlines()
            while '' in horario:
                horario.remove('')
            hor_compuesto = []
            for horSimple in horario:
                aula_edificio = 0
                for car in horSimple:
                    if car == '/':
                        aula_edificio = (horSimple.index(car) - 3) - 16
                        break
                hor_sim_procesado = particion_arbitraria(horSimple, 2, 9, 6,
                                                         aula_edificio, 17, join_string=True)
                hor_sim_procesado[2] = list(hor_sim_procesado[2].replace('.', ''))
                hor_sim_procesado = HorarioCompleto(ses=hor_sim_procesado[self.clave_horario['nrc']],
                                                    duracion=hor_sim_procesado[self.clave_horario['dur']],
                                                    dias=hor_sim_procesado[self.clave_horario['dias']],
                                                    ubicacion=hor_sim_procesado[
                                                        self.clave_horario['ubi']],
                                                    periodo=hor_sim_procesado[self.clave_horario['per']])
                hor_compuesto.append(hor_sim_procesado)
            horarios_limpios.append(hor_compuesto)

        return horarios_limpios

    def _ordenar_materias(self):
        materias_limpias = []
        for linea in self.materias_crudas:
            materias_limpias.append(limpiar_html(linea))

        for linProfesor in range(7, len(materias_limpias), 8):
            profes_crudos = materias_limpias[linProfesor].splitlines()
            while '' in profes_crudos:
                profes_crudos.remove('')
            profes_ordenados = particionar(profes_crudos, 2)
            profes_clasificados = []
            for profesor_s in profes_ordenados:
                profe_sim_clasificado = Profesor(ses=profesor_s[0],
                                                 nombre=profesor_s[1].title())
                profes_clasificados.append(profe_sim_clasificado)
            materias_limpias[linProfesor] = profes_clasificados

        materias_limpias = particionar(materias_limpias, 8)

        materias_clasificadas = []
        for materia_l in materias_limpias:
            mat_clasificadas = MateriaCompleta(nrc=materia_l[self.clave_oferta['nrc']],
                                               clave=materia_l[self.clave_oferta['cve']],
                                               nombre=materia_l[self.clave_oferta['nom']],
                                               seccion=materia_l[self.clave_oferta['sec']],
                                               creditos=int(materia_l[self.clave_oferta['cred']]),
                                               cupos=int(materia_l[self.clave_oferta['cup']]),
                                               cupo_disponible=int(materia_l[self.clave_oferta['disp']]),
                                               horarios=[],
                                               profesores=materia_l[self.clave_oferta['prof']],
                                               rango_por_dia=[])
            materias_clasificadas.append(mat_clasificadas)

            if mat_clasificadas.clave not in list(self.nombres_materias.keys()):
                self.nombres_materias[mat_clasificadas.clave] = mat_clasificadas.nombre

        return materias_clasificadas

    def _obtener_datos(self, materiaSimple):
        html = BeautifulSoup(
            self.consulta.oferta(
                materiaSimple,
                self.centro
            ).content, 'html.parser'
        )
        self.materias_crudas = html.select('td.tddatos')
        self.horarios_crudos = html.select('table.td1')
        self.materias = self._ordenar_materias()
        self.horarios = self._ordenar_horarios()

        for materia in range(len(self.materias)):
            for horario in self.horarios[materia]:
                self.materias[materia].horarios.append(horario)
            for horario in self.horarios[materia]:
                for dia in horario.dias:
                    rango_clave = horario.duracion.split('-')
                    rango_clave[1] = rango_clave[1][:2] + (
                        '55' if rango_clave[1][2:] == '00' else '00')
                    rango_clave = slice(self.horas_horario.index(rango_clave[0]),
                                        self.horas_horario.index(rango_clave[1]) + 1)
                    horas_en_rango = self.horas_horario[rango_clave]
                    for i in range(len(horas_en_rango)):
                        ubicacion = (self.horas_horario.index(horas_en_rango[i]),
                                     self.dias_semana.index(dia))
                        horas_en_rango[i] = '-'.join([horas_en_rango[i],
                                                      horas_en_rango[i][:2] + '55'])
                        self.materias[materia].rango_por_dia.append(ubicacion)
            self.completa.append(self.materias[materia])

        return self.completa

    def _filtrar_datos_segun_horario(self, seleccionHorario, filtroEstricto=True):
        for materia in self.completa:
            correctas = 0
            for posicion in materia.rango_por_dia:
                if posicion in seleccionHorario:
                    correctas += 1
            if filtroEstricto and correctas == len(materia.rango_por_dia):
                self.filtrada.append(materia)
            if (not filtroEstricto) and correctas > 0:
                self.filtrada.append(materia)

        return self.filtrada

    def _convertirADic(self, materiasFiltradas):
        materias = self.filtrada if materiasFiltradas else self.completa
        for obtenida in materias:
            try:
                for profe in range(len(obtenida.profesores)):
                    obtenida.profesores[profe] = obtenida.profesores[profe]._asdict()
                for hor in range(len(obtenida.horarios)):
                    obtenida.horarios[hor] = obtenida.horarios[hor]._asdict()
            except:
                print(len(materias))
                print(materias.index(obtenida))
                print(obtenida)
                exit()
            para_hacer_dic = obtenida
            convertida = para_hacer_dic._asdict()

            try:
                self.procesada[obtenida.clave][obtenida.nrc] = convertida
            except:
                self.procesada[obtenida.clave] = {
                    'nombre': self.nombres_materias[obtenida.clave]
                }
                self.procesada[obtenida.clave][obtenida.nrc] = convertida
            try:
                self.nrcs[obtenida.clave].append(obtenida.nrc)
            except:
                self.nrcs[obtenida.clave] = []
                self.nrcs[obtenida.clave].append(obtenida.nrc)
            for profesor in obtenida.profesores:
                try:
                    if profesor['nombre'] not in self.profes[obtenida.clave]:
                        self.profes[obtenida.clave].append(profesor['nombre'])
                except:
                    self.profes[obtenida.clave] = []
                    self.profes[obtenida.clave].append(profesor['nombre'])
            self.profes[obtenida.clave].sort()

        return OfertaFormada(self.procesada, self.nrcs, self.profes)

    def buscar(self, selHorario='', filtSegunHorario=True, filtroHorarioEstricto=True,
               filtrarProfesores=True):
        if len(self.matAConsultar) == 0:
            return
        for matSimple in self.matAConsultar:
            self._obtener_datos(matSimple)
        if filtSegunHorario:
            self._filtrar_datos_segun_horario(selHorario, filtroHorarioEstricto)
        # if filtrarProfesores:
        #     # self._filtrarProfesores()
        #     pass

        return self._convertirADic(filtSegunHorario)