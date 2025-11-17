# models/usuario.py
from database.conexion_db
from utils.security import SecurityManager

class UsuarioModel:
    """Modelo para operaciones de usuario con encriptación bcrypt"""
    
    def __init__(self):
        self.db = ConexionDB()
    
    def crear_usuario(self, nombre, email, password):
        """Crea usuario con contraseña encriptada"""
        hashed_password = SecurityManager.hash_password(password)
        
        query = """
        INSERT INTO usuario (nombre, email, password_hash) 
        VALUES (%s, %s, %s)
        """
        try:
            self.db.conectar()
            self.db.ejecutar_accion(query, (nombre, email, hashed_password))
            self.db.desconectar()
            return True
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            return False
    
    def autenticar(self, email, password):
        """Autentica usuario verificando hash"""
        query = "SELECT id, nombre, email, password_hash FROM usuario WHERE email = %s"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (email,))
        self.db.desconectar()
        
        if result and len(result) > 0:
            user = result[0]
            if SecurityManager.verify_password(password, user['password_hash']):
                del user['password_hash']  # NUNCA enviar el hash
                return user
        return None
    
    def obtener_por_id(self, user_id):
        """Obtiene usuario por ID (para sesiones)"""
        query = "SELECT id, nombre, email FROM usuario WHERE id = %s"
        
        self.db.conectar()
        result = self.db.ejecutar_consulta(query, (user_id,))
        self.db.desconectar()
        
        return result[0] if result else None