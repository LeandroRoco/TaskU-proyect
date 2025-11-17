from flask import Flask, session, redirect, url_for, render_template
from controllers.auth_controller import auth_bp
import os

app = Flask(__name__,
            template_folder='views/templates',
            static_folder='views/static')
app.secret_key = os.urandom(24)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    """Ruta principal"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard del usuario con datos dinámicos"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard.html', 
                         nombre=session.get('user_name'),
                         email=session.get('user_email'),
                         rol=session.get('user_rol'))

if __name__ == '__main__':
    app.run(debug=True)