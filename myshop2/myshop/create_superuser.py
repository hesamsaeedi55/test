#!/usr/bin/env python
"""
Create a superuser for the Django app
Run this via: python manage.py shell < create_superuser.py
Or: python create_superuser.py (if run from myshop2/myshop/)
"""

import os
import sys
import django

# Setup Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
    django.setup()

from accounts.models import Customer

def create_superuser():
    """Create a superuser if one doesn't exist"""
    email = 'admin@example.com'
    password = 'admin123'
    
    if Customer.objects.filter(email=email, is_staff=True).exists():
        print(f"✅ Superuser {email} already exists")
        return
    
    try:
        user = Customer.objects.create_superuser(
            email=email,
            password=password,
            username='admin'
        )
        print(f"✅ Superuser created!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change this password after logging in!")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()

