// ==========================================================================
// Portfolio JavaScript - API Connectivity, ScrollSpy, Animations & Sidebar
// ==========================================================================


// API Configuration with Environment & Fallback Support
const API_BASE_URL = (typeof window !== 'undefined' && window.ENV && window.ENV.API_BASE_URL)
    || (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_API_URL)
    || 'https://dynamic-portfolio-website.fastapicloud.dev'; // <--- PASTE YOUR DEPLOYED BACKEND URL HERE (e.g. Render / FastAPI Cloud URL)

// DOM Elements
const sidebar = document.getElementById('sidebar');
const mobileNavToggle = document.getElementById('mobileNavToggle');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const sidebarLinks = document.querySelectorAll('.sidebar-link');
const sections = document.querySelectorAll('section.section');
const contactForm = document.getElementById('contact-form');
const skillsContainer = document.getElementById('skills-container');
const projectsContainer = document.getElementById('projects-container');
const servicesContainer = document.getElementById('services-container');
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const themeText = document.getElementById('themeText');

/* --------------------------------------------------------------------------
   1. Theme Toggle Functionality
   -------------------------------------------------------------------------- */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Update icon and text
    if (newTheme === 'light') {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        themeText.textContent = 'Light Mode';
    } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        themeText.textContent = 'Dark Mode';
    }
}

// Initialize theme from localStorage or default to dark
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const html = document.documentElement;

    html.setAttribute('data-theme', savedTheme);

    if (savedTheme === 'light') {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        themeText.textContent = 'Light Mode';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
}

/* --------------------------------------------------------------------------
   2. Mobile Navigation & Sidebar Drawer Controls
   -------------------------------------------------------------------------- */
if (mobileNavToggle) {
    mobileNavToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    });
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    });
}

// Close mobile menu when clicking any sidebar link
sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
        sidebar.classList.remove('active');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
    });
});

/* --------------------------------------------------------------------------
   2. ScrollSpy - Active Section Highlight on Sidebar
   -------------------------------------------------------------------------- */
function updateActiveSection() {
    let currentSectionId = '';
    const scrollPosition = window.scrollY + 200;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSectionId = section.getAttribute('id');
        }
    });

    if (currentSectionId) {
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === currentSectionId || link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });
    }
}

window.addEventListener('scroll', updateActiveSection);

/* --------------------------------------------------------------------------
   3. On-Scroll Reveal Animation & Skill Bar Filling
   -------------------------------------------------------------------------- */
function revealOnScroll() {
    const reveals = document.querySelectorAll('.reveal');
    const windowHeight = window.innerHeight;

    reveals.forEach(reveal => {
        const revealTop = reveal.getBoundingClientRect().top;
        const revealPoint = 130;

        if (revealTop < windowHeight - revealPoint) {
            reveal.classList.add('active');
            
            // Trigger skill bar animation if this is skills section
            const skillBars = reveal.querySelectorAll('.skill-progress');
            skillBars.forEach(bar => {
                const targetWidth = bar.getAttribute('data-level');
                if (targetWidth) {
                    bar.style.width = targetWidth;
                }
            });
        }
    });

    // Handle about text card animation
    const aboutTextCard = document.querySelector('.about-text-card');
    if (aboutTextCard) {
        const cardTop = aboutTextCard.getBoundingClientRect().top;
        if (cardTop < windowHeight - 100) {
            aboutTextCard.classList.add('active');
        }
    }
}

window.addEventListener('scroll', revealOnScroll);

/* --------------------------------------------------------------------------
   4. Hero Section Animated Stats Counters
   -------------------------------------------------------------------------- */
