/**
 * TaskU - Organizador de Tareas Estudiantil INACAP
 * Archivo: js/app.js
 * Funcionalidad principal de la aplicación
 */

// === CONFIGURACIÓN GLOBAL ===
const APP_CONFIG = {
    animations: true,
    debugMode: false,
    institution: 'INACAP',
    defaultSubjects: {
        'integracion': 'Integración de Proyecto',
        'bd': 'Base de Datos',
        'movil': 'Desarrollo Móvil',
        'seguridad': 'Seguridad de la Información',
        'redes': 'Redes de Computadores',
        'algoritmos': 'Algoritmos y Estructuras'
    },
    welcomeMessages: [
        '¡Bienvenido a TaskU INACAP!',
        '¡Hola estudiante INACAP!',
        '¡Organiza tu éxito académico!',
        '¡Tu productividad académica empieza aquí!'
    ]
};

// === ESTADO GLOBAL DE LA APLICACIÓN ===
let appState = {
    currentUser: null,
    tasks: [],
    currentView: 'login-view',
    isLoading: false,
    institution: 'INACAP'
};

// === FUNCIONES DE NAVEGACIÓN ===

/**
 * Muestra una vista específica y oculta las demás
 * @param {string} viewId - ID de la vista a mostrar
 */
function showView(viewId) {
    try {
        // Ocultar todas las vistas
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Mostrar la vista seleccionada
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.add('active');
            appState.currentView = viewId;
            
            // Actualizar navegación
            updateNavigation(viewId);
            
            // Trigger eventos específicos por vista
            handleViewChange(viewId);
            
            if (APP_CONFIG.debugMode) {
                console.log(`Vista cambiada a: ${viewId}`);
            }
        } else {
            console.error(`Vista no encontrada: ${viewId}`);
        }
    } catch (error) {
        console.error('Error al cambiar vista:', error);
        showErrorMessage('Error al navegar. Intenta de nuevo.');
    }
}

/**
 * Actualiza la navegación visual según la vista activa
 * @param {string} activeViewId - Vista actualmente activa
 */
function updateNavigation(activeViewId) {
    // Limpiar navegación activa
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Mapeo de vistas a índices de navegación
    const navMapping = {
        'dashboard-view': 0,
        'create-view': 1,
        'calendar-view': 2
    };
    
    const navIndex = navMapping[activeViewId];
    if (navIndex !== undefined) {
        const navItems = document.querySelectorAll('.nav-item');
        if (navItems[navIndex]) {
            navItems[navIndex].classList.add('active');
        }
    }
}

/**
 * Maneja eventos específicos cuando cambia la vista
 * @param {string} viewId - ID de la nueva vista
 */
function handleViewChange(viewId) {
    switch(viewId) {
        case 'dashboard-view':
            loadDashboardData();
            break;
        case 'create-view':
            resetTaskForm();
            setDefaultDate();
            break;
        case 'calendar-view':
            loadCalendarData();
            break;
    }
}

// === FUNCIONES DE AUTENTICACIÓN ===

/**
 * Maneja el proceso de login
 * @param {Event} event - Evento del formulario
 */
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validación básica
    if (!email || !password) {
        showErrorMessage('Por favor completa todos los campos.');
        return;
    }
    
    if (!isValidEmail(email)) {
        showErrorMessage('Por favor ingresa un correo válido de INACAP.');
        return;
    }
    
    // Verificar que sea un email de INACAP
    if (!email.toLowerCase().includes('inacap.cl')) {
        showErrorMessage('Debes usar tu correo institucional de INACAP.');
        return;
    }
    
    // Simular proceso de autenticación
    showLoadingMessage('Iniciando sesión en TaskU INACAP...');
    
    setTimeout(() => {
        hideLoadingMessage();
        
        // Simular autenticación exitosa
        appState.currentUser = {
            email: email,
            name: getNameFromEmail(email),
            initials: getInitialsFromEmail(email),
            institution: 'INACAP'
        };
        
        // Actualizar UI con datos del usuario
        updateUserInterface();
        
        // Navegar al dashboard
        showView('dashboard-view');
        
        // Mensaje de bienvenida aleatorio
        const welcomeMsg = APP_CONFIG.welcomeMessages[Math.floor(Math.random() * APP_CONFIG.welcomeMessages.length)];
        showSuccessMessage(welcomeMsg);
        
    }, 1500);
}

/**
 * Cierra la sesión del usuario
 */
