import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalist_core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cbi.gov', 'cbi12345')
    print('Superuser created.')
else:
    print('Already exists.')
