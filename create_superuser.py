#!/usr/bin/env python
"""
Django superuser creation script for Church Management System
This script creates a default admin superuser if one doesn't exist.
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

def create_superuser():
    """Create a default superuser if none exists."""
    User = get_user_model()
    
    # Check if any superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("✓ Superuser already exists. Skipping creation.")
        return True
    
    try:
        # Create the superuser
        user = User.objects.create_superuser(
            username='admin',
            email='admin@church.local',
            password='admin'
        )
        print("✓ Superuser created successfully!")
        print("  Username: admin")
        print("  Password: admin")
        print("  Email: admin@church.local")
        return True
        
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")
        return False

def main():
    """Main function to create superuser."""
    print("Church Management System - Superuser Creation")
    print("=" * 50)
    
    try:
        # Run migrations first
        print("Checking database migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--check'])
        print("✓ Database is up to date")
        
    except SystemExit as e:
        if e.code != 0:
            print("Database needs migration. Running migrations...")
            try:
                execute_from_command_line(['manage.py', 'migrate'])
                print("✓ Database migrations completed")
            except Exception as migration_error:
                print(f"✗ Migration failed: {migration_error}")
                return False
    
    # Create superuser
    print("\nCreating superuser...")
    success = create_superuser()
    
    if success:
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("You can now log in to the admin panel at:")
        print("http://localhost:8000/admin")
        print("=" * 50)
        return True
    else:
        print("\n" + "=" * 50)
        print("Setup completed with errors.")
        print("You may need to create a superuser manually using:")
        print("python manage.py createsuperuser")
        print("=" * 50)
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
