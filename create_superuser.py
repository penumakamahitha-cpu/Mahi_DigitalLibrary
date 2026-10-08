import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mahi.settings')
django.setup()

from django.contrib.auth import get_user_model
from library.seed_data import create_all_seed_data

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@library.org')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists. Updating password...")
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print("Password updated successfully.")

# Automatically populate initial seed catalog & circulation demo records if empty
print("Checking and seeding demonstration library records...")
create_all_seed_data()
print("Initialization complete.")
