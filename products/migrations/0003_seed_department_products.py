from django.db import migrations
from django.utils.text import slugify


SEED_PRODUCTS = [
    ('Home Products', 'Modern Table Lamp', 'home-table-lamp', '39.99', '59.99'),
    ('Home Products', 'Bamboo Storage Basket', 'home-bamboo-storage-basket', '18.50', '25.00'),
    ('Wearing Products', 'Classic Cotton Hoodie', 'wearing-classic-cotton-hoodie', '34.99', '49.99'),
    ('Wearing Products', 'Everyday Canvas Sneakers', 'wearing-canvas-sneakers', '44.99', '64.99'),
    ('Electronics', 'Wireless Noise Cancelling Headphones', 'electronics-wireless-headphones', '79.99', '109.99'),
    ('Electronics', 'Smart LED Desk Light', 'electronics-smart-led-desk-light', '29.99', '39.99'),
    ('Technology', 'Ultra Slim Laptop Stand', 'technology-laptop-stand', '27.50', '35.00'),
    ('Technology', 'USB-C Fast Charging Hub', 'technology-usb-c-charging-hub', '24.99', '34.99'),
    ('Beauty & Health', 'Daily Glow Skin Set', 'beauty-daily-glow-skin-set', '32.99', '45.99'),
    ('Beauty & Health', 'Wellness Aroma Diffuser', 'beauty-wellness-aroma-diffuser', '26.99', '39.99'),
    ('Sports & Outdoors', 'Insulated Active Water Bottle', 'sports-active-water-bottle', '16.99', '24.99'),
    ('Sports & Outdoors', 'Lightweight Yoga Mat', 'sports-lightweight-yoga-mat', '21.99', '29.99'),
    ('Grocery & Food', 'Organic Pantry Starter Box', 'grocery-organic-pantry-box', '42.99', '54.99'),
    ('Grocery & Food', 'Fresh Garden Salad Mix', 'grocery-fresh-garden-salad', '8.99', '11.99'),
    ('Books & Stationery', 'Hardcover Daily Planner', 'books-hardcover-daily-planner', '12.99', '18.99'),
    ('Books & Stationery', 'Creative Marker Collection', 'books-creative-marker-collection', '14.99', '21.99'),
]


def seed_products(apps, schema_editor):
    User = apps.get_model('accounts', 'CustomUser')
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')

    seller, _ = User.objects.get_or_create(
        email='catalog@shophub.local',
        defaults={
            'username': 'shophub-catalog',
            'first_name': 'ShopHub',
            'last_name': 'Catalog',
            'role': 'seller',
            'is_active': True,
            'is_verified': True,
            'password': '!',
        },
    )

    for category_name, name, slug, price, compare_at_price in SEED_PRODUCTS:
        category = Category.objects.filter(slug=slugify(category_name)).first()
        if not category:
            continue
        Product.objects.get_or_create(
            sku=f'SEED-{slug.upper()}',
            defaults={
                'name': name,
                'slug': slug,
                'description': f'{name} from the ShopHub {category_name} collection.',
                'short_description': f'Quality {name.lower()} at a special introductory price.',
                'category': category,
                'seller': seller,
                'price': price,
                'compare_at_price': compare_at_price,
                'is_featured': True,
                'status': 'active',
            },
        )


def remove_seeded_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(sku__startswith='SEED-').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_seed_store_categories'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_seeded_products),
    ]
