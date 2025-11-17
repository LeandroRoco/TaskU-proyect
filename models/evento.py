# models/evento.py
from database.conexion_db import ConexionDB
from datetime import datetime

class EventoModel:
    """Modelo para tareas, exámenes, proyectos y eventos académicos"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def crear_evento(self, titulo, descripcion, fecha_limite, prioridad, 
                     tipo, usuario_id, asignatura_id=None):
        """Crea un nuevo evento/tarea"""
        # Validar que la fecha no sea en el pasado
        fecha_limite_dt = datetime.strptime(fecha_limite, '%Y-%m-%d %H:%M:%S')
        if fecha_limite_dt < datetime.now():
            raise ValueError("La fecha límite no puede ser en el pasado")
        
        query = """
        INSERT INTO evento (titulo, descripcion, fecha_limite, prioridad, tipo, usuario_id, asignatura_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (titulo, descripcion, fecha_limite, 
                                           prioridad, tipo, usuario_id, asignatura_id))
            evento_id = self.db.obtener_ultimo_id()
            self.db.desconectar()
            
            # Crear notificación automática
            self.crear_notificacion_automatica(evento_id, fecha_limite_dt, usuario_id)
            
            return evento_id
        except Exception as e:
            print(f"❌ Error creando evento: {e}")
            return None
    
    def obtener_por_usuario(self, usuario_id, estado=None, limite=50):
        """Obtiene eventos de un usuario con filtros"""
        query = """
        SELECT e.*, a.nombre as asignatura_nombre, a.codigo as asignatura_codigo
        FROM evento e
        LEFT JOIN asignatura a ON e.asignatura_id = a.id
        WHERE e.usuario_id = %s
        """
        params = [usuario_id]
        
        if estado:
            query += " AND e.estado = %s"
            params.append(estado)
            
        query += " ORDER BY e.fecha_limite ASC LIMIT %s"
        params.append(limite)
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, tuple(params))
        self.db.desconectar()
        
        return result
    
    def obtener_urgentes(self, usuario_id):
        """Obtiene eventos urgentes (próximos 24h o vencidos)"""
        query = """
        SELECT e.*, a.nombre as asignatura_nombre
        FROM evento e
        LEFT JOIN asignatura a ON e.asignatura_id = a.id
        WHERE e.usuario_id = %s 
        AND e.estado = 'pendiente'
        AND (fecha_limite <= DATE_ADD(NOW(), INTERVAL 24 HOUR) 
             OR fecha_limite < NOW())
        ORDER BY fecha_limite ASC
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id,))
        self.db.desconectar()
        
        return result
    
    def completar_evento(self, evento_id, usuario_id):
        """Marca un evento como completado"""
        query = """
        UPDATE evento 
        SET estado = 'completada', fecha_actualizacion = NOW()
        WHERE id = %s AND usuario_id = %s
        """
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (evento_id, usuario_id))
        self.db.desconectar()
        return success
    
    def actualizar_evento(self, evento_id, datos):
        """Actualiza información del evento"""
        campos = []
        valores = []
        for campo, valor in datos.items():
            campos.append(f"{campo} = %s")
            valores.append(valor)
        
        valores.append(evento_id)
        
        query = f"""
        UPDATE evento 
        SET {', '.join(campos)}, fecha_actualizacion = NOW()
        WHERE id = %s
        """
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, tuple(valores))
        self.db.desconectar()
        return success
    
    def eliminar_evento(self, evento_id, usuario_id):
        """Elimina un evento (solo si pertenece al usuario)"""
        query = "DELETE FROM evento WHERE id = %s AND usuario_id = %s"
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (evento_id, usuario_id))
        self.db.desconectar()
        return success
    
    def estadisticas_usuario(self, usuario_id):
        """Obtiene estadísticas de eventos del usuario"""
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as completadas,
            SUM(CASE WHEN fecha_limite < NOW() AND estado = 'pendiente' THEN 1 ELSE 0 END) as vencidas,
            SUM(CASE WHEN prioridad = 'alta' AND estado = 'pendiente' THEN 1 ELSE 0 END) as urgentes
        FROM evento
        WHERE usuario_id = %s
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id,))
        self.db.desconectar()
        
        return result[0] if result else None
    
    def crear_notificacion_automatica(self, evento_id, fecha_limite, usuario_id):
        """Crea notificación automática para eventos"""
        # Notificación 24h antes
        from models.notificacion import NotificacionModel
        notif_model = NotificacionModel()
        
        notif_model.crear_notificacion(
            tipo='recordatorio_24h',
            mensaje=f'Recordatorio: Tarea vence en 24 horas',
            fecha_programada=fecha_limite.replace(hour=fecha_limute.hour-24),
            evento_id=evento_id,
            usuario_id=usuario_id
        )