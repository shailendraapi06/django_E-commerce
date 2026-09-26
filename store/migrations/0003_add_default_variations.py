from django.db import migrations


def add_default_variations(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Variation = apps.get_model('store', 'Variation')

    defaults = {
        'Color': ('Silver', 'Gray', 'Gold', 'Black'),
        'Size': ('S', 'M', 'L', 'XL'),
    }
    for product in Product.objects.all().iterator():
        for category, values in defaults.items():
            for value in values:
                Variation.objects.get_or_create(
                    product_id=product.pk,
                    variation_category=category,
                    variation_value=value,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.RunPython(add_default_variations, migrations.RunPython.noop),
    ]