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
        # ----------------------------------------------------
        # 1. ADMIN USER SETUP (non-destructive)
        #
        # Only inserts the default admin account when the users
        # table is completely empty.  Once an admin exists — even
        # if the credentials were changed through the admin panel —
        # this block is skipped entirely so user modifications are
        # never overwritten on restart.
        # ----------------------------------------------------
        if db.query(User).count() == 0:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                hashed_password=get_password_hash(admin_password)
            )
            db.add(admin_user)
            db.commit()
            print(f"[OK] Admin user created (username: {admin_username})")
        else:
            print(f"[INFO] Admin user already exists. Skipping default admin seeding.")

        # ----------------------------------------------------
        # 2. SEED INITIAL PROJECTS DATA (Only if projects table is empty)
        # ----------------------------------------------------
        if db.query(Project).count() == 0:
            projects_data = [
                {
                    "title": "Portfolio Website",
                    "description": "A personal portfolio website showcasing ServiceNow development skills, projects, and professional experience with a modern responsive design.",
                    "features": "Dynamic content loading\nAdmin panel for content management\nResponsive design\nContact form integration",
                    "tech_stack": "FastAPI, HTML, CSS, JavaScript, MySQL",
                    "image_url": "/images/portfolio-project.svg"
                },
                {
                    "title": "Crypto Exchange Mini App",
                    "description": "A front-end mini application simulating a cryptocurrency exchange interface, built to strengthen component-based design and state management skills in React.",
                    "features": "Real-time price updates\nInteractive trading interface\nPortfolio tracking\nResponsive design",
                    "tech_stack": "React, JavaScript, CSS",
                    "image_url": "/images/crypto-exchange-mini-app.svg"
                },
                {
                    "title": "Snake Game",
                    "description": "A classic browser-based Snake game built from scratch, focusing on DOM manipulation, event handling, and game-loop logic.",
                    "features": "Classic gameplay mechanics\nScore tracking\nResponsive controls\nSmooth animations",
                    "tech_stack": "HTML, CSS, JavaScript",
                    "image_url": "/images/snake-game.svg"
                },
                {
                    "title": "Tic Tac Toe Game",
                    "description": "An interactive two-player Tic Tac Toe game demonstrating logic building, win-condition checks, and clean UI design.",
                    "features": "Two-player mode\nWin detection\nReset functionality\nClean UI",
                    "tech_stack": "HTML, CSS, JavaScript",
                    "image_url": "/images/tic-tac-toe-game.svg"
                },
                {
                    "title": "Color Generator Tool",
                    "description": "A utility tool that generates and displays random color codes, built to practice DOM manipulation and dynamic styling.",
                    "features": "Random color generation\nHex code display\nCopy to clipboard\nColor preview",
                    "tech_stack": "HTML, CSS, JavaScript",
                    "image_url": "/images/color-generator-tool.svg"
                }
            ]
            for project_data in projects_data:
                project = Project(**project_data)
                db.add(project)
            db.commit()
            print(f"[OK] Initial projects table seeded cleanly ({len(projects_data)} projects)")
        else:
            print("[INFO] Projects table already contains user data. Skipping default project seeding.")

        # ----------------------------------------------------
        # 3. SEED SKILLS (Only if skills table is empty)
        # ----------------------------------------------------
        if db.query(Skill).count() == 0:
            skills_data = [
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
                
                {"category": "Development", "name": "HTML", "level": 90},
                {"category": "Development", "name": "CSS", "level": 85},
                {"category": "Development", "name": "JavaScript", "level": 80},
                {"category": "Development", "name": "C++ Fundamentals", "level": 70},
                {"category": "Development", "name": "Python", "level": 75},
                
                {"category": "Core Skills", "name": "Critical Thinking", "level": 95},
                {"category": "Core Skills", "name": "Problem Solving", "level": 92},
                {"category": "Core Skills", "name": "Communication", "level": 90},
                {"category": "Core Skills", "name": "Analytical Skills", "level": 88}
            ]
            for skill_data in skills_data:
                skill = Skill(
                    category=skill_data["category"],
                    name=skill_data["name"],
                    level=str(skill_data["level"])
                )
                db.add(skill)
            db.commit()
            print(f"[OK] Initial skills table seeded cleanly ({len(skills_data)} skills)")
        else:
            print("[INFO] Skills table already contains user data. Skipping default skill seeding.")

        # ----------------------------------------------------
        # 4. SEED SERVICES (Only if services table is empty)
        # ----------------------------------------------------
        if db.query(Service).count() == 0:
            services_data = [
                {
                    "title": "ServiceNow Development",
                    "description": "Expert ServiceNow platform development including custom applications, modules, and integrations tailored to your business needs.",
                    "icon": "⚡"
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
                service = Service(**service_data)
                db.add(service)
            db.commit()
            print(f"[OK] Initial services table seeded cleanly ({len(services_data)} services)")
        else:
            print("[INFO] Services table already contains user data. Skipping default service seeding.")
        
        print("\n[SUCCESS] Database setup & verification completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
