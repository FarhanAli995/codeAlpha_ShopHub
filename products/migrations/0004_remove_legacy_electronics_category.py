from django.db import migrations


LEGACY_SLUG = 'electronics-6e0f3324'
CANONICAL_SLUG = 'electronics'


def remove_legacy_category(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')

    legacy = Category.objects.filter(slug=LEGACY_SLUG).first()
    if not legacy:
        return

    canonical = Category.objects.filter(slug=CANONICAL_SLUG).first()
    if canonical:
        Product.objects.filter(category=legacy).update(category=canonical)
    else:
        legacy.slug = CANONICAL_SLUG
        legacy.name = 'Electronics'
        legacy.save(update_fields=['slug', 'name'])
        return

    legacy.delete()


def restore_legacy_category(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    canonical = Category.objects.filter(slug=CANONICAL_SLUG).first()
    if canonical and not Category.objects.filter(slug=LEGACY_SLUG).exists():
        canonical.slug = LEGACY_SLUG
        canonical.save(update_fields=['slug'])


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0003_seed_department_products'),
    ]

    operations = [
        migrations.RunPython(remove_legacy_category, restore_legacy_category),
    ]
