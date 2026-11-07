import math


class Proyecto:
    MAX_PRESUPUESTO = 999_999_999_999

    def __init__(self, nombre, fecha_inicio, descripcion, id_proyecto=None, presupuesto_clp=0):
        self._id_proyecto = id_proyecto
        self._nombre = nombre
        self._fecha_inicio = fecha_inicio
        self._descripcion = descripcion
        self._presupuesto_clp = self.validar_presupuesto(presupuesto_clp)
        self._empleados = []
        self._registros_tiempo = []

    # ------------------------------------------------------------ presupuesto
    @classmethod
    def validar_presupuesto(cls, valor):
        """Acepta numero o texto (coma o punto decimal); no negativo y finito."""
        mensaje = "Ingrese solo numeros, por ejemplo 12000000."
        if isinstance(valor, bool) or valor is None:
            raise ValueError(mensaje)
        texto = str(valor).strip().replace(",", ".")
        if not texto:
            raise ValueError("Ingrese un presupuesto (use 0 si aun no tiene).")
        try:
            numero = float(texto)
        except ValueError:
            raise ValueError(mensaje) from None
        if not math.isfinite(numero):
            raise ValueError(mensaje)
        if numero < 0:
            raise ValueError("El presupuesto no puede ser negativo.")
        if numero > cls.MAX_PRESUPUESTO:
            raise ValueError("El presupuesto es demasiado grande.")
        return numero

    @staticmethod
    def formatear_clp(monto):
        """12000000 -> '12.000.000' (separador de miles chileno)."""
        return f"{monto:,.0f}".replace(",", ".")

    def estimar_presupuesto_usd(self, valor_dolar):
        """Convierte el presupuesto en CLP a USD con el valor del dolar recibido.

        El dominio no consulta ninguna API: recibe el valor ya obtenido y
        vuelve a comprobarlo (numero finito y mayor que cero) antes de usarlo.
        """
        if type(valor_dolar) not in (int, float) or not math.isfinite(valor_dolar) \
                or valor_dolar <= 0:
            raise ValueError("El valor del dolar no es valido.")
        if self._presupuesto_clp <= 0:
            raise ValueError("El proyecto no tiene presupuesto definido.")
        return round(self._presupuesto_clp / valor_dolar, 2)

    def asignar_empleado(self, empleado):
        if empleado is None or empleado in self._empleados:
            return False
        self._empleados.append(empleado)
        return True

    def desvincular_empleado(self, empleado):
        if empleado not in self._empleados:
            return False
        self._empleados.remove(empleado)
        return True

    def agregar_registro_tiempo(self, registro):
        if registro is None:
            return False
        if registro._proyecto != self:
            return False
        if registro._empleado not in self._empleados:
            return False
        if registro._horas_trabajadas <= 0:
            return False
        if registro in self._registros_tiempo:
            return False
        self._registros_tiempo.append(registro)
        return True

    def generar_informe(self):
        total_horas = 0
        for registro in self._registros_tiempo:
            total_horas += registro._horas_trabajadas
        if self._presupuesto_clp > 0:
            presupuesto = f"${self.formatear_clp(self._presupuesto_clp)} CLP"
        else:
            presupuesto = "no definido"
        return (
            f"Proyecto: {self._nombre}\n"
            f"Fecha de inicio: {self._fecha_inicio}\n"
            f"Descripción: {self._descripcion}\n"
            f"Presupuesto de referencia: {presupuesto}\n"
            f"Cantidad de empleados: {len(self._empleados)}\n"
            f"Horas registradas: {total_horas}"
        )
