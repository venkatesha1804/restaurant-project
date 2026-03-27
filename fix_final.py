import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resturant_Project.settings')
django.setup()

from Base_App.models import Items

print("🔧 Updating items with CORRECT image paths (with items/ prefix)...")

image_map = {
    'Margherita Pizza': 'items/delicious-vegan-pizza-social-post_3.jpg',
    'Pepperoni Pizza': 'items/pepperoni-toast-with-cheese-served-win-bamboo-plate.jpg',
    'Vegetarian Pizza': 'items/pizza-8319463.jpg',
    'Veggie Pizza': 'items/pizza-8319463.jpg',
    'Delicious Burger': 'items/pexels-holoshuriken-14704837.jpg',
    'Tasty Burger': 'items/pexels-enginakyurt-1437267.jpg',
    'Big Burger': 'items/tasty-smoke-cooked-food_23-2151259677.jpg',
    'Spicy Burger': 'items/pexels-zandatsu-32293382.jpg',
    'Spaghetti Carbonara': 'items/close-up-street-food-neon-light.jpg',
    'Penne Arrabbiata': 'items/delicious-chicken-cheesy-grilled-cheese-sandwich_961875-54402.jpg',
    'Fettuccine Alfredo': 'items/side-view-sandwich-with-baked-potato-sauce.jpg',
    'Classic Fries': 'items/delicious-fries-studio.jpg',
    'Cheese Fries': 'items/StockCake-Seasoning_French_Fries_1749889532.jpg',
    'Spicy Fries': 'items/delicious-fries-studio.jpg',
    'Classic Veggie Sandwich': 'items/cheesy-grilled-cheese-sandwich-303883093.webp',
    'Cheesy Grilled Sandwich': 'items/front-view-tasty-ham-sandwiches-with-french-fries-dark-surface.jpg',
    'Spicy Paneer Sandwich': 'items/side-view-club-sandwich-with-salted-cucumbers-lemon-olives-round-white-plate_1.jpg',
    'Chicken Sandwich': 'items/front-view-tasty-ham-sandwiches-with-french-fries-dark-surface_1.jpg',
}

for item_name, image_file in image_map.items():
    try:
        item = Items.objects.get(item_name=item_name)
        item.image = image_file
        item.save()
        print(f"✅ Updated: {item_name} → {image_file}")
    except Items.DoesNotExist:
        print(f"⚠️  Not found: {item_name}")

print("\n✅ ALL IMAGES UPDATED WITH items/ PREFIX!")
print("🔄 Refresh your menu page!")
