from horario_siiau_service import compactar_horario_por_clases
from consulta_siiau_service import oferta
from esquemas import ClaseOferta, Clase
from typing import NamedTuple, Tuple, List


def estructurar_oferta_como_horario(oferta: Tuple[ClaseOferta]):
    pass


def obtener_campos_oferta(oferta: Tuple[ClaseOferta]) -> ClaseOferta:
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



if __name__ == '__main__':
    # from os import environ as envF
    # from dotenv import load_dotenv
    # import time

    # usuario = env['USUARIO_G']
    # contra = env['CONTRA_G']
    # carrera = env['CARRERA_G']
    # ciclo = env['CICLO_ACTUAL_G']

    oferta = oferta(centro='D', ciclo='202210', materia='I7024')
    campos_oferta = obtener_campos_oferta(oferta=oferta)
    campo = campos_oferta.nrc
    list(map(print, campo))
    

    