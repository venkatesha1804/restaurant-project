import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resturant_Project.settings')
django.setup()

from Base_App.models import Items

print("🔧 Fixing image paths...")

items = Items.objects.all()

for item in items:
    if item.image:
        # Remove 'items/' prefix if it exists
        image_path = str(item.image)
        if image_path.startswith('items/'):
            new_path = image_path.replace('items/', '')
            item.image = new_path
            item.save()
            print(f"✅ Fixed: {item.item_name} → {new_path}")
        else:
            print(f"⏭️  Already correct: {item.item_name}")

print("\n✅ ALL IMAGE PATHS FIXED!")
print("🔄 Refresh your menu page to see images!")