import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resturant_Project.settings')
django.setup()

from Base_App.models import Items

print("🔧 Updating items with CORRECT image paths...")

image_map = {
    'Margherita Pizza': 'delicious-vegan-pizza-social-post_3.jpg',
    'Pepperoni Pizza': 'pepperoni-toast-with-cheese-served-win-bamboo-plate.jpg',
    'Vegetarian Pizza': 'pizza-8319463.jpg',
    'Veggie Pizza': 'pizza-8319463.jpg',
    'Delicious Burger': 'pexels-holoshuriken-14704837.jpg',
    'Tasty Burger': 'pexels-enginakyurt-1437267.jpg',
    'Big Burger': 'tasty-smoke-cooked-food_23-2151259677.jpg',
    'Spicy Burger': 'pexels-zandatsu-32293382.jpg',
    'Spaghetti Carbonara': 'close-up-street-food-neon-light.jpg',
    'Penne Arrabbiata': 'delicious-chicken-cheesy-grilled-cheese-sandwich_961875-54402.jpg',
    'Fettuccine Alfredo': 'side-view-sandwich-with-baked-potato-sauce.jpg',
    'Classic Fries': 'delicious-fries-studio.jpg',
    'Cheese Fries': 'StockCake-Seasoning_French_Fries_1749889532.jpg',
    'Spicy Fries': 'delicious-fries-studio.jpg',
    'Classic Veggie Sandwich': 'cheesy-grilled-cheese-sandwich-303883093.webp',
    'Cheesy Grilled Sandwich': 'front-view-tasty-ham-sandwiches-with-french-fries-dark-surface.jpg',
    'Spicy Paneer Sandwich': 'side-view-club-sandwich-with-salted-cucumbers-lemon-olives-round-white-plate_1.jpg',
    'Chicken Sandwich': 'front-view-tasty-ham-sandwiches-with-french-fries-dark-surface_1.jpg',
}

for item_name, image_file in image_map.items():
    try:
        item = Items.objects.get(item_name=item_name)
        item.image = image_file
        item.save()
        print(f"✅ Updated: {item_name} → {image_file}")
    except Items.DoesNotExist:
        print(f"⚠️  Not found: {item_name}")

print("\n✅ ALL IMAGES UPDATED!")