function logout() {
    if (confirm('¿Deseas cerrar sesión de TaskU INACAP?')) {
        showLoadingMessage('Cerrando sesión...');
        
        setTimeout(() => {
            hideLoadingMessage();
            
            // Limpiar estado
            appState.currentUser = null;
            appState.tasks = [];
            
            // Limpiar formularios
            document.getElementById('login-form').reset();
            resetTaskForm();
            
            // Volver al login
            showView('login-view');
            showSuccessMessage('Sesión cerrada exitosamente.');
        }, 1000);
    }
}

// === FUNCIONES DE GESTIÓN DE TAREAS ===

/**
 * Crea una nueva tarea
 */
function createTask() {
    const formData = getTaskFormData();
    
    // Validación
    if (!validateTaskForm(formData)) {
        return;
    }
    
    showLoadingMessage('Creando tarea académica...');
    
    setTimeout(() => {
        hideLoadingMessage();
        
        // Crear objeto de tarea
        const newTask = {
            id: generateTaskId(),
            title: formData.title,
            subject: formData.subject,
            date: new Date(formData.date),
            priority: formData.priority,
            description: formData.description,
            status: 'pending',
            createdAt: new Date(),
            institution: 'INACAP'
        };
        
        // Agregar a estado global
        appState.tasks.push(newTask);
        
        // Actualizar UI
        addTaskToUI(newTask);
        updateStats();
        
        // Limpiar formulario y volver al dashboard
        resetTaskForm();
        showView('dashboard-view');
        showSuccessMessage('Tarea académica creada exitosamente');
        
        if (APP_CONFIG.debugMode) {
            console.log('Nueva tarea creada:', newTask);
        }
    }, 1000);
}

/**
 * Obtiene los datos del formulario de tareas
 * @returns {Object} Datos del formulario
 */
function getTaskFormData() {
    return {
        title: document.getElementById('task-title').value.trim(),
        subject: document.getElementById('task-subject').value,
        date: document.getElementById('task-date').value,
        priority: document.getElementById('task-priority').value,
        description: document.getElementById('task-description').value.trim()
    };
}

/**
 * Valida los datos del formulario de tareas
 * @param {Object} formData - Datos a validar
 * @returns {boolean} True si es válido
 */
function validateTaskForm(formData) {
    if (!formData.title) {
        showErrorMessage('El título de la tarea es obligatorio.');
        return false;
    }
    
    if (formData.title.length < 3) {
        showErrorMessage('El título debe tener al menos 3 caracteres.');
        return false;
    }
    
    if (!formData.subject) {
        showErrorMessage('Selecciona una asignatura de tu carrera.');
        return false;
    }
    
    if (!formData.date) {
        showErrorMessage('La fecha límite es obligatoria.');
        return false;
    }
    
    if (!formData.priority) {
        showErrorMessage('Selecciona una prioridad para la tarea.');
        return false;
    }
    
    // Validar que la fecha no sea en el pasado
    const taskDate = new Date(formData.date);
    const now = new Date();
    
    if (taskDate < now) {
        if (!confirm('La fecha seleccionada es en el pasado. ¿Continuar creando la tarea?')) {
            return false;
        }
    }
    
    // Validar que no sea demasiado en el futuro (más de 1 año)
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
    
    if (taskDate > oneYearFromNow) {
        showErrorMessage('La fecha no puede ser más de un año en el futuro.');
        return false;
    }
    
    return true;
}

/**
 * Agrega una tarea a la interfaz de usuario
 * @param {Object} task - Tarea a agregar
 */
function addTaskToUI(task) {
    const taskList = document.querySelector('.task-list');
    if (!taskList) return;
    
    const taskElement = createTaskElement(task);
    taskList.insertBefore(taskElement, taskList.firstChild);
    
    // Animación de entrada
    setTimeout(() => {
        taskElement.style.opacity = '1';
        taskElement.style.transform = 'translateY(0)';
    }, 100);
}

/**
 * Crea el elemento HTML para una tarea
 * @param {Object} task - Datos de la tarea
 * @returns {HTMLElement} Elemento de la tarea
 */
