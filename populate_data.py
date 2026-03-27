import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resturant_Project.settings')
django.setup()

from Base_App.models import ItemList, Items, AboutUs, Feedback

# CREATE CATEGORIES
print("Creating categories...")
Pizza, _ = ItemList.objects.get_or_create(category_name='Pizza', defaults={'description': 'Delicious Pizzas', 'display_order': 1})
Burger, _ = ItemList.objects.get_or_create(category_name='Burger', defaults={'description': 'Juicy Burgers', 'display_order': 2})
Pasta, _ = ItemList.objects.get_or_create(category_name='Pasta', defaults={'description': 'Italian Pasta', 'display_order': 3})
Fries, _ = ItemList.objects.get_or_create(category_name='Fries', defaults={'description': 'Crispy Fries', 'display_order': 4})
Sandwich, _ = ItemList.objects.get_or_create(category_name='Sandwich', defaults={'description': 'Fresh Sandwiches', 'display_order': 5})

# CREATE PIZZA ITEMS
Items.objects.get_or_create(item_name='Margherita Pizza', defaults={'description': 'Classic pizza with mozzarella and basil', 'price': 8.99, 'category': Pizza, 'image': 'delicious-vegan-pizza-social-post_3.jpg', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 15})

Items.objects.get_or_create(item_name='Pepperoni Pizza', defaults={'description': 'Loaded with pepperoni and cheese', 'price': 10.99, 'category': Pizza, 'image': 'pepperoni-toast-with-cheese-served-win-bamboo-plate.jpg', 'is_available': True, 'is_spicy': True, 'preparation_time': 15})

Items.objects.get_or_create(item_name='Veggie Pizza', defaults={'description': 'Fresh vegetables pizza', 'price': 9.99, 'category': Pizza, 'image': 'pizza-8319463.jpg', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 15})

# CREATE BURGER ITEMS
Items.objects.get_or_create(item_name='Delicious Burger', defaults={'description': 'Bold flavors with crunchy layers and creamy sauces', 'price': 6.99, 'category': Burger, 'image': 'pexels-holoshuriken-14704837.jpg', 'is_available': True, 'preparation_time': 12})

Items.objects.get_or_create(item_name='Tasty Burger', defaults={'description': 'Juicy and fresh, perfect mix of crispy and cheesy', 'price': 6.99, 'category': Burger, 'image': 'pexels-enginakyurt-1437267.jpg', 'is_available': True, 'preparation_time': 12})

Items.objects.get_or_create(item_name='Big Burger', defaults={'description': 'Giant burger with fresh veggies and crispy patties', 'price': 7.99, 'category': Burger, 'image': 'tasty-smoke-cooked-food_23-2151259677.jpg', 'is_available': True, 'preparation_time': 14})

Items.objects.get_or_create(item_name='Spicy Burger', defaults={'description': 'Hot peppers and spicy sauce for spice lovers', 'price': 7.49, 'category': Burger, 'image': 'pexels-zandatsu-32293382.jpg', 'is_available': True, 'is_spicy': True, 'preparation_time': 12})

# CREATE PASTA ITEMS
Items.objects.get_or_create(item_name='Spaghetti Carbonara', defaults={'description': 'Creamy sauce with pancetta and parmesan', 'price': 11.99, 'category': Pasta, 'image': 'close-up-street-food-neon-light.jpg', 'is_available': True, 'preparation_time': 18})

Items.objects.get_or_create(item_name='Penne Arrabbiata', defaults={'description': 'Spicy tomato sauce with garlic', 'price': 10.99, 'category': Pasta, 'image': 'delicious-chicken-cheesy-grilled-cheese-sandwich_961875-54402.jpg', 'is_available': True, 'is_spicy': True, 'preparation_time': 16})

