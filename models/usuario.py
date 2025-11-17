# models/usuario.py
from database.conexion_db import ConexionDB
from utils.security import SecurityManager

class UsuarioModel:
    """Modelo para operaciones de usuario con encriptación bcrypt"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def validar_email_inacap(self, email):
        """Valida que el email sea institucional"""
        dominios_validos = ['@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl']
        return any(email.lower().endswith(dominio) for dominio in dominios_validos)
    
    def crear_usuario(self, nombre, email, password, rol='estudiante'):
        """Crea usuario con contraseña encriptada"""
        if not self.validar_email_inacap(email):
            raise ValueError("Correo debe ser institucional INACAP")
        
        # Verificar si ya existe
        if self.obtener_por_email(email):
            raise ValueError("El correo ya está registrado")
        
        hashed_password = SecurityManager.hash_password(password)
        
        query = """
        INSERT INTO usuario (nombre, email, password_hash, rol) 
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (nombre, email, hashed_password, rol))
            user_id = self.db.obtener_ultimo_id()
            self.db.desconectar()
            return user_id
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            return None
    
    def autenticar(self, email, password):
        """Autentica usuario verificando hash"""
        query = "SELECT id, nombre, email, password_hash, rol FROM usuario WHERE email = %s"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (email,))
        self.db.desconectar()
        
        if result and len(result) > 0:
            user = result[0]
            if SecurityManager.verify_password(password, user['password_hash']):
                del user['password_hash']  # NUNCA enviar el hash
                return user
        return None
    
    def obtener_por_email(self, email):
        """Busca usuario por email (para verificar duplicados)"""
        query = "SELECT id, email FROM usuario WHERE email = %s"
    
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (email,))
        self.db.desconectar()
    
        return result[0] if result else None
    
    def obtener_por_id(self, user_id):
        """Obtiene usuario por ID (para sesiones)"""
        query = "SELECT id, nombre, email, rol, fecha_registro FROM usuario WHERE id = %s"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (user_id,))
        self.db.desconectar()
        
        return result[0] if result else None
    
    def actualizar_ultimo_acceso(self, user_id):
        """Actualiza la fecha de último acceso"""
        query = "UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s"
        
        self.db.conectar()
        success = self.db.ejecutar_accion(query, (user_id,))
        self.db.desconectar()
        return success