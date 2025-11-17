from flask import Flask, session, redirect  
from controllers.auth_controller import auth_bp
import os

app = Flask(__name__,
            template_folder='views/templates',
            static_folder='views/static')
app.secret_key = os.urandom(24)  # Para sesiones seguras

# Registrar blueprint de autenticación
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    if 'user_id' in session:
        return "¡Sesión activa! User ID: " + str(session['user_id'])
    return redirect('/auth/login')  

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/auth/login')
    return f"Dashboard TaskU - Bienvenido {session.get('user_name')}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
