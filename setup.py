#!/usr/bin/env python3
"""
Setup script for Composting Efficiency Analysis Application
"""

import os
import subprocess
import sys

def install_requirements():
    """Install Python requirements"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
    print("✓ Dependencies installed successfully!")

def create_directories():
    """Create necessary directories"""
    directories = ['exports', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_database():
    """Initialize the database"""
    print("Setting up database...")
    os.chdir('backend')
    subprocess.run([sys.executable, "-c", "from app import app, init_db; app.app_context().push(); init_db()"])
    os.chdir('..')
    print("✓ Database initialized!")

def main():
    """Main setup function"""
    print("🌱 Setting up Composting Efficiency Analysis Application...")
    print("=" * 60)
    
    try:
        install_requirements()
        create_directories()
        setup_database()
        
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print("\nTo start the application:")
        print("1. cd backend")
        print("2. python app.py")
        print("3. Open frontend/login.html in your browser")
        print("\n📚 Check README.md for detailed usage instructions")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
