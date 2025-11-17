# models/evento.py CORREGIDO
from database.conexion_db import ConexionDB
from datetime import datetime, timedelta

class EventoModel:
    """Modelo para tareas, exámenes, proyectos y eventos académicos"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def crear_evento(self, titulo, descripcion, fecha_limite, prioridad, 
                     tipo, usuario_id, asignatura_id=None):
        """Crea un nuevo evento/tarea"""
        # Convertir string a datetime si es necesario
        if isinstance(fecha_limite, str):
            fecha_limite_dt = datetime.strptime(fecha_limite, '%Y-%m-%dT%H:%M')
        else:
            fecha_limite_dt = fecha_limite
        
        # Validar que la fecha no sea en el pasado
        if fecha_limite_dt < datetime.now():
            raise ValueError("La fecha límite no puede ser en el pasado")
        
        # Convertir datetime a string para MySQL
        fecha_limite_str = fecha_limite_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
        INSERT INTO evento (titulo, descripcion, fecha_limite, prioridad, tipo, usuario_id, asignatura_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (titulo, descripcion, fecha_limite_str, 
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
        SELECT e.*, a.nombre as asignatura_nombre, a.codigo as asignatura_codigo, a.color as asignatura_color
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
        
        return result if result else []
    
    def obtener_urgentes(self, usuario_id):
        """Obtiene eventos urgentes (próximos 48h o vencidos)"""
        query = """
        SELECT e.*, a.nombre as asignatura_nombre, a.color as asignatura_color
        FROM evento e
        LEFT JOIN asignatura a ON e.asignatura_id = a.id
        WHERE e.usuario_id = %s 
        AND e.estado = 'pendiente'
        AND fecha_limite <= DATE_ADD(NOW(), INTERVAL 48 HOUR)
        ORDER BY fecha_limite ASC
        LIMIT 10
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id,))
        self.db.desconectar()
        
        return result if result else []
    
    def obtener_proximas_vencer(self, usuario_id, horas=24):
        """Obtiene tareas que vencen en las próximas X horas"""
        query = """
        SELECT e.*, a.nombre as asignatura_nombre
        FROM evento e
        LEFT JOIN asignatura a ON e.asignatura_id = a.id
        WHERE e.usuario_id = %s 
        AND e.estado = 'pendiente'
        AND fecha_limite BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s HOUR)
        ORDER BY fecha_limite ASC
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id, horas))
        self.db.desconectar()
        
        return result if result else []
    
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
            if campo not in ['id', 'usuario_id', 'fecha_creacion']:  # Campos protegidos
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
            
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
            SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
            SUM(CASE WHEN fecha_limite < NOW() AND estado = 'pendiente' THEN 1 ELSE 0 END) as vencidas,
            SUM(CASE WHEN prioridad = 'alta' AND estado = 'pendiente' THEN 1 ELSE 0 END) as urgentes,
            SUM(CASE WHEN fecha_limite BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 48 HOUR) 
                AND estado = 'pendiente' THEN 1 ELSE 0 END) as proximas_vencer
        FROM evento
        WHERE usuario_id = %s
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id,))
        self.db.desconectar()
        
        return result[0] if result else {
            'total': 0,
            'completadas': 0,
            'pendientes': 0,
            'vencidas': 0,
            'urgentes': 0,
            'proximas_vencer': 0
        }
    
    def obtener_por_mes(self, usuario_id, año, mes):
        """Obtiene eventos de un mes específico para el calendario"""
        query = """
        SELECT e.*, a.nombre as asignatura_nombre, a.color as asignatura_color
        FROM evento e
        LEFT JOIN asignatura a ON e.asignatura_id = a.id
        WHERE e.usuario_id = %s
        AND YEAR(e.fecha_limite) = %s
        AND MONTH(e.fecha_limite) = %s
        ORDER BY e.fecha_limite ASC
        """
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (usuario_id, año, mes))
        self.db.desconectar()
        
        return result if result else []
    
    def crear_notificacion_automatica(self, evento_id, fecha_limite, usuario_id):
        """Crea notificación automática para eventos"""
        try:
            from models.notificacion import NotificacionModel
            notif_model = NotificacionModel()
            
            # Calcular fecha para notificación (24 horas antes)
            fecha_notif = fecha_limite - timedelta(hours=24)
            
            # Solo crear si la fecha de notificación es futura
            if fecha_notif > datetime.now():
                fecha_notif_str = fecha_notif.strftime('%Y-%m-%d %H:%M:%S')
                
                notif_model.crear_notificacion(
                    tipo='recordatorio_24h',
                    mensaje=f'Recordatorio: Tarea vence en 24 horas',
                    fecha_programada=fecha_notif_str,
                    evento_id=evento_id,
                    usuario_id=usuario_id
                )
        except Exception as e:
            print(f"⚠️ No se pudo crear notificación: {e}")
            # No falla la creación del evento si falla la notificación