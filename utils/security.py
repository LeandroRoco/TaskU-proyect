# utils/security.py
import bcrypt

class SecurityManager:
    """Gestiona la seguridad de contraseñas usando bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Encripta una contraseña usando bcrypt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        # Genera salt y hash en un solo paso
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash
        
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
            
        Returns:
            bool: True si coinciden, False si no
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))