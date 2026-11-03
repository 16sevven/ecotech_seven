class Usuario:
    """Cuenta de acceso. Siempre pertenece a un Empleado (empleado_id).

    Guarda el hash de la contrasena, nunca la contrasena. Generar y
    verificar el hash es trabajo del servicio servicios/autenticacion.py.
    """
    MIN_USUARIO = 3
    MAX_USUARIO = 40
    MIN_CLAVE = 6

    def __init__(self, nombre_usuario, password_hash, empleado_id, id=None):
        if type(empleado_id) is not int or empleado_id <= 0:
            raise ValueError("El ID del empleado debe ser positivo.")
        if not isinstance(password_hash, str) or not password_hash:
            raise ValueError("Falta el hash de la contrasena.")
        self.id = id
        self.empleado_id = empleado_id
        self.nombre_usuario = self.normalizar_usuario(nombre_usuario)
        self.password_hash = password_hash
        self._permisos = []          # se conserva para GestionPermisos

    @classmethod
    def normalizar_usuario(cls, nombre):
        if not isinstance(nombre, str):
            raise TypeError("El usuario debe ser texto.")
        nombre = nombre.strip().lower()
        if not cls.MIN_USUARIO <= len(nombre) <= cls.MAX_USUARIO:
            raise ValueError(
                f"El usuario debe tener entre {cls.MIN_USUARIO} y {cls.MAX_USUARIO} caracteres."
            )
        if not all(c.isascii() and (c.isalnum() or c == "_") for c in nombre):
            raise ValueError("Use letras ASCII, numeros o guion bajo.")
        return nombre

    @classmethod
    def validar_clave(cls, clave):
        if not isinstance(clave, str):
            raise TypeError("La contrasena debe ser texto.")
        if len(clave) < cls.MIN_CLAVE:
            raise ValueError(f"Use al menos {cls.MIN_CLAVE} caracteres.")
        return clave                 # sin strip, lower ni truncado

    # --- permisos (dominio previo, sin cambios de reglas) ---
    def tiene_permiso(self, permiso):
        return permiso in self._permisos

    def agregar_permiso(self, permiso, otorgante):
        if not isinstance(permiso, str) or not permiso.strip():
            raise ValueError("El permiso no puede estar vacio")
        if "administrar_permisos" not in otorgante._permisos:
            raise PermissionError("No tiene autorizacion para otorgar permisos")
        permiso = permiso.strip()
        if permiso in self._permisos:
            return False
        self._permisos.append(permiso)
        return True
