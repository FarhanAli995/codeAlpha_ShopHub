from django.db import migrations
from django.utils.text import slugify


CATEGORY_NAMES = [
    'Home Products',
    'Wearing Products',
    'Electronics',
    'Technology',
    'Beauty & Health',
    'Sports & Outdoors',
    'Grocery & Food',
    'Books & Stationery',
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    for name in CATEGORY_NAMES:
        Category.objects.get_or_create(
            slug=slugify(name),
            defaults={'name': name, 'is_active': True},
        )


def remove_seeded_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(slug__in=[slugify(name) for name in CATEGORY_NAMES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_seeded_categories),
    ]
