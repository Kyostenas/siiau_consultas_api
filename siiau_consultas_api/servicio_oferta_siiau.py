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


from .esquemas import ClaseOferta, Clase, DiaClase, HorarioOferta
from .utiles import simplificar_lista
from .servicio_horario_siiau import (
    __obtener_fecha_completa,
    __convertir_formato_24000_a_12h,
    __procesar_rango_horas,
    __rango_horas_hhmm
)
from typing import List, Tuple, Union


DIAS_SEMANA = 6  # Semana de clases

INDICES_DIAS = {0: 'dia_lu',
                1: 'dia_ma',
                2: 'dia_mi',
                3: 'dia_ju',
                4: 'dia_vi',
                5: 'dia_sa',}

MENSJE_PROFESOR_OFERTA = 'Materia de oferta'


def obtener_campos_clases(oferta: Tuple[ClaseOferta]) -> ClaseOferta:
    """
    Retorna tupla nombrada que permite escoger los campos en conjuntos
    de todas las materias de la oferta ingresada
    """
    nombres_campos_clase = ClaseOferta._fields
    solo_datos_clases = tuple(map(lambda clase: tuple(clase._asdict().values()), oferta))
    solo_datos_clases = tuple(zip(*solo_datos_clases))
    campos_con_nombres = tuple(zip(nombres_campos_clase, solo_datos_clases))
    campos_con_nombres = dict(campos_con_nombres)
    campos_oferta = ClaseOferta(**campos_con_nombres)

    return campos_oferta


def revisar_solapamientos(oferta: Tuple[ClaseOferta]) -> Tuple[bool, Tuple[int], Tuple[Tuple[int]]]:
    campos = obtener_campos_clases(oferta=oferta)
    horarios: Tuple[HorarioOferta] = campos.horarios
    indices_clases_solapadas = []
    juegos_clases_solapadas = []
    clases_se_solapan = False
    
    conjunto_dias_horas = dict()
    for i_clase, horarios_una_clase in enumerate(horarios):
        for un_horario_una_clase in horarios_una_clase:
            un_horario_una_clase: HorarioOferta
            hora = un_horario_una_clase.hora

            try:
                conjunto_dias_horas[hora]
            except KeyError:
                conjunto_dias_horas[hora] = {
                    'indices': [i_clase], 
                    'sensores': [False for _ in range(DIAS_SEMANA)]
                }
            
            for i_dia, dia_horario_por_revisar in enumerate(un_horario_una_clase.dias):
                if conjunto_dias_horas[hora]['sensores'][i_dia] is False:
                    if dia_horario_por_revisar is True:
                        conjunto_dias_horas[hora]['sensores'][i_dia] = True
                elif conjunto_dias_horas[hora]['sensores'][i_dia] is True:
                    if dia_horario_por_revisar is True:
                        conjunto_dias_horas[hora]['indices'].append(i_clase)
                        indices_clases_solapadas += conjunto_dias_horas[hora]['indices']
                        juegos_clases_solapadas.append(
                            tuple(
                               simplificar_lista(conjunto_dias_horas[hora]['indices'])
                            ) 
                        )
                        if clases_se_solapan is False:
                            clases_se_solapan = True  # Si ya era verdadero, ya hay una clase ahi. Se solapan
    
    indices_clases_solapadas = tuple(simplificar_lista(indices_clases_solapadas))
    juegos_clases_solapadas = tuple(simplificar_lista(juegos_clases_solapadas))

    return clases_se_solapan, indices_clases_solapadas, juegos_clases_solapadas


def filtrar_clases_solapadas(oferta: Tuple[ClaseOferta], 
                             indices_solapados: Union[Tuple[int], List[int]]) -> Tuple[ClaseOferta]:
    filtradas = []
    [filtradas.append(clase) for i_clase, clase in enumerate(oferta) if i_clase not in indices_solapados]
    filtradas = tuple(filtradas)

    return filtradas


def __revisar_dias(horarios: Tuple[HorarioOferta]) -> dict:
    dias_clase = dict(dia_lu=None,
                      dia_ma=None,
                      dia_mi=None,
                      dia_ju=None,
                      dia_vi=None,
                      dia_sa=None)

    for un_horario in horarios:
        un_horario: HorarioOferta
        for i_dia, es_dia_clase in enumerate(un_horario.dias):
            if es_dia_clase:
                hora_inicio, hora_fin = tuple(un_horario.hora.split('-'))
                hora_inicio_completa = __convertir_formato_24000_a_12h(hora_inicio)
                hora_final_completa = __convertir_formato_24000_a_12h(hora_fin)
                rango_horas = __procesar_rango_horas(hora_inicio, hora_fin)
                rango_horas_hhmm = __rango_horas_hhmm(int(hora_inicio), int(hora_fin), paso=100)

                nuevo_dia_clase = DiaClase(
                    hora_inicio=hora_inicio,
                    hora_final=hora_fin,
                    hora_inicio_completa=hora_inicio_completa,
                    hora_final_completa=hora_final_completa,
                    profesor=MENSJE_PROFESOR_OFERTA,
                    edificio=un_horario.edif,
                    aula=un_horario.aula,
                    rango_horas=rango_horas,
                    rango_horas_hhmm=rango_horas_hhmm
                )

                clave_dia = INDICES_DIAS[i_dia]
                dias_clase[clave_dia] = nuevo_dia_clase

    return dias_clase


def estructurar_oferta_como_horario(oferta: Tuple[ClaseOferta]) -> Tuple[Tuple[Clase], bool, Tuple[Tuple[int]]]:
    """
    Convierte una lista de materias de oferta (Seleccion de oferta), en un horario estructurado
    por materias (Lista de materias).

    Si las materias se solapan, solo retorna las que no se solapan con ninguna otra.

    Retorna horario por materias, valor booleano que dice si hay solapamientos, y, si es que hay,
    los juegos de indices solapados.
    """
    hay_solap, solapadas, juegos_solapadas = revisar_solapamientos(oferta=oferta)
    if hay_solap:
        clases_filtradas = filtrar_clases_solapadas(oferta, solapadas)
    else:
        clases_filtradas = oferta

    horario_por_clases = []

    for clase_oferta in clases_filtradas:
        fecha_inicio, fecha_fin = tuple(clase_oferta.horarios[0].periodo.split(' - '))
        fecha_inicio_completa = __obtener_fecha_completa(fecha_inicio, '/')
        fecha_final_completa = __obtener_fecha_completa(fecha_fin, '/')

        dias_clase = __revisar_dias(clase_oferta.horarios)

        nueva_clase = Clase(nrc=clase_oferta.nrc,
                            clave_materia=clase_oferta.clave,
                            nombre=clase_oferta.materia,
                            seccion=clase_oferta.seccion,
                            creditos=clase_oferta.creditos,
                            **dias_clase,
                            fecha_inicio=fecha_inicio,
                            fecha_final=fecha_fin,
                            fecha_inicio_completa=fecha_inicio_completa,
                            fecha_final_completa=fecha_final_completa)
        
        horario_por_clases.append(nueva_clase)
    
    horario_por_clases = tuple(horario_por_clases)
    
    return horario_por_clases, hay_solap, juegos_solapadas


if __name__ == '__main__':
    print('Esto no se debe mostrar. Ejecutando desde servicio_oferta_siiau')


    

    