function createTaskElement(task) {
    const taskItem = document.createElement('div');
    taskItem.className = 'task-item';
    taskItem.dataset.taskId = task.id;
    taskItem.style.opacity = '0';
    taskItem.style.transform = 'translateY(20px)';
    taskItem.style.transition = 'all 0.3s ease';
    
    const formattedDate = formatTaskDate(task.date);
    const subjectName = APP_CONFIG.defaultSubjects[task.subject] || task.subject;
    
    taskItem.innerHTML = `
        <div class="task-header">
            <div class="task-title">${escapeHtml(task.title)}</div>
            <div class="task-priority priority-${task.priority}">${task.priority.toUpperCase()}</div>
        </div>
        <div class="task-subject">${escapeHtml(subjectName)}</div>
        <div class="task-date">Vence: ${formattedDate}</div>
    `;
    
    // Agregar evento click para futuras funcionalidades
    taskItem.addEventListener('click', () => handleTaskClick(task.id));
    
    return taskItem;
}

/**
 * Maneja el click en una tarea
 * @param {string} taskId - ID de la tarea
 */
function handleTaskClick(taskId) {
    const task = appState.tasks.find(t => t.id === taskId);
    if (task) {
        // Aquí se podría implementar edición de tareas
        if (APP_CONFIG.debugMode) {
            console.log('Tarea seleccionada:', task);
        }
        showSuccessMessage('Funcionalidad de edición próximamente disponible.');
    }
}

// === FUNCIONES DE UTILIDAD ===

/**
 * Valida si un email es válido
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Obtiene el nombre desde un email
 * @param {string} email - Email del usuario
 * @returns {string} Nombre extraído
 */
function getNameFromEmail(email) {
    const name = email.split('@')[0];
    // Capitalizar primera letra y reemplazar puntos/guiones
    const cleanName = name.replace(/[._-]/g, ' ');
    return cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
}

/**
 * Obtiene las iniciales desde un email
 * @param {string} email - Email del usuario
 * @returns {string} Iniciales
 */
function getInitialsFromEmail(email) {
    const name = email.split('@')[0];
    const cleanName = name.replace(/[._-]/g, ' ');
    const nameParts = cleanName.split(' ');
    
    if (nameParts.length >= 2) {
        return (nameParts[0][0] + nameParts[1][0]).toUpperCase();
    } else if (cleanName.length >= 2) {
        return (cleanName[0] + cleanName[1]).toUpperCase();
    }
    return cleanName[0].toUpperCase();
}

/**
 * Genera un ID único para tareas
 * @returns {string} ID único
 */
