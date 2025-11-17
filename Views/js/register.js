// register.js - Registro de usuarios INACAP con validaciones y conexión Flask
(function () {
  const registerForm = document.getElementById('register-form');
  const messageEl = document.getElementById('register-message');
  const loadingState = document.getElementById('loading-state');

  // Helpers
  const showMessage = (msg, type = 'info') => {
    messageEl.textContent = msg;
    messageEl.style.color = type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : 'inherit';
    messageEl.style.display = 'block';
    messageEl.setAttribute('aria-live', 'polite');
  };

  const hideMessage = () => {
    messageEl.style.display = 'none';
    messageEl.textContent = '';
  };

  const showLoading = (show = true) => {
    loadingState.classList.toggle('show', show);
    const button = registerForm.querySelector('button[type="submit"]');
    button.disabled = show;
    button.style.opacity = show ? '0.7' : '1';
  };

  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  
  const isInacapEmail = (email) => 
    ['@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl'].some(d => email.toLowerCase().endsWith(d));

  // Validación en tiempo real
  const inputs = {
    nombre: document.getElementById('register-name'),
    email: document.getElementById('register-email'),
    password: document.getElementById('register-password'),
    confirm: document.getElementById('register-confirm')
  };

  inputs.nombre.addEventListener('blur', () => {
    if (inputs.nombre.value.trim().length < 3) {
      inputs.nombre.style.borderColor = '#dc3545';
    } else {
      inputs.nombre.style.borderColor = '#28a745';
    }
  });

  inputs.email.addEventListener('blur', () => {
    const email = inputs.email.value.trim().toLowerCase();
    if (!isInacapEmail(email)) {
      showMessage('Usa tu correo institucional INACAP', 'error');
      inputs.email.style.borderColor = '#dc3545';
    } else {
      hideMessage();
      inputs.email.style.borderColor = '#28a745';
    }
  });

  inputs.password.addEventListener('input', () => {
    const password = inputs.password.value;
    if (password.length < 6) {
      inputs.password.style.borderColor = '#dc3545';
    } else {
      inputs.password.style.borderColor = '#28a745';
    }
  });

  inputs.confirm.addEventListener('input', () => {
    if (inputs.confirm.value !== inputs.password.value) {
      inputs.confirm.style.borderColor = '#dc3545';
    } else {
      inputs.confirm.style.borderColor = '#28a745';
    }
  });

  // Submit del formulario
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessage();
    showLoading(true);

    const nombre = inputs.nombre.value.trim();
    const email = inputs.email.value.trim().toLowerCase();
    const password = inputs.password.value;
    const confirmPassword = inputs.confirm.value;

    // Validaciones completas
    const errores = [];

    if (nombre.length < 3) {
      errores.push('El nombre debe tener al menos 3 caracteres');
    }

    if (!isValidEmail(email)) {
      errores.push('Correo electrónico inválido');
    }

    if (!isInacapEmail(email)) {
      errores.push('Debe ser un correo institucional INACAP (@inacap.cl, @alumnos.inacap.cl, @profesor.inacap.cl)');
    }

    if (password.length < 6) {
      errores.push('La contraseña debe tener al menos 6 caracteres');
    }

    if (password !== confirmPassword) {
      errores.push('Las contraseñas no coinciden');
    }

    if (errores.length > 0) {
      showMessage(errores.join(' | '), 'error');
      showLoading(false);
      return;
    }

    // Enviar al backend Flask
    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify({ nombre, email, password })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMessage('✅ Cuenta creada exitosamente. Redirigiendo...', 'success');
        
        // Auto-login después de 2 segundos
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 2000);
      } else {
        showMessage(data.message || 'Error al crear la cuenta', 'error');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      showMessage('Error de conexión con el servidor. Verifica tu conexión.', 'error');
    } finally {
      showLoading(false);
    }
  });

  // Limpiar mensajes al enfocar inputs
  Object.values(inputs).forEach(input => {
    input.addEventListener('focus', hideMessage);
  });

  // Mostrar/ocultar contraseña
  const togglePasswordButtons = document.createElement('div');
  togglePasswordButtons.innerHTML = `
    <style>
      .password-toggle {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: var(--inst-gray);
        font-size: 18px;
        user-select: none;
      }
      .form-group { position: relative; }
    </style>
  `;
  document.body.appendChild(togglePasswordButtons);

  const createToggle = (inputId, icon = '👁️') => {
    const input = document.getElementById(inputId);
    const wrapper = input.parentElement;
    const toggle = document.createElement('span');
    toggle.className = 'password-toggle';
    toggle.textContent = icon;
    toggle.addEventListener('click', () => {
      input.type = input.type === 'password' ? 'text' : 'password';
      toggle.textContent = input.type === 'password' ? '👁️' : '🙈';
    });
    wrapper.style.position = 'relative';
    wrapper.appendChild(toggle);
  };

  createToggle('register-password');
  createToggle('register-confirm');
})();