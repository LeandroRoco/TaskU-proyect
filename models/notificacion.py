# models/notificacion.py
from database.conexion_db import ConexionDB

class NotificacionModel:
    """Modelo para notificaciones de recordatorio"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def crear_notificacion(self, tipo, mensaje, fecha_programada, evento_id, usuario_id):
        """Crea una notificación programada"""
        query = """
        INSERT INTO notificacion (tipo, mensaje, fecha_programada, evento_id, usuario_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (tipo, mensaje, fecha_programada, evento_id, usuario_id))
            notif_id = self.db.obtener_ultimo_id()
            self.db.desconectar()
            return notif_id
        except Exception as e:
            print(f"❌ Error creando notificación: {e}")
            return None
    
    def obtener_pendientes(self, usuario_id, limite=20):
        """Obtiene notificaciones no leídas"""
        query = """
        SELECT n.*, e.titulo as evento_titulo
        FROM notificacion n
        INNER JOIN evento e ON n.evento_id = e.id
        WHERE n.usuario_id = %s AND n.leida = 0
        ORDER BY n.fecha_programada ASC
        LIMIT %s
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id, limite))
        self.db.desconectar()
        
        return result
    
    def marcar_leida(self, notificacion_id):
        """Marca una notificación como leída"""
        query = "UPDATE notificacion SET leida = 1 WHERE id = %s"
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (notificacion_id,))
        self.db.desconectar()
        return success
    
    def eliminar_notificaciones_viejas(self, dias=30):
        """Elimina notificaciones leídas de más de X días"""
        query = """
        DELETE FROM notificacion 
        WHERE leida = 1 AND fecha_programada < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (dias,))
        self.db.desconectar()
        return success