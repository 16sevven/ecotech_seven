import math
import re
from datetime import date, datetime


class Empleado:
    # Reglas del dominio (constantes de la clase)
    MIN_NOMBRE = 2
    MAX_NOMBRE = 100
    MAX_DIRECCION = 200
    MAX_NUMERO = 30
    MAX_CORREO = 150
    MAX_CARGO = 100
    PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, nombre, direccion, numero, correo, fecha_contrato, salario, cargo, id=None):
        # Cada validador devuelve el dato ya limpio o lanza ValueError.
        self._id = id
        self._nombre = self.validar_nombre(nombre)
        self._direccion = self.validar_direccion(direccion)
        self._numero = self.validar_numero(numero)
        self._correo = self.validar_correo(correo)
        self._fecha_contrato = self.validar_fecha_contrato(fecha_contrato)
        self._salario = self.validar_salario(salario)
        self._cargo = self.validar_cargo(cargo)
        self._registros_tiempo = []

    # ------------------------------------------------------------ validadores
    @classmethod
    def _texto_obligatorio(cls, valor, articulo_nombre, maximo, genero="o"):
        """Texto no vacio y de largo acotado; quita espacios externos."""
        if not isinstance(valor, str):
            raise TypeError(f"{articulo_nombre.capitalize()} debe ser texto.")
        valor = valor.strip()
        if not valor:
            raise ValueError(f"Ingrese {articulo_nombre}. Es obligatori{genero}.")
        if len(valor) > maximo:
            raise ValueError(f"Use como maximo {maximo} caracteres.")
        return valor

    @classmethod
    def validar_nombre(cls, nombre):
        nombre = cls._texto_obligatorio(nombre, "un nombre", cls.MAX_NOMBRE)
        if len(nombre) < cls.MIN_NOMBRE:
            raise ValueError(f"El nombre debe tener al menos {cls.MIN_NOMBRE} caracteres.")
        return nombre

    @classmethod
    def validar_direccion(cls, direccion):
        return cls._texto_obligatorio(direccion, "una direccion", cls.MAX_DIRECCION, "a")

    @classmethod
    def validar_numero(cls, numero):
        return cls._texto_obligatorio(numero, "un numero de telefono", cls.MAX_NUMERO)

    @classmethod
    def validar_cargo(cls, cargo):
        return cls._texto_obligatorio(cargo, "un cargo", cls.MAX_CARGO)

    @classmethod
    def validar_correo(cls, correo):
        correo = cls._texto_obligatorio(correo, "un correo", cls.MAX_CORREO)
        if not cls.PATRON_CORREO.match(correo):
            raise ValueError(
                "El correo no es valido. Use el formato nombre@dominio.cl, "
                "por ejemplo ana@ecotech.example."
            )
        return correo.lower()

    @classmethod
    def validar_fecha_contrato(cls, valor):
        """Acepta date, datetime o texto AAAA-MM-DD y devuelve un date."""
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        if not isinstance(valor, str):
            raise TypeError("La fecha debe ser texto con formato AAAA-MM-DD.")
        valor = valor.strip()
        if not valor:
            raise ValueError("Ingrese una fecha. Es obligatoria.")
        try:
            return date.fromisoformat(valor)
        except ValueError:
            raise ValueError(
                "La fecha no es valida. Use el formato AAAA-MM-DD, "
                "por ejemplo 2026-03-15."
            ) from None

    @classmethod
    def validar_salario(cls, valor):
        """Acepta numero o texto (con coma o punto decimal); no negativo."""
        mensaje = "Ingrese solo numeros, por ejemplo 850000 o 850000.50."
        if isinstance(valor, bool) or valor is None:
            raise ValueError(mensaje)
        texto = str(valor).strip().replace(",", ".")
        if not texto:
            raise ValueError("Ingrese un salario. Es obligatorio.")
        try:
            numero = float(texto)
        except ValueError:
            raise ValueError(mensaje) from None
        if not math.isfinite(numero):          # rechaza nan e inf
            raise ValueError(mensaje)
        if numero < 0:
            raise ValueError("El salario no puede ser negativo.")
        return numero

    # ---------------------------------------------------------------- metodos
    def mostrar_datos(self):
        return f"{self._id} - {self._nombre} - {self._cargo} - {self._correo} - {self._direccion}"

    def ver_salario(self):
        return self._salario

    def registrar_horas(self, registro):
        if registro._empleado != self:
            raise ValueError("El registro pertenece a otro empleado")
        if registro._horas_trabajadas <= 0:
            raise ValueError("Las horas deben ser mayores que cero")
        if registro in self._registros_tiempo:
            raise ValueError("Este registro ya fue agregado")
        self._registros_tiempo.append(registro)
        total_horas = 0
        for registro_guardado in self._registros_tiempo:
            total_horas += registro_guardado._horas_trabajadas
        return total_horas
