from ctypes import Union
from esquemas import ClaseOferta, Clase, HorarioOferta, DiasHorarioOferta
from servicio_horario_siiau import compactar_horario_por_clases
from servicio_consulta_siiau import oferta
from utiles import simplificar_lista

from typing import List, Tuple, Union


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


def revisar_solapamientos(oferta: Tuple[ClaseOferta]) -> Tuple[bool, Tuple[int]]:

    campos = obtener_campos_clases(oferta=oferta)
    horarios: Tuple[HorarioOferta] = campos.horarios
    indices_clases_solapadas = []
    clases_se_solapan = False
    
    dias_sensores = [False, False, False, False, False, False]
    conjunto_dias_horas = dict()
    for i_clase, horarios_una_clase in enumerate(horarios):
        for un_horario_una_clase in horarios_una_clase:
            un_horario_una_clase: HorarioOferta
            hora = un_horario_una_clase.hora

            try:
                conjunto_dias_horas[hora]
            except KeyError:
                conjunto_dias_horas[hora] = {'indices': [i_clase], 'sensores': dias_sensores}
            
            for i_dia, dia_horario_por_revisar in enumerate(un_horario_una_clase.dias):
                if conjunto_dias_horas[hora]['sensores'][i_dia] is False:
                    if dia_horario_por_revisar is True:
                        conjunto_dias_horas[hora]['sensores'][i_dia] = True
                elif conjunto_dias_horas[hora]['sensores'][i_dia] is True:
                    if dia_horario_por_revisar is True:
                        conjunto_dias_horas[hora]['indices'].append(i_clase)
                        indices_clases_solapadas += conjunto_dias_horas[hora]['indices']
                        if clases_se_solapan is False:
                            clases_se_solapan = True  # Si ya era verdadero, ya hay una clase ahi. Se solapan
    
    indices_clases_solapadas = tuple(simplificar_lista(indices_clases_solapadas))

    return clases_se_solapan, indices_clases_solapadas


def filtrar_clases_solapadas(oferta: Tuple[ClaseOferta], 
                             indices_solapados: Union[Tuple[int], List[int]]) -> Tuple[ClaseOferta]:
    filtradas = []
    [filtradas.append(clase) for i_clase, clase in enumerate(oferta) if i_clase not in indices_solapados]
    filtradas = tuple(filtradas)

    return filtradas


def estructurar_oferta_como_horario(oferta: Tuple[ClaseOferta]) -> Tuple[Clase]:
    hay_clases_solapadas, clases_que_se_solapan = revisar_solapamientos(oferta=oferta)
    if hay_clases_solapadas:
        clases_filtradas = filtrar_clases_solapadas(oferta, clases_que_se_solapan)
        print(clases_filtradas)
    else:
        print(hay_clases_solapadas)


if __name__ == '__main__':
    # from os import environ as envF
    # from dotenv import load_dotenv
    # import time
    # usuario = env['USUARIO_G']
    # contra = env['CONTRA_G']
    # carrera = env['CARRERA_G']
    # ciclo = env['CICLO_ACTUAL_G']

    oferta_202210 = oferta(centro='D', ciclo='202210', materia='I7024')
    estructurar_oferta_como_horario(oferta=oferta_202210)

    

    