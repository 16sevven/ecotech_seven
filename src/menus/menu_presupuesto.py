import requests

from dominio.proyecto import Proyecto
from servicios.presupuesto import estimar_presupuesto_usd


def mostrar_estimacion_usd(proyecto):
    """Muestra la estimacion en USD. Si algo falla, el flujo del sistema continua."""
    print("\n--- ESTIMACION DEL PRESUPUESTO EN DOLARES ---")
    if proyecto._presupuesto_clp <= 0:
        print("El proyecto no tiene presupuesto definido. Registrelo con "
              "'Actualizar Proyecto' para poder estimarlo en USD.")
        return None
    try:
        r = estimar_presupuesto_usd(proyecto)
    except requests.exceptions.RequestException:
        print("Estimacion en USD no disponible: no pudimos consultar el servicio. Reintente.")
        return None
    except (ValueError, KeyError, TypeError):
        print("Estimacion en USD no disponible: la respuesta no contiene un indicador valido.")
        return None

    print(f"Presupuesto de referencia: ${Proyecto.formatear_clp(r['presupuesto_clp'])} CLP")
    print(f"Dolar observado: {r['valor_dolar']:.2f} {r['unidad']} (fecha {r['fecha']})")
    print(f"Estimacion: {r['usd']:,.2f} USD")
    print(f"Origen: {r['origen']}")
    if r["desactualizado"]:
        print(f"Aviso: el valor del dolar tiene {r['antiguedad_dias']} dias de antiguedad; "
              "la estimacion puede no ser actual.")
    print("Referencia aproximada, no es una cotizacion bancaria.")
    return r
