from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from models.usuario import UsuarioModel

auth_bp = Blueprint('auth', __name__)
usuario_model = UsuarioModel()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja login de usuario INACAP"""
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'error')
            return redirect(url_for('auth.login'))
        
        user = usuario_model.autenticar(email, password)
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['user_email'] = user['email']
            session['user_rol'] = user.get('rol', 'estudiante')
            
            # Actualizar último acceso
            usuario_model.actualizar_ultimo_acceso(user['id'])
            
            # ✅ REDIRIGE AL DASHBOARD
            return redirect(url_for('dashboard'))
        
        flash('Credenciales inválidas', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja registro de nuevos usuarios INACAP"""
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validaciones
        if not nombre or len(nombre) < 3:
            flash('Nombre debe tener al menos 3 caracteres', 'error')
            return redirect(url_for('auth.register'))
        
        if not usuario_model.validar_email_inacap(email):
            flash('Usa tu correo institucional INACAP', 'error')
            return redirect(url_for('auth.register'))
        
        if not password or len(password) < 6:
            flash('Contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('auth.register'))
        
        # Verificar si usuario ya existe
        if usuario_model.obtener_por_email(email):
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('auth.register'))
        
        # Crear usuario
        try:
            user_id = usuario_model.crear_usuario(nombre, email, password)
            if user_id:
                flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Error al crear la cuenta', 'error')
                return redirect(url_for('auth.register'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('auth.register'))

@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('auth.login'))