function generateTaskId() {
    return 'task_inacap_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Formatea la fecha de una tarea
 * @param {Date} date - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatTaskDate(date) {
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    const timeString = date.toLocaleTimeString('es-CL', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (diffDays === 0) {
        return `Hoy, ${timeString}`;
    } else if (diffDays === 1) {
        return `Mañana, ${timeString}`;
    } else if (diffDays === -1) {
        return `Ayer, ${timeString}`;
    } else if (diffDays > 0 && diffDays <= 7) {
        const dayName = date.toLocaleDateString('es-CL', { weekday: 'long' });
        return `${dayName.charAt(0).toUpperCase() + dayName.slice(1)}, ${timeString}`;
    } else {
        return date.toLocaleDateString('es-CL', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

/**
 * Escapa HTML para prevenir XSS
 * @param {string} text - Texto a escapar
 * @returns {string} Texto escapado
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Establece la fecha por defecto en el formulario
 */
function setDefaultDate() {
    const dateInput = document.getElementById('task-date');
    if (dateInput) {
        const now = new Date();
        // Agregar 2 horas a la fecha actual para dar tiempo razonable
        now.setHours(now.getHours() + 2);
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }
}

/**
 * Resetea el formulario de tareas
 */
function resetTaskForm() {
    const form = document.getElementById('task-form');
    if (form) {
        form.reset();
        // Restaurar valores por defecto
        const prioritySelect = document.getElementById('task-priority');
        if (prioritySelect) {
            prioritySelect.value = 'media';
        }
    }
}

/**
 * Actualiza la interfaz con datos del usuario
 */
function updateUserInterface() {
    if (appState.currentUser) {
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            userAvatar.textContent = appState.currentUser.initials;
            userAvatar.title = `${appState.currentUser.name} - Click para cerrar sesión`;
        }
    }
}

/**
 * Actualiza las estadísticas del dashboard
 */
function updateStats() {
    const pendingTasks = appState.tasks.filter(task => task.status === 'pending').length;
    const today = new Date();
    const todayTasks = appState.tasks.filter(task => {
        const taskDate = new Date(task.date);
        return taskDate.toDateString() === today.toDateString() && task.status === 'pending';
    }).length;
    
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length >= 2) {
        statNumbers[0].textContent = pendingTasks;
        statNumbers[1].textContent = todayTasks;
    }
    
    // Actualizar labels si es necesario
    const statLabels = document.querySelectorAll('.stat-label');
    if (statLabels.length >= 2) {
        statLabels[0].textContent = pendingTasks === 1 ? 'Tarea Pendiente' : 'Tareas Pendientes';
        statLabels[1].textContent = todayTasks === 1 ? 'Vence Hoy' : 'Vencen Hoy';
    }
}

/**
 * Carga datos del dashboard
 */
function loadDashboardData() {
    // Simular carga de datos
    if (APP_CONFIG.debugMode) {
        console.log('Cargando datos del dashboard INACAP...');
    }
    updateStats();
    
    // Verificar tareas próximas a vencer
    checkUpcomingTasks();
}

/**
 * Verifica tareas próximas a vencer
 */
function checkUpcomingTasks() {
    const now = new Date();
    const twentyFourHoursLater = new Date(now.getTime() + (24 * 60 * 60 * 1000));
    
    const upcomingTasks = appState.tasks.filter(task => {
        const taskDate = new Date(task.date);
        return taskDate <= twentyFourHoursLater && taskDate > now && task.status === 'pending';
    });
    
    if (upcomingTasks.length > 0) {
        const taskCount = upcomingTasks.length;
        const message = taskCount === 1 
            ? `Tienes 1 tarea que vence en las próximas 24 horas.`
            : `Tienes ${taskCount} tareas que vencen en las próximas 24 horas.`;
        
        setTimeout(() => {
            showInfoMessage(message);
        }, 2000);
    }
}

/**
 * Carga datos del calendario
 */
function loadCalendarData() {
    // Simular carga de datos del calendario
    if (APP_CONFIG.debugMode) {
        console.log('Cargando datos del calendario INACAP...');
    }
}

// === FUNCIONES DE MENSAJES ===

/**
 * Muestra un mensaje de éxito
 * @param {string} message - Mensaje a mostrar
 */
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

/**
 * Muestra un mensaje de error
 * @param {string} message - Mensaje a mostrar
 */
function showErrorMessage(message) {
    showMessage(message, 'error');
}

/**
 * Muestra un mensaje informativo
 * @param {string} message - Mensaje a mostrar
 */
function showInfoMessage(message) {
    showMessage(message, 'info');
}

/**
 * Muestra un mensaje de carga
 * @param {string} message - Mensaje a mostrar
 */
function showLoadingMessage(message) {
    showMessage(message, 'loading');
}

/**
 * Oculta el mensaje de carga
 */
function hideLoadingMessage() {
    const existingMessage = document.querySelector('.message-overlay');
    if (existingMessage) {
        existingMessage.remove();
    }
}

/**
 * Muestra un mensaje con tipo específico
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de mensaje (success, error, loading, info)
 */
function showMessage(message, type = 'info') {
    // Remover mensaje anterior
    hideLoadingMessage();
    
    const overlay = document.createElement('div');
    overlay.className = 'message-overlay';
    
    const messageBox = document.createElement('div');
    messageBox.className = `message-box message-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        loading: '⏳',
        info: 'ℹ️'
    };
    
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        loading: '#0066CC',
        info: '#FF6600'
    };
    
    messageBox.innerHTML = `
        <div class="message-icon" style="color: ${colors[type]};">
            ${icons[type]}
        </div>
        <div class="message-text">${escapeHtml(message)}</div>
    `;
    
    overlay.appendChild(messageBox);
    document.body.appendChild(overlay);
    
    // Auto-remove para mensajes que no son loading
    if (type !== 'loading') {
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }, 3000);
    }
    
    // Cerrar con click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
}

// === FUNCIONES DE VALIDACIÓN ESPECÍFICAS INACAP ===

/**
 * Valida que el email sea de dominio INACAP
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido
 */
function isInacapEmail(email) {
    const inacapDomains = ['@inacap.cl', '@alumnos.inacap.cl', '@profesor.inacap.cl'];
    return inacapDomains.some(domain => email.toLowerCase().includes(domain));
}

/**
 * Obtiene sugerencias de estudio basadas en las tareas
 * @returns {Array} Lista de sugerencias
 */
function getStudySuggestions() {
    const pendingTasks = appState.tasks.filter(task => task.status === 'pending');
    const suggestions = [];
    
    if (pendingTasks.length === 0) {
        suggestions.push('¡Excelente! No tienes tareas pendientes. Considera revisar material de estudio.');
    } else if (pendingTasks.length > 5) {
        suggestions.push('Tienes muchas tareas. Considera organizarlas por prioridad.');
        suggestions.push('Planifica bloques de estudio de 45-60 minutos con descansos.');
    }
    
    // Verificar tareas de alta prioridad
    const highPriorityTasks = pendingTasks.filter(task => task.priority === 'alta');
    if (highPriorityTasks.length > 0) {
        suggestions.push('Enfócate primero en las tareas de alta prioridad.');
    }
    
    return suggestions;
}

// === INICIALIZACIÓN ===

/**
 * Inicializa la aplicación cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Configurar formulario de login
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
        }
        
        // Configurar avatar de usuario para logout
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            userAvatar.addEventListener('click', logout);
        }
        
        // Configurar navegación con teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const currentView = document.querySelector('.view.active');
                if (currentView && 
                    currentView.id !== 'dashboard-view' && 
                    currentView.id !== 'login-view') {
                    showView('dashboard-view');
                }
            }
        });
        
        // Prevenir envío accidental de formularios
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && 
                    e.target.tagName !== 'TEXTAREA' && 
                    e.target.type !== 'submit') {
                    e.preventDefault();
                }
            });
        });
        
        // Configurar fecha por defecto
        setDefaultDate();
        
        // Mensaje de bienvenida inicial
        setTimeout(() => {
            if (appState.currentView === 'login-view') {
                showInfoMessage('Bienvenido a TaskU INACAP - Tu organizador académico personalizado');
            }
        }, 1000);
        
        // Configurar validación en tiempo real para emails
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                const email = this.value.trim();
                if (email && isValidEmail(email) && !isInacapEmail(email)) {
                    showErrorMessage('Recuerda usar tu correo institucional de INACAP (@inacap.cl)');
                }
            });
        }
        
        if (APP_CONFIG.debugMode) {
            console.log('TaskU INACAP inicializada correctamente');
            console.log('Institución:', APP_CONFIG.institution);
            window.appState = appState; // Para debugging
        }
        
    } catch (error) {
        console.error('Error al inicializar TaskU INACAP:', error);
        showErrorMessage('Error al cargar la aplicación. Recarga la página.');
    }
});

// === EXPORTAR FUNCIONES GLOBALES ===
// Hacer funciones disponibles globalmente para uso en HTML
window.showView = showView;
window.createTask = createTask;
window.logout = logout;

// === FUNCIONES ADICIONALES ESPECÍFICAS PARA INACAP ===

/**
 * Obtiene el semestre actual basado en la fecha
 * @returns {string} Semestre actual
 */
function getCurrentSemester() {
    const now = new Date();
    const month = now.getMonth() + 1; // getMonth() retorna 0-11
    const year = now.getFullYear();
    
    if (month >= 3 && month <= 7) {
        return `Primer Semestre ${year}`;
    } else if (month >= 8 && month <= 12) {
        return `Segundo Semestre ${year}`;
    } else {
        return `Verano ${year}`;
    }
}

/**
 * Calcula estadísticas académicas del estudiante
 * @returns {Object} Estadísticas
 */
function calculateAcademicStats() {
    const totalTasks = appState.tasks.length;
    const completedTasks = appState.tasks.filter(t => t.status === 'completed').length;
    const pendingTasks = appState.tasks.filter(t => t.status === 'pending').length;
    const overdueTasks = appState.tasks.filter(t => {
        const taskDate = new Date(t.date);
        return taskDate < new Date() && t.status === 'pending';
    }).length;
    
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    return {
        total: totalTasks,
        completed: completedTasks,
        pending: pendingTasks,
        overdue: overdueTasks,
        completionRate: completionRate,
        semester: getCurrentSemester()
    };
}

/**
 * Genera reporte académico
 * @returns {string} Reporte formateado
 */
function generateAcademicReport() {
    const stats = calculateAcademicStats();
    
    return `
=== REPORTE ACADÉMICO INACAP ===
Semestre: ${stats.semester}
Tareas Totales: ${stats.total}
Completadas: ${stats.completed}
Pendientes: ${stats.pending}
Atrasadas: ${stats.overdue}
Tasa de Cumplimiento: ${stats.completionRate}%
=============================
    `.trim();
}

// Agregar función para mostrar estadísticas en consola (solo en modo debug)
if (APP_CONFIG.debugMode) {
    window.showStats = function() {
        console.log(generateAcademicReport());
    };
}