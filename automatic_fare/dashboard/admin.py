from django.contrib import admin
from django.apps import apps

# Get all models from a specific app (replace 'myapp' with your app name)
app = apps.get_app_config('dashboard')

for model in app.get_models():
    if model not in admin.site._registry:
        try:
            admin.site.register(model)
            print(f"Registered {model.__name__} successfully.")
        except admin.sites.AlreadyRegistered:
            pass