let statsAnimated = false;

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    if (!statNumbers.length || statsAnimated) return;

    const firstStat = statNumbers[0];
    const top = firstStat.getBoundingClientRect().top;
    if (top < window.innerHeight) {
        statsAnimated = true;
        statNumbers.forEach(stat => {
            const targetStr = stat.getAttribute('data-target');
            const suffix = stat.getAttribute('data-suffix') || '';
            const targetVal = parseFloat(targetStr);
            const duration = 1500;
            const startTime = performance.now();

            function updateCounter(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const currentVal = (targetVal * progress).toFixed(targetVal % 1 !== 0 ? 1 : 0);
                stat.textContent = currentVal + suffix;

                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    stat.textContent = targetStr + suffix;
                }
            }

            requestAnimationFrame(updateCounter);
        });
    }
}

window.addEventListener('scroll', animateStats);

/* --------------------------------------------------------------------------
   5. Helper API Call Function
   -------------------------------------------------------------------------- */
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

/* --------------------------------------------------------------------------
   6. Load & Render Skills
   -------------------------------------------------------------------------- */
async function loadSkills() {
    const skills = await fetchAPI('/skills/');
    if (skills && skills.length > 0) {
        renderSkills(skills);
    } else {
        renderDefaultSkills();
    }
}

function renderSkills(skills) {
    // Group skills by category
    const categories = {};
    skills.forEach(skill => {
        if (!categories[skill.category]) {
            categories[skill.category] = [];
        }
        categories[skill.category].push(skill);
    });

    let html = '';
    for (const [catName, catSkills] of Object.entries(categories)) {
        html += `
            <div class="glass-card skill-card reveal">
                <h3 class="skill-category-title">
                    <i class="fa-solid fa-code icon-accent"></i> ${catName}
                </h3>
                ${catSkills.map(skill => `
                    <div class="skill-item">
                        <div class="skill-info">
                            <span class="skill-name">${skill.name}</span>
                            <span class="skill-val">${skill.level}%</span>
                        </div>
                        <div class="skill-bar">
                            <div class="skill-progress" data-level="${skill.level}%" style="width: 0%;"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    skillsContainer.innerHTML = html;
    setTimeout(revealOnScroll, 100);
}

function renderDefaultSkills() {
    const defaultSkills = [
        {
            category: 'ServiceNow Platform',
            skills: [
                { name: 'ITSM Module', level: 90 },
                { name: 'Flow Designer & Workflows', level: 85 },
                { name: 'Client Scripts & UI Policies', level: 88 },
                { name: 'Business Rules & Data Architecture', level: 87 },
                { name: 'Service Catalog & Email Actions', level: 82 }
            ]
        },
        {
            category: 'Frontend & Languages',
            skills: [
                { name: 'HTML5 & Modern CSS3', level: 90 },
                { name: 'Vanilla JavaScript (ES6+)', level: 85 },
                { name: 'Python & FastAPI', level: 80 },
                { name: 'C++ Fundamentals', level: 75 }
            ]
        },
        {
            category: 'Core Competencies',
            skills: [
                { name: 'Problem Solving & Debugging', level: 95 },
                { name: 'Critical Thinking & Design', level: 92 },
                { name: 'Stakeholder Communication', level: 90 }
            ]
        }
    ];

    let html = '';
    defaultSkills.forEach(cat => {
        html += `
            <div class="glass-card skill-card reveal">
                <h3 class="skill-category-title">
                    <i class="fa-solid fa-code icon-accent"></i> ${cat.category}
                </h3>
                ${cat.skills.map(skill => `
                    <div class="skill-item">
                        <div class="skill-info">
                            <span class="skill-name">${skill.name}</span>
                            <span class="skill-val">${skill.level}%</span>
                        </div>
                        <div class="skill-bar">
                            <div class="skill-progress" data-level="${skill.level}%" style="width: 0%;"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    });
    skillsContainer.innerHTML = html;
    setTimeout(revealOnScroll, 100);
}

/* --------------------------------------------------------------------------
   7. Load & Render Projects
   -------------------------------------------------------------------------- */
async function loadProjects() {
    const projects = await fetchAPI('/projects/');
    if (projects && projects.length > 0) {
        renderProjects(projects);
    } else {
        renderDefaultProjects();
    }
}

function renderProjects(projects) {
    projectsContainer.innerHTML = projects.map(project => `
        <div class="glass-card project-card reveal">
            <div class="project-banner">
                ${project.image_url ? `<img src="${project.image_url}" alt="${project.title}">` : '<i class="fa-solid fa-rocket"></i>'}
            </div>
            <div class="project-body">
                <h3 class="project-title">${project.title}</h3>
                <p class="project-description">${project.description}</p>
                <div class="project-features-list">
                    <h4>Key Features:</h4>
                    <ul>
                        ${project.features ? project.features.split('\n').map(feature => `<li>${feature}</li>`).join('') : ''}
                    </ul>
                </div>
                <div class="project-tags">
                    ${project.tech_stack.split(',').map(tech => `<span class="tech-tag">${tech.trim()}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
    setTimeout(revealOnScroll, 100);
}

function renderDefaultProjects() {
    const defaultProjects = [
        {
            title: 'Crypto Exchange Mini App',
            description: 'A front-end mini application simulating a cryptocurrency exchange interface, built to strengthen component-based design and state management skills.',
            features: ['Real-time price updates', 'Interactive trading interface', 'Portfolio tracking', 'Responsive UI design'],
            tech_stack: 'React, JavaScript, CSS',
            icon: '<i class="fa-solid fa-coins"></i>'
        },
        {
            title: 'Snake Game',
            description: 'A classic browser-based Snake game built from scratch, focusing on DOM manipulation, event handling, and custom game-loop logic.',
            features: ['Classic gameplay mechanics', 'Score tracking', 'Responsive controls', 'Smooth animations'],
            tech_stack: 'HTML, CSS, JavaScript',
            icon: '<i class="fa-solid fa-gamepad"></i>'
        },
        {
            title: 'Tic Tac Toe Game',
            description: 'An interactive two-player Tic Tac Toe game demonstrating logic building, win-condition checks, and clean UI design.',
            features: ['Two-player mode', 'Win detection algorithm', 'Reset functionality', 'Clean responsive layout'],
            tech_stack: 'HTML, CSS, JavaScript',
            icon: '<i class="fa-solid fa-xmark"></i>'
        },
        {
            title: 'Color Generator Tool',
            description: 'A utility tool that generates and displays random color codes, built to practice DOM manipulation and dynamic style binding.',
            features: ['Random hex color generation', 'Hex code display', 'Copy to clipboard', 'Instant color preview'],
            tech_stack: 'HTML, CSS, JavaScript',
            icon: '<i class="fa-solid fa-palette"></i>'
        }
    ];

    projectsContainer.innerHTML = defaultProjects.map(project => `
        <div class="glass-card project-card reveal">
            <div class="project-banner">
                ${project.icon}
            </div>
            <div class="project-body">
                <h3 class="project-title">${project.title}</h3>
                <p class="project-description">${project.description}</p>
                <div class="project-features-list">
                    <h4>Key Features:</h4>
                    <ul>
                        ${project.features.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                </div>
                <div class="project-tags">
                    ${project.tech_stack.split(',').map(tech => `<span class="tech-tag">${tech.trim()}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
    setTimeout(revealOnScroll, 100);
}

/* --------------------------------------------------------------------------
   8. Load & Render Services
   -------------------------------------------------------------------------- */
async function loadServices() {
    const services = await fetchAPI('/services/');
    if (services && services.length > 0) {
        renderServices(services);
    } else {
        renderDefaultServices();
    }
}

function getServiceIconMarkup(icon) {
    if (!icon || icon.trim() === '') return '';
    if (icon.startsWith('<')) return icon;
    if (icon.startsWith('/') || icon.startsWith('http') || icon.includes('.')) {
        return `<img src="${icon}" alt="Service Icon" class="service-icon-img" style="width:100%; height:100%; object-fit:contain;">`;
    }
    return icon;
}

function renderServices(services) {
    servicesContainer.innerHTML = services.map(service => {
        const iconMarkup = getServiceIconMarkup(service.icon);
        return `
        <div class="glass-card service-card reveal">
            ${iconMarkup ? `<div class="service-icon-box">${iconMarkup}</div>` : ''}
            <h3 class="service-title">${service.title}</h3>
            <p class="service-description">${service.description}</p>
        </div>
    `}).join('');
    setTimeout(revealOnScroll, 100);
}

function renderDefaultServices() {
    const defaultServices = [
        {
            icon: '',
            title: 'ServiceNow Development',
            description: 'Expert ServiceNow platform development including custom applications, modules, and integrations tailored to your business needs.'
        },
        {
            icon: '<i class="fa-solid fa-diagram-next"></i>',
            title: 'Workflow Automation',
            description: 'Automate complex business processes using Flow Designer and workflows to reduce manual intervention and improve efficiency.'
        },
        {
            icon: '<i class="fa-solid fa-list-check"></i>',
            title: 'ITSM Implementation',
            description: 'Complete IT Service Management implementation including Incident, Problem, Change, and Request Management workflows.'
        },
        {
            icon: '<i class="fa-solid fa-bolt"></i>',
            title: 'Process Automation',
            description: 'Streamline your business processes with intelligent automation solutions that save time and reduce errors.'
        }
    ];

    servicesContainer.innerHTML = defaultServices.map(service => {
        const iconMarkup = getServiceIconMarkup(service.icon);
        return `
        <div class="glass-card service-card reveal">
            ${iconMarkup ? `<div class="service-icon-box">${iconMarkup}</div>` : ''}
            <h3 class="service-title">${service.title}</h3>
            <p class="service-description">${service.description}</p>
        </div>
    `}).join('');
    setTimeout(revealOnScroll, 100);
}

/* --------------------------------------------------------------------------
   9. Contact Form Submission Handling
   -------------------------------------------------------------------------- */
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            subject: document.getElementById('subject').value.trim(),
            message: document.getElementById('message').value.trim()
        };

        const submitBtn = contactForm.querySelector('.btn-submit');
        const originalHtml = submitBtn.innerHTML;
        submitBtn.innerHTML = `<span>Sending...</span> <i class="fa-solid fa-spinner fa-spin"></i>`;
        submitBtn.disabled = true;

        try {
            const result = await fetchAPI('/messages/', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            if (result) {
                alert('Thank you! Your message has been sent successfully.');
                contactForm.reset();
            } else {
                alert('Failed to send message. Please try again or email directly.');
            }
        } catch (error) {
            alert('An error occurred while sending your message.');
        } finally {
            submitBtn.innerHTML = originalHtml;
            submitBtn.disabled = false;
        }
    });
}

