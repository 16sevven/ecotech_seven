"""Integra el dolar de la API con el presupuesto de un proyecto (flujo del sistema)."""
from servicios.indicadores import DIAS_MAX_ANTIGUEDAD, dias_de_antiguedad, obtener_dolar


def estimar_presupuesto_usd(proyecto, hoy=None):
    """Estima el presupuesto del proyecto en USD con el dolar observado.

    Orden pensado para no hacer trabajo inutil ni usar datos dudosos:
      1. si el proyecto no tiene presupuesto, NO se llama a la API;
      2. el dolar se obtiene y se valida (estructura, unidad, valor, fecha);
      3. el dominio vuelve a comprobar el valor y calcula;
      4. se informa la antiguedad del dato para advertir si esta desactualizado.
    """
    if proyecto._presupuesto_clp <= 0:
        raise ValueError("El proyecto no tiene presupuesto definido.")
    dolar = obtener_dolar()
    usd = proyecto.estimar_presupuesto_usd(dolar["valor"])
    antiguedad = dias_de_antiguedad(dolar["fecha"], hoy)
    return {
        "presupuesto_clp": proyecto._presupuesto_clp,
        "valor_dolar": dolar["valor"],
        "usd": usd,
        "fecha": dolar["fecha"],
        "unidad": dolar["unidad"],
        "origen": dolar["origen"],
        "antiguedad_dias": antiguedad,
        "desactualizado": antiguedad > DIAS_MAX_ANTIGUEDAD,
    }
