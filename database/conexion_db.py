# conexion_db.py
# Archivo de conexión a la base de datos MySQL (TaskU)
# Requiere: pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error


class ConexionDB:
    """Clase para manejar la conexión a la base de datos TaskU"""
    
    # Configuración por defecto (puedes sobrescribir en __init__)
    CONFIG_DEFAULT = {
        'host': 'localhost',        # o 127.0.0.1
        'database': 'tasku',        # Base de datos actual
        'user': 'root',             # XAMPP por defecto
        'password': '',             # XAMPP no tiene contraseña
        'port': 3306                # XAMPP usa 3306 (NO 3307)
    }

    def obtener_ultimo_id(self):
        """Obtiene el ID del último INSERT"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo último ID: {e}")
            return None

    def __init__(self, **kwargs):
        """
        Inicializa la conexión. 
        Puedes pasar parámetros para sobrescribir la configuración:
        db = ConexionDB(port=3307, password='mi_clave')
        """
        self.config = {**self.CONFIG_DEFAULT, **kwargs}
        self.connection = None
        self.cursor = None

    def conectar(self):
        """Establece la conexión con la base de datos"""
        # Si ya hay conexión activa, no volver a conectar
        if self.connection and self.connection.is_connected():
            return True

        try:
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print(f"✅ Conexión exitosa a '{self.config['database']}' "
                      f"en {self.config['host']}:{self.config['port']}")
                return True

        except Error as e:
            print(f"❌ Error al conectar a MySQL: {e}")
            print(f"Configuración usada: {self.config}")
            return False

    def desconectar(self):
        """Cierra la conexión con la base de datos de forma segura"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("🔌 Conexión cerrada correctamente")
        except Error as e:
            print(f"⚠️ Error al cerrar conexión: {e}")

    def ejecutar_consulta(self, query, params=None):
        """
        Ejecuta una consulta SELECT y retorna los resultados
        Ejemplo: db.ejecutar_consulta("SELECT * FROM usuario WHERE email = %s", (email,))
        """
        if not self.conectar():
            return None
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"⚠️ Error al ejecutar consulta: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            return None
        finally:
            # No cerramos aquí para permitir múltiples consultas en la misma conexión
            pass

    def ejecutar_accion(self, query, params=None):
        """
        Ejecuta INSERT, UPDATE o DELETE
        Retorna True si tuvo éxito, False si falló
        """
        if not self.conectar():
            return False
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"⚠️ Error al ejecutar acción: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            self.connection.rollback()
            return False

    def obtener_ultimo_id(self):
        """Obtiene el ID del último registro insertado"""
        return self.cursor.lastrowid if self.cursor else None
    
    def obtener_ultimo_id(self):
        """Obtiene el ID del último INSERT"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo último ID: {e}")
            return None


# === Función de prueba ===
def probar_conexion():
    """Verifica la conexión y lista las tablas disponibles"""
    print("\n=== PRUEBA DE CONEXIÓN TASKU ===\n")
    
    db = ConexionDB()
    
    if db.conectar():
        print("✅ Conexión establecida correctamente\n")
        
        # Listar tablas
        tablas = db.ejecutar_consulta("SHOW TABLES")
        if tablas:
            print("Tablas en la base de datos:")
            for tabla in tablas:
                for nombre in tabla.values():
                    print(f"   - {nombre}")
                    
            # Si hay tabla 'usuario', mostrar cuántos registros tiene
            usuarios = db.ejecutar_consulta("SELECT COUNT(*) as total FROM usuario")
            if usuarios:
                print(f"\n👥 Usuarios registrados: {usuarios[0]['total']}")
        else:
            print("⚠️ No se encontraron tablas o la base de datos está vacía")
        
        db.desconectar()
        print("\n=== PRUEBA FINALIZADA ===")
        return True
    else:
        print("❌ No se pudo establecer la conexión")
        print("\n=== PRUEBA FALLIDA ===")
        return False


# === Ejemplo de uso ===
def ejemplo_crud():
    """Ejemplo de cómo usar la clase en tu proyecto"""
    db = ConexionDB()
    
    # INSERT
    query = "INSERT INTO usuario (nombre, email, password_hash) VALUES (%s, %s, %s)"
    db.ejecutar_accion(query, ("Marcelo Araya", "marcelo.araya@inacap.cl", "hash_de_prueba"))
    
    # SELECT
    usuarios = db.ejecutar_consulta("SELECT id, nombre FROM usuario WHERE email LIKE %s", ('%@inacap.cl',))
    for user in usuarios:
        print(f"ID: {user['id']} - Nombre: {user['nombre']}")
    
    # UPDATE
    db.ejecutar_accion("UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s", (1,))
    
    # DELETE
    db.ejecutar_accion("DELETE FROM usuario WHERE id = %s", (5,))
    
    db.desconectar()


# Si ejecutas este archivo directamente, prueba la conexión
if __name__ == "__main__":
    success = probar_conexion()
    # Si quieres ver el ejemplo CRUD, descomenta la línea siguiente:
    # ejemplo_crud()
    exit(0 if success else 1)

