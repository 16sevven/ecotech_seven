from persistencia.conexion import abrir_conexion, marcador_sql
from dominio.usuario import Usuario


class UsuarioDAO:
    COLUMNAS = "id, nombre_usuario, password_hash, empleado_id"

    @staticmethod
    def _fila_a_usuario(fila):
        return Usuario(
            nombre_usuario=fila[1],
            password_hash=fila[2],
            empleado_id=fila[3],
            id=fila[0],
        )

    @staticmethod
    def insertar(usuario):
        """Guarda la cuenta y devuelve su ID."""
        conexion = None
        try:
            conexion = abrir_conexion()
            cursor = conexion.cursor()
            marca = marcador_sql()
            cursor.execute(
                "INSERT INTO usuario (nombre_usuario, password_hash, empleado_id) "
                f"VALUES ({marca}, {marca}, {marca})",
                (usuario.nombre_usuario, usuario.password_hash, usuario.empleado_id),
            )
            conexion.commit()
            usuario.id = cursor.lastrowid
            return usuario.id
        except Exception:
            if conexion:
                conexion.rollback()
            raise
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def _buscar(columna, valor):
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            marca = marcador_sql()
            # 'columna' viene de este archivo (nunca del usuario); el valor va parametrizado
            cursor.execute(
                f"SELECT {UsuarioDAO.COLUMNAS} FROM usuario WHERE {columna} = {marca}",
                (valor,),
            )
            fila = cursor.fetchone()
        finally:
            conexion.close()
        return None if fila is None else UsuarioDAO._fila_a_usuario(fila)

    @staticmethod
    def buscar_por_nombre(nombre_usuario):
        return UsuarioDAO._buscar("nombre_usuario", nombre_usuario)

    @staticmethod
    def buscar_por_empleado(empleado_id):
        return UsuarioDAO._buscar("empleado_id", empleado_id)

    @staticmethod
    def hay_cuentas():
        conexion = abrir_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuario")
            return cursor.fetchone()[0] > 0
        finally:
            conexion.close()
