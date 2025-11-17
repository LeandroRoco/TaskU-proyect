# models/asignatura.py
from database.conexion_db import ConexionDB

class AsignaturaModel:
    """Modelo para gestión de asignaturas INACAP"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def crear_asignatura(self, nombre, codigo, color="#CC0000", icono="📚"):
        """Crea una nueva asignatura"""
        query = """
        INSERT INTO asignatura (nombre, codigo, color, icono)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (nombre, codigo, color, icono))
            asignatura_id = self.db.obtener_ultimo_id()
            self.db.desconectar()
            return asignatura_id
        except Exception as e:
            print(f"❌ Error creando asignatura: {e}")
            return None
    
    def obtener_todas(self):
        """Obtiene todas las asignaturas disponibles"""
        query = "SELECT * FROM asignatura ORDER BY nombre"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query)
        self.db.desconectar()
        
        return result
    
    def obtener_por_id(self, asignatura_id):
        """Obtiene una asignatura específica"""
        query = "SELECT * FROM asignatura WHERE id = %s"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (asignatura_id,))
        self.db.desconectar()
        
        return result[0] if result else None
    
    def asignar_a_usuario(self, usuario_id, asignatura_id):
        """Asocia una asignatura a un usuario"""
        query = """
        INSERT INTO usuario_has_asignatura (usuario_id, asignatura_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE usuario_id = usuario_id
        """
        try:
            self.db.conectar()
            success = self.db.ejecutar_accion(query, (usuario_id, asignatura_id))
            self.db.desconectar()
            return success
        except Exception as e:
            print(f"❌ Error asignando asignatura: {e}")
            return False
    
    def obtener_por_usuario(self, usuario_id):
        """Obtiene las asignaturas de un usuario específico"""
        query = """
        SELECT a.* FROM asignatura a
        INNER JOIN usuario_has_asignatura ua ON a.id = ua.asignatura_id
        WHERE ua.usuario_id = %s
        ORDER BY a.nombre
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id,))
        self.db.desconectar()
        
        return result
    
    def eliminar_asignatura(self, asignatura_id):
        """Elimina una asignatura (solo admin)"""
        query = "DELETE FROM asignatura WHERE id = %s"
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (asignatura_id,))
        self.db.desconectar()
        return success