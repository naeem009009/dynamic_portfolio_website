import sys
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Add backend directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Project, Skill, Service

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    admin_username = os.getenv("ADMIN_USERNAME", "muneer")
    admin_password = os.getenv("ADMIN_PASSWORD", "muneer037")
    admin_email = os.getenv("ADMIN_EMAIL", "muneermajeed037@gmail.com")
    
    try:
        # Query any existing admin users by username or email
        admin_users = db.query(User).filter(
            (User.username == admin_username) | (User.username == "admin") | (User.email == admin_email)
        ).all()
        
        if admin_users:
            main_admin = admin_users[0]
            # Delete other duplicate user rows first to avoid unique constraint collisions
            for extra_user in admin_users[1:]:
                db.delete(extra_user)
            db.commit()
            
            # Update main admin fields
            main_admin.username = admin_username
            main_admin.email = admin_email
            main_admin.hashed_password = get_password_hash(admin_password)
            db.commit()
            print(f"[OK] Single admin user '{admin_username}' configured cleanly")
        else:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                hashed_password=get_password_hash(admin_password)
            )
            db.add(admin_user)
            db.commit()
            print(f"[OK] Admin user created (username: {admin_username})")
        
        # Seed Projects
        projects_data = [
            {
                "title": "Portfolio Website",
                "description": "A personal portfolio website showcasing ServiceNow development skills, projects, and professional experience with a modern responsive design.",
                "features": "Dynamic content loading\nAdmin panel for content management\nResponsive design\nContact form integration",
                "tech_stack": "FastAPI, HTML, CSS, JavaScript, SQLite",
                "image_url": "/frontend/images/portfolio-project.svg"
            },
            {
                "title": "Crypto Exchange Mini App",
                "description": "A front-end mini application simulating a cryptocurrency exchange interface, built to strengthen component-based design and state management skills in React.",
                "features": "Real-time price updates\nInteractive trading interface\nPortfolio tracking\nResponsive design",
                "tech_stack": "React, JavaScript, CSS",
                "image_url": "/frontend/images/crypto-exchange-mini-app.svg"
            },
            {
                "title": "Snake Game",
                "description": "A classic browser-based Snake game built from scratch, focusing on DOM manipulation, event handling, and game-loop logic.",
                "features": "Classic gameplay mechanics\nScore tracking\nResponsive controls\nSmooth animations",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/snake-game.svg"
            },
            {
                "title": "Crypto Snake Game - Neon Edition",
                "description": "A cryptocurrency-themed Snake game featuring Bitcoin, Ethereum, and other crypto icons as collectibles with a neon grid aesthetic.",
                "features": "Crypto icon collection\nNeon grid design\nScore tracking\nResponsive mobile layout",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/crypto-snake-game-1.svg"
            },
            {
                "title": "Crypto Snake Game - Gold Edition",
                "description": "A premium version of the crypto Snake game with golden aesthetics, featuring multiple cryptocurrencies including Dogecoin and Cardano.",
                "features": "Golden treasure theme\nMulti-coin support\nEnhanced graphics\nSmooth animations",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/crypto-snake-game-2.svg"
            },
            {
                "title": "Crypto Snake Game - Cyber Edition",
                "description": "A cyberpunk-themed crypto Snake game with Polkadot, Chainlink, and Ripple icons in a futuristic dark grid environment.",
                "features": "Cyberpunk aesthetics\nAdvanced crypto icons\nParticle effects\nImmersive gameplay",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/crypto-snake-game-3.svg"
            },
            {
                "title": "Tic Tac Toe Game",
                "description": "An interactive two-player Tic Tac Toe game demonstrating logic building, win-condition checks, and clean UI design.",
                "features": "Two-player mode\nWin detection\nReset functionality\nClean UI",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/tic-tac-toe-game.svg"
            },
            {
                "title": "Color Generator Tool",
                "description": "A utility tool that generates and displays random color codes, built to practice DOM manipulation and dynamic styling.",
                "features": "Random color generation\nHex code display\nCopy to clipboard\nColor preview",
                "tech_stack": "HTML, CSS, JavaScript",
                "image_url": "/frontend/images/color-generator-tool.svg"
            }
        ]
        
        for project_data in projects_data:
            existing_project = db.query(Project).filter(Project.title == project_data["title"]).first()
            if not existing_project:
                project = Project(**project_data)
                db.add(project)
                db.commit()
                print(f"[OK] Project '{project_data['title']}' created")
            else:
                print(f"[OK] Project '{project_data['title']}' already exists")
        
        # Seed Skills
        skills_data = [
            # ServiceNow Platform Skills
            {"category": "ServiceNow Platform", "name": "ITSM", "level": 90},
            {"category": "ServiceNow Platform", "name": "Service Catalog Development", "level": 85},
            {"category": "ServiceNow Platform", "name": "Flow Designer", "level": 85},
            {"category": "ServiceNow Platform", "name": "Client Scripts", "level": 88},
            {"category": "ServiceNow Platform", "name": "UI Policies", "level": 85},
            {"category": "ServiceNow Platform", "name": "Business Rules", "level": 87},
            {"category": "ServiceNow Platform", "name": "Custom Tables", "level": 82},
            {"category": "ServiceNow Platform", "name": "Roles & Permissions", "level": 80},
            {"category": "ServiceNow Platform", "name": "Inbound Email Actions", "level": 78},
            {"category": "ServiceNow Platform", "name": "On-Call Scheduling", "level": 75},
            
            # Frontend & Programming Skills
            {"category": "Development", "name": "HTML", "level": 90},
            {"category": "Development", "name": "CSS", "level": 85},
            {"category": "Development", "name": "JavaScript", "level": 80},
            {"category": "Development", "name": "C++ Fundamentals", "level": 70},
            {"category": "Development", "name": "Python", "level": 75},
            
            # Core Skills
            {"category": "Core Skills", "name": "Critical Thinking", "level": 95},
            {"category": "Core Skills", "name": "Problem Solving", "level": 92},
            {"category": "Core Skills", "name": "Communication", "level": 90},
            {"category": "Core Skills", "name": "Analytical Skills", "level": 88}
        ]
        
        for skill_data in skills_data:
            existing_skill = db.query(Skill).filter(
                Skill.name == skill_data["name"],
                Skill.category == skill_data["category"]
            ).first()
            if not existing_skill:
                skill = Skill(**skill_data)
                db.add(skill)
                db.commit()
                print(f"[OK] Skill '{skill_data['name']}' created")
            else:
                print(f"[OK] Skill '{skill_data['name']}' already exists")
        
        # Seed Services
        services_data = [
            {
                "title": "ServiceNow Development",
                "description": "Expert ServiceNow platform development including custom applications, modules, and integrations tailored to your business needs.",
                "icon": ""
            },
            {
                "title": "Workflow Automation",
                "description": "Automate complex business processes using Flow Designer and workflows to reduce manual intervention and improve efficiency.",
                "icon": "⚙️"
            },
            {
                "title": "ITSM Implementation",
                "description": "Complete IT Service Management implementation including Incident, Problem, Change, and Request Management workflows.",
                "icon": "📋"
            },
            {
                "title": "Process Automation",
                "description": "Streamline your business processes with intelligent automation solutions that save time and reduce errors.",
                "icon": "🚀"
            }
        ]
        
        for service_data in services_data:
            existing_service = db.query(Service).filter(Service.title == service_data["title"]).first()
            if not existing_service:
                service = Service(**service_data)
                db.add(service)
                db.commit()
                print(f"[OK] Service '{service_data['title']}' created")
            else:
                print(f"[OK] Service '{service_data['title']}' already exists")
        
        print("\n[SUCCESS] Database seeded successfully!")
        print("\nLogin credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\n[NOTE] Please change the default password after first login!")
        
    except Exception as e:
        print(f"[ERROR] Error seeding database: {e}")

        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
