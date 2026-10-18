from persistencia.conexion import abrir_conexion, obtener_motor


def _asegurar_correo_unico(cursor):
    """Respalda en la base de datos la regla 'un correo = un empleado'.

    Se crea como indice UNIQUE aparte (en vez de ponerlo dentro del
    CREATE TABLE) para que tambien se aplique en bases que ya existian,
    ya que CREATE TABLE IF NOT EXISTS no modifica tablas antiguas.
    """
    try:
        if obtener_motor() == "sqlite":
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_empleado_correo "
                "ON empleado(correo)"
            )
        else:
            cursor.execute(
                "SHOW INDEX FROM empleado WHERE Key_name = 'ux_empleado_correo'"
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    "CREATE UNIQUE INDEX ux_empleado_correo ON empleado(correo)"
                )
    except Exception as error:
        print("Aviso: no se pudo crear la restriccion UNIQUE del correo "
              "(puede haber correos repetidos en la tabla empleado).")
        print("Detalle:", error)


def crear_tablas():
    conexion = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        if obtener_motor() == "sqlite":
            tablas = [
                """CREATE TABLE IF NOT EXISTS empleado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    direccion TEXT NOT NULL,
                    numero TEXT NOT NULL,
                    correo TEXT NOT NULL,
                    fecha_contrato TEXT NOT NULL,
                    salario REAL NOT NULL,
                    cargo TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS departamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    id_gerente INTEGER
                )""",
                """CREATE TABLE IF NOT EXISTS proyecto (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha_inicio TEXT NOT NULL,
                    descripcion TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS registro_tiempo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    horas_trabajadas INTEGER NOT NULL CHECK (horas_trabajadas > 0),
                    fecha_trabajada TEXT NOT NULL,
                    descripcion_tarea TEXT NOT NULL,
                    empleado_id INTEGER NOT NULL,
                    proyecto_id INTEGER NOT NULL,
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                )""",
                """CREATE TABLE IF NOT EXISTS departamento_empleado (
                    departamento_id INTEGER NOT NULL,
                    empleado_id INTEGER NOT NULL,
                    PRIMARY KEY (departamento_id, empleado_id),
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                )""",
                """CREATE TABLE IF NOT EXISTS departamento_proyecto (
                    departamento_id INTEGER NOT NULL,
                    proyecto_id INTEGER NOT NULL,
                    PRIMARY KEY (departamento_id, proyecto_id),
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                )""",
                """CREATE TABLE IF NOT EXISTS proyecto_empleado (
                    proyecto_id INTEGER NOT NULL,
                    empleado_id INTEGER NOT NULL,
                    PRIMARY KEY (proyecto_id, empleado_id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id),
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                )"""
            ]
        else:
            tablas = [
                """CREATE TABLE IF NOT EXISTS empleado (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    direccion VARCHAR(200) NOT NULL,
                    numero VARCHAR(30) NOT NULL,
                    correo VARCHAR(150) NOT NULL,
                    fecha_contrato DATE NOT NULL,
                    salario DECIMAL(12, 2) NOT NULL,
                    cargo VARCHAR(100) NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS departamento (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    id_gerente INT
                )""",
                """CREATE TABLE IF NOT EXISTS proyecto (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    descripcion TEXT NOT NULL
                )""",
                """CREATE TABLE IF NOT EXISTS registro_tiempo (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    horas_trabajadas INT NOT NULL,
                    fecha_trabajada DATE NOT NULL,
                    descripcion_tarea TEXT NOT NULL,
                    empleado_id INT NOT NULL,
                    proyecto_id INT NOT NULL,
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                )""",
                """CREATE TABLE IF NOT EXISTS departamento_empleado (
                    departamento_id INT NOT NULL,
                    empleado_id INT NOT NULL,
                    PRIMARY KEY (departamento_id, empleado_id),
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                )""",
                """CREATE TABLE IF NOT EXISTS departamento_proyecto (
                    departamento_id INT NOT NULL,
                    proyecto_id INT NOT NULL,
                    PRIMARY KEY (departamento_id, proyecto_id),
                    FOREIGN KEY (departamento_id) REFERENCES departamento(id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id)
                )""",
                """CREATE TABLE IF NOT EXISTS proyecto_empleado (
                    proyecto_id INT NOT NULL,
                    empleado_id INT NOT NULL,
                    PRIMARY KEY (proyecto_id, empleado_id),
                    FOREIGN KEY (proyecto_id) REFERENCES proyecto(id),
                    FOREIGN KEY (empleado_id) REFERENCES empleado(id)
                )"""
            ]
        for sql in tablas:
            cursor.execute(sql)
        _asegurar_correo_unico(cursor)
        conexion.commit()
    except Exception:
        if conexion:
            conexion.rollback()
        raise
    finally:
        if conexion:
            conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Tablas de EcoTech preparadas correctamente.")
