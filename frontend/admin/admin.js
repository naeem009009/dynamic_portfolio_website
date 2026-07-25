// API Configuration
const API_BASE_URL = 'https://muneer.fastapicloud.dev';

// State
let authToken = localStorage.getItem('authToken');
let currentSection = 'dashboard';

// DOM Elements
const loginPage = document.getElementById('login-page');
const adminDashboard = document.getElementById('admin-dashboard');
const loginForm = document.getElementById('login-form');
const logoutBtn = document.getElementById('logout-btn');
const navLinks = document.querySelectorAll('.nav-link');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        showDashboard();
    } else {
        showLogin();
    }

    setupNavigation();
    setupForms();
});

// Authentication
function showLogin() {
    loginPage.style.display = 'flex';
    adminDashboard.style.display = 'none';
}

function showDashboard() {
    loginPage.style.display = 'none';
    adminDashboard.style.display = 'flex';
    loadDashboardData();
}

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        // Form Data required for FastAPI OAuth2 Password Flow
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showDashboard();
        } else {
            alert('Invalid credentials');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
    }
});

logoutBtn.addEventListener('click', () => {
    authToken = null;
    localStorage.removeItem('authToken');
    showLogin();
});

// Navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            switchSection(section);

            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function switchSection(section) {
    currentSection = section;

    document.querySelectorAll('.dashboard-section').forEach(s => {
        s.classList.remove('active');
    });

    document.getElementById(`section-${section}`).classList.add('active');

    const titles = {
        dashboard: 'Dashboard',
        projects: 'Projects',
        skills: 'Skills',
        services: 'Services',
        messages: 'Messages'
    };

    document.getElementById('page-title').textContent = titles[section];

    if (section === 'dashboard') {
        loadDashboardData();
    } else if (section === 'projects') {
        loadProjects();
    } else if (section === 'skills') {
        loadSkills();
    } else if (section === 'services') {
        loadServices();
    } else if (section === 'messages') {
        loadMessages();
    }
}

