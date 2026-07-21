# Portfolio Website with Admin Panel

A production-ready portfolio web application with a fully functional admin panel, built for ServiceNow Developer & Workflow Automation Specialist.

## 🚀 Features

### Public Portfolio
- **Hero Section**: Animated parallax background with CTAs
- **About Section**: Professional summary and experience highlights
- **Skills Section**: Categorized skill display with progress bars
- **Experience Section**: Timeline-based experience display
- **Projects Section**: Project showcase with features and tech stack
- **Services Section**: Freelancing services display
- **Contact Section**: Contact form connected to backend API

### Admin Panel
- **JWT Authentication**: Secure login system
- **Dashboard**: Overview statistics
- **Project Management**: Add, edit, delete projects
- **Skill Management**: Manage technical skills
- **Service Management**: Manage offered services
- **Message Management**: View and manage contact messages

## 🛠️ Tech Stack

### Backend
- Python 3.8+
- FastAPI (REST API)
- SQLAlchemy (ORM)
- SQLite (Database)
- JWT (Authentication)
- Pydantic (Data validation)

### Frontend
- HTML5
- CSS3 (Glassmorphism design)
- Vanilla JavaScript
- Responsive design

## 📁 Project Structure

```
portfolio/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── models/
│   │   └── __init__.py         # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── projects.py         # Project CRUD endpoints
│   │   ├── skills.py           # Skill CRUD endpoints
│   │   ├── services.py         # Service CRUD endpoints
│   │   └── messages.py         # Message endpoints
│   └── schemas/
│       └── __init__.py         # Pydantic schemas
├── frontend/
│   ├── index.html              # Main portfolio page
│   ├── css/
│   │   └── style.css           # Styles with glassmorphism
│   └── js/
│       └── main.js             # Frontend JavaScript
├── admin/
│   ├── dashboard.html          # Admin panel UI
│   └── admin.js                # Admin panel JavaScript
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Access the Portfolio

Open `frontend/index.html` in your browser or serve it through the backend:
```
http://localhost:8000/static/index.html
```

### 4. Access the Admin Panel

Open `admin/dashboard.html` in your browser

### 5. Create Admin Account

First, register an admin account using the API:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword&email=admin@example.com"
```

Then login with these credentials in the admin panel.

## 🗄️ Database Seeding

To populate the database with initial CV data, run the seed script:

```bash
python seed_database.py
```

This will create:
- Default admin user (username: admin, password: admin123)
- Sample projects from CV
- Skills from CV
- Services from CV

## 🔐 Security Notes

- Change the JWT SECRET_KEY in `backend/routers/auth.py` before production
- Use environment variables for sensitive configuration
- Implement rate limiting for production
- Use HTTPS in production
- Change default admin password after first login

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Projects
- `GET /projects/` - Get all projects
- `GET /projects/{id}` - Get single project
- `POST /projects/` - Create project (auth required)
- `PUT /projects/{id}` - Update project (auth required)
- `DELETE /projects/{id}` - Delete project (auth required)

### Skills
- `GET /skills/` - Get all skills
- `GET /skills/{id}` - Get single skill
- `POST /skills/` - Create skill (auth required)
- `PUT /skills/{id}` - Update skill (auth required)
- `DELETE /skills/{id}` - Delete skill (auth required)

### Services
- `GET /services/` - Get all services
- `GET /services/{id}` - Get single service
- `POST /services/` - Create service (auth required)
- `PUT /services/{id}` - Update service (auth required)
- `DELETE /services/{id}` - Delete service (auth required)

### Messages
- `POST /messages/` - Create message (public)
- `GET /messages/` - Get all messages (auth required)
- `GET /messages/{id}` - Get single message (auth required)
- `DELETE /messages/{id}` - Delete message (auth required)
- `PATCH /messages/{id}/read` - Mark as read (auth required)

## 🎨 Design Features

- **Glassmorphism**: Modern glass-like card effects
- **Gradient Backgrounds**: Blue (#2563EB) + Orange (#F59E0B)
- **Smooth Animations**: Scroll reveal, hover effects, parallax
- **Responsive Design**: Mobile-first approach
- **Premium Typography**: Poppins & Inter fonts

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🤝 Contributing

This is a personal portfolio project. For suggestions or improvements, please contact the developer.

## 📄 License

This project is for personal use. All rights reserved.

## 👤 Developer

**Muneer Majeed**
- ServiceNow Developer
- Workflow Automation Specialist
- Email: muneermajeed037@gmail.com
- Location: Lahore, Pakistan