/* --------------------------------------------------------------------------
   10. Typing Effect for Hero Tagline
   -------------------------------------------------------------------------- */
function typeWriterEffect() {
    const typingElement = document.querySelector('.typing-text');
    if (!typingElement) return;

    const taglines = [
        "Building intelligent ServiceNow solutions",
        "Automating enterprise workflows",
        "Transforming ITSM operations"
    ];
    
    let taglineIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 50;

    function type() {
        const currentTagline = taglines[taglineIndex];
        
        if (isDeleting) {
            typingElement.textContent = currentTagline.substring(0, charIndex - 1);
            charIndex--;
            typingSpeed = 30;
        } else {
            typingElement.textContent = currentTagline.substring(0, charIndex + 1);
            charIndex++;
            typingSpeed = 50;
        }

        if (!isDeleting && charIndex === currentTagline.length) {
            isDeleting = true;
            typingSpeed = 2000; // Pause at end
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            taglineIndex = (taglineIndex + 1) % taglines.length;
            typingSpeed = 500; // Pause before next tagline
        }

        setTimeout(type, typingSpeed);
    }

    type();
}

/* --------------------------------------------------------------------------
   11. Initialization
   -------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initializeTheme();

    loadSkills();
    loadProjects();
    loadServices();

    // Start typing effect
    setTimeout(typeWriterEffect, 1000);

    // Initial scroll triggers
    setTimeout(() => {
        updateActiveSection();
        revealOnScroll();
        animateStats();
    }, 150);
});
