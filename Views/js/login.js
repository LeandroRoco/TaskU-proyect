// login.js - Integración completa con Flask
(function () {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const loginMessage = document.getElementById('login-message');
  const registerMessage = document.getElementById('register-message');
  const loadingState = document.getElementById('loading-state');
  const authTabs = document.querySelectorAll('.auth-tab');
  const formPanels = document.querySelectorAll('.form-panel');

  // Helpers
  const showMsg = (element, msg, type = 'info') => {
    element.textContent = msg;
    element.style.color = type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : 'inherit';
    element.style.display = 'block';
  };

  const hideMsg = (element) => {
    element.style.display = 'none';
  };

  const showLoading = (show = true) => {
    loadingState.classList.toggle('show', show);
    document.querySelectorAll('.btn-text').forEach(btn => {
      btn.style.opacity = show ? '0' : '1';
    });
  };

  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isInacapEmail = (email) => 
    ['@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl'].some(d => email.toLowerCase().endsWith(d));

  // Switch Tabs
  authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetTab = tab.dataset.tab;
      
      authTabs.forEach(t => t.classList.remove('active'));
      formPanels.forEach(p => p.classList.remove('active'));
      
      tab.classList.add('active');
      document.getElementById(`${targetTab}-panel`).classList.add('active');
      
      // Limpiar mensajes
      hideMsg(loginMessage);
      hideMsg(registerMessage);
    });
  });

  // LOGIN
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMsg(loginMessage);
    showLoading(true);

    const email = loginForm.email.value.trim().toLowerCase();
    const password = loginForm.password.value;

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMsg(loginMessage, '✅ Acceso correcto. Redirigiendo...', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 1500);
      } else {
        showMsg(loginMessage, data.message || 'Error de autenticación', 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      showMsg(loginMessage, 'Error de conexión con el servidor', 'error');
    } finally {
      showLoading(false);
    }
  });

  // REGISTRO
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMsg(registerMessage);
    showLoading(true);

    const nombre = registerForm.nombre.value.trim();
    const email = registerForm.email.value.trim().toLowerCase();
    const password = registerForm.password.value;
    const confirmPassword = registerForm.confirm_password.value;

    // Validaciones frontend
    if (nombre.length < 3) {
      showMsg(registerMessage, 'El nombre debe tener al menos 3 caracteres', 'error');
      showLoading(false);
      return;
    }

    if (!isInacapEmail(email)) {
      showMsg(registerMessage, 'Usa tu correo institucional INACAP (@inacap.cl)', 'error');
      showLoading(false);
      return;
    }

    if (password.length < 6) {
      showMsg(registerMessage, 'La contraseña debe tener al menos 6 caracteres', 'error');
      showLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      showMsg(registerMessage, 'Las contraseñas no coinciden', 'error');
      showLoading(false);
      return;
    }

    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({nombre, email, password})
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMsg(registerMessage, data.message || '✅ Cuenta creada correctamente', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 2000);
      } else {
        showMsg(registerMessage, data.message || 'Error al crear cuenta', 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      showMsg(registerMessage, 'Error de conexión con el servidor', 'error');
    } finally {
      showLoading(false);
    }
  });

  // Validación en tiempo real para email
  registerForm.email.addEventListener('blur', () => {
    const email = registerForm.email.value.trim().toLowerCase();
    if (email && !isInacapEmail(email)) {
      showMsg(registerMessage, 'Usa @inacap.cl, @alumnos.inacap.cl o @profesor.inacap.cl', 'info');
    }
  });

  // Limpiar mensajes al escribir
  document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', (e) => {
      const form = e.target.closest('form');
      const msgElement = form.id === 'login-form' ? loginMessage : registerMessage;
      hideMsg(msgElement);
    });
  });
})();