// API Functions
async function fetchAPI(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers,
            ...options
        });

        if (!response.ok) {
            if (response.status === 401) {
                authToken = null;
                localStorage.removeItem('authToken');
                showLogin();
                return null;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// Dashboard Data
async function loadDashboardData() {
    const projects = await fetchAPI('/projects/');
    const skills = await fetchAPI('/skills/');
    const services = await fetchAPI('/services/');
    const messages = await fetchAPI('/messages/');

    document.getElementById('stat-projects').textContent = projects ? projects.length : 0;
    document.getElementById('stat-skills').textContent = skills ? skills.length : 0;
    document.getElementById('stat-services').textContent = services ? services.length : 0;
    document.getElementById('stat-messages').textContent = messages ? messages.filter(m => !m.is_read).length : 0;
}

// Projects
async function loadProjects() {
    const projects = await fetchAPI('/projects/');
    const tbody = document.getElementById('projects-table-body');

    if (projects) {
        tbody.innerHTML = projects.map(project => `
            <tr>
                <td>${project.title}</td>
                <td>${project.tech_stack}</td>
                <td>${new Date(project.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-edit" onclick="editProject(${project.id})">Edit</button>
                        <button class="btn-action btn-delete" onclick="deleteProject(${project.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function openProjectModal(project = null) {
    const modal = document.getElementById('project-modal');
    const title = document.getElementById('project-modal-title');

    if (project) {
        title.textContent = 'Edit Project';
        document.getElementById('project-id').value = project.id;
        document.getElementById('project-title').value = project.title;
        document.getElementById('project-description').value = project.description;
        document.getElementById('project-features').value = project.features;
        document.getElementById('project-tech-stack').value = project.tech_stack;
        document.getElementById('project-image-url').value = project.image_url || '';
    } else {
        title.textContent = 'Add Project';
        document.getElementById('project-form').reset();
        document.getElementById('project-id').value = '';
    }

    modal.classList.add('active');
}

function closeProjectModal() {
    document.getElementById('project-modal').classList.remove('active');
}

async function editProject(id) {
    const project = await fetchAPI(`/projects/${id}`);
    if (project) {
        openProjectModal(project);
    }
}

async function deleteProject(id) {
    if (confirm('Are you sure you want to delete this project?')) {
        const result = await fetchAPI(`/projects/${id}`, {
            method: 'DELETE'
        });

        if (result) {
            loadProjects();
        }
    }
}

// Skills
async function loadSkills() {
    const skills = await fetchAPI('/skills/');
    const tbody = document.getElementById('skills-table-body');

    if (skills) {
        tbody.innerHTML = skills.map(skill => `
            <tr>
                <td>${skill.category}</td>
                <td>${skill.name}</td>
                <td>${skill.level}%</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-edit" onclick="editSkill(${skill.id})">Edit</button>
                        <button class="btn-action btn-delete" onclick="deleteSkill(${skill.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function openSkillModal(skill = null) {
    const modal = document.getElementById('skill-modal');
    const title = document.getElementById('skill-modal-title');

    if (skill) {
        title.textContent = 'Edit Skill';
        document.getElementById('skill-id').value = skill.id;
        document.getElementById('skill-category').value = skill.category;
        document.getElementById('skill-name').value = skill.name;
        document.getElementById('skill-level').value = skill.level;
    } else {
        title.textContent = 'Add Skill';
        document.getElementById('skill-form').reset();
        document.getElementById('skill-id').value = '';
    }

    modal.classList.add('active');
}

function closeSkillModal() {
    document.getElementById('skill-modal').classList.remove('active');
}

async function editSkill(id) {
    const skill = await fetchAPI(`/skills/${id}`);
    if (skill) {
        openSkillModal(skill);
    }
}

async function deleteSkill(id) {
    if (confirm('Are you sure you want to delete this skill?')) {
        const result = await fetchAPI(`/skills/${id}`, {
            method: 'DELETE'
        });

        if (result) {
            loadSkills();
        }
    }
}

// Services
async function loadServices() {
    const services = await fetchAPI('/services/');
    const tbody = document.getElementById('services-table-body');

    if (services) {
        tbody.innerHTML = services.map(service => `
            <tr>
                <td>${service.title}</td>
                <td>${service.description.substring(0, 50)}...</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-edit" onclick="editService(${service.id})">Edit</button>
                        <button class="btn-action btn-delete" onclick="deleteService(${service.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

function openServiceModal(service = null) {
    const modal = document.getElementById('service-modal');
    const title = document.getElementById('service-modal-title');

    if (service) {
        title.textContent = 'Edit Service';
        document.getElementById('service-id').value = service.id;
        document.getElementById('service-title').value = service.title;
        document.getElementById('service-description').value = service.description;
        document.getElementById('service-icon').value = service.icon || '';
    } else {
        title.textContent = 'Add Service';
        document.getElementById('service-form').reset();
        document.getElementById('service-id').value = '';
    }

    modal.classList.add('active');
}

function closeServiceModal() {
    document.getElementById('service-modal').classList.remove('active');
}

async function editService(id) {
    const service = await fetchAPI(`/services/${id}`);
    if (service) {
        openServiceModal(service);
    }
}

async function deleteService(id) {
    if (confirm('Are you sure you want to delete this service?')) {
        const result = await fetchAPI(`/services/${id}`, {
            method: 'DELETE'
        });

        if (result) {
            loadServices();
        }
    }
}

// Messages
async function loadMessages() {
    const messages = await fetchAPI('/messages/');
    const tbody = document.getElementById('messages-table-body');

    if (messages) {
        tbody.innerHTML = messages.map(message => `
            <tr>
                <td>${message.name}</td>
                <td>${message.email}</td>
                <td>${message.subject}</td>
                <td>${new Date(message.created_at).toLocaleDateString()}</td>
                <td>
                    <span style="color: ${message.is_read ? '#10b981' : '#f59e0b'}">
                        ${message.is_read ? 'Read' : 'Unread'}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        ${!message.is_read ? `<button class="btn-action btn-edit" onclick="markAsRead(${message.id})">Mark Read</button>` : ''}
                        <button class="btn-action btn-delete" onclick="deleteMessage(${message.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

async function markAsRead(id) {
    const result = await fetchAPI(`/messages/${id}/read`, {
        method: 'PATCH'
    });

    if (result) {
        loadMessages();
    }
}

async function deleteMessage(id) {
    if (confirm('Are you sure you want to delete this message?')) {
        const result = await fetchAPI(`/messages/${id}`, {
            method: 'DELETE'
        });

        if (result) {
            loadMessages();
        }
    }
}

// Form Submissions
function setupForms() {
    // Project Form
    document.getElementById('project-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('project-id').value;
        const data = {
            title: document.getElementById('project-title').value,
            description: document.getElementById('project-description').value,
            features: document.getElementById('project-features').value,
            tech_stack: document.getElementById('project-tech-stack').value,
            image_url: document.getElementById('project-image-url').value
        };

        let result;
        if (id) {
            result = await fetchAPI(`/projects/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            result = await fetchAPI('/projects/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }

        if (result) {
            closeProjectModal();
            loadProjects();
        }
    });

    // Skill Form
    document.getElementById('skill-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('skill-id').value;
        const data = {
            category: document.getElementById('skill-category').value,
            name: document.getElementById('skill-name').value,
            level: parseInt(document.getElementById('skill-level').value, 10)
        };

        let result;
        if (id) {
            result = await fetchAPI(`/skills/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            result = await fetchAPI('/skills/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }

        if (result) {
            closeSkillModal();
            loadSkills();
        }
    });

    // Service Form
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('service-id').value;
        const data = {
            title: document.getElementById('service-title').value,
            description: document.getElementById('service-description').value,
            icon: document.getElementById('service-icon').value
        };

        let result;
        if (id) {
            result = await fetchAPI(`/services/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            result = await fetchAPI('/services/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }

        if (result) {
            closeServiceModal();
            loadServices();
        }
    });
}

// Close modals when clicking outside
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});