Items.objects.get_or_create(item_name='Fettuccine Alfredo', defaults={'description': 'Creamy Alfredo sauce with butter and cream', 'price': 11.99, 'category': Pasta, 'image': 'side-view-sandwich-with-baked-potato-sauce.jpg', 'is_available': True, 'preparation_time': 16})

# CREATE FRIES ITEMS
Items.objects.get_or_create(item_name='Classic Fries', defaults={'description': 'Crispy golden fries with salt', 'price': 3.99, 'category': Fries, 'image': 'delicious-fries-studio.jpg', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 8})

Items.objects.get_or_create(item_name='Cheese Fries', defaults={'description': 'Fries with melted cheddar cheese', 'price': 4.99, 'category': Fries, 'image': 'StockCake-Seasoning_French_Fries_1749889532.jpg', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 10})

Items.objects.get_or_create(item_name='Spicy Fries', defaults={'description': 'Fries with spicy seasoning', 'price': 4.99, 'category': Fries, 'image': 'delicious-fries-studio.jpg', 'is_available': True, 'is_vegetarian': True, 'is_spicy': True, 'preparation_time': 9})

# CREATE SANDWICH ITEMS
Items.objects.get_or_create(item_name='Classic Veggie Sandwich', defaults={'description': 'Fresh vegetables on toasted bread', 'price': 5.99, 'category': Sandwich, 'image': 'cheesy-grilled-cheese-sandwich-303883093.webp', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 10})

Items.objects.get_or_create(item_name='Cheesy Grilled Sandwich', defaults={'description': 'Melted cheese with herbs and butter', 'price': 6.99, 'category': Sandwich, 'image': 'front-view-tasty-ham-sandwiches-with-french-fries-dark-surface.jpg', 'is_available': True, 'is_vegetarian': True, 'preparation_time': 10})

Items.objects.get_or_create(item_name='Spicy Paneer Sandwich', defaults={'description': 'Spicy paneer with veggies', 'price': 7.99, 'category': Sandwich, 'image': 'side-view-club-sandwich-with-salted-cucumbers-lemon-olives-round-white-plate_1.jpg', 'is_available': True, 'is_vegetarian': True, 'is_spicy': True, 'preparation_time': 11})

Items.objects.get_or_create(item_name='Chicken Sandwich', defaults={'description': 'Grilled chicken with lettuce and tomato', 'price': 7.49, 'category': Sandwich, 'image': 'front-view-tasty-ham-sandwiches-with-french-fries-dark-surface_1.jpg', 'is_available': True, 'preparation_time': 11})

# CREATE FEEDBACK
Feedback.objects.get_or_create(user_name='Rajesh Kumar', email='rajesh@example.com', defaults={'description': 'Amazing burgers! Highly recommend!', 'rating': 5, 'is_approved': True})
Feedback.objects.get_or_create(user_name='Priya Sharma', email='priya@example.com', defaults={'description': 'Great pizza with authentic taste!', 'rating': 5, 'is_approved': True})
Feedback.objects.get_or_create(user_name='Arjun Singh', email='arjun@example.com', defaults={'description': 'Perfect pasta! Will come back!', 'rating': 4, 'is_approved': True})
Feedback.objects.get_or_create(user_name='Neha Gupta', email='neha@example.com', defaults={'description': 'Best sandwich ever!', 'rating': 5, 'is_approved': True})
Feedback.objects.get_or_create(user_name='Vikram Patel', email='vikram@example.com', defaults={'description': 'Good quality and reasonable prices!', 'rating': 4, 'is_approved': True})

# CREATE ABOUT US
AboutUs.objects.get_or_create(defaults={'description': 'Welcome to Feane! We serve delicious food made from fresh ingredients. Join us for an amazing dining experience!', 'phone': '+91 9876543210', 'email': 'info@feanefoods.com', 'address': 'Mumbai, India', 'opening_hours': '10 AM - 10 PM'})

print("✅ ALL DATA ADDED SUCCESSFULLY!")
print("🎉 Your menu is ready!")