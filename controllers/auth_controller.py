# controllers/auth_controller.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from models.usuario import UsuarioModel

auth_bp = Blueprint('auth', __name__)
usuario_model = UsuarioModel()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja login de usuario INACAP"""
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Validación INACAP
        if not email.endswith(('@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl')):
            return jsonify({'success': False, 'message': 'Usa tu correo institucional INACAP'}), 401
        
        user = usuario_model.autenticar(email, password)
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            return jsonify({'success': True, 'redirect': '/dashboard'})
        
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja registro de nuevos usuarios INACAP"""
    if request.method == 'GET':
        return render_template('login.html')  # Misma plantilla
    
    if request.method == 'POST':
        data = request.get_json()
        nombre = data.get('nombre')
        email = data.get('email')
        password = data.get('password')
        
        # Validaciones
        if not nombre or len(nombre) < 3:
            return jsonify({'success': False, 'message': 'Nombre debe tener al menos 3 caracteres'}), 400
        
        if not email.endswith(('@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl')):
            return jsonify({'success': False, 'message': 'Correo institucional INACAP inválido'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': 'Contraseña debe tener al menos 6 caracteres'}), 400
        
        # Verificar si usuario ya existe
        if usuario_model.obtener_por_email(email):
            return jsonify({'success': False, 'message': 'El correo ya está registrado'}), 400
        
        # Crear usuario
        user_id = usuario_model.crear_usuario(nombre, email, password)
        
        if user_id:
            # Auto-login después de registro
            user = usuario_model.obtener_por_id(user_id)
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            return jsonify({'success': True, 'redirect': '/dashboard', 'message': 'Cuenta creada exitosamente'})
        
        return jsonify({'success': False, 'message': 'Error al crear la cuenta'}), 500

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register-page')
def register_page():
    """Muestra la página de registro"""
    return render_template('register.html')