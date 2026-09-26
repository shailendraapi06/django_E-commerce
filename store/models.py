from django.db import models
from django.urls import reverse
from category.models import Category
# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=100)
    slug            = models.SlugField(max_length=100, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modify_date     = models.DateTimeField(auto_now=True)


    def __str__(self):  
        return self.product_name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


class Variation(models.Model):
    COLOR = 'Color'
    SIZE = 'Size'
    VARIATION_CATEGORIES = [
        (COLOR, 'Color'),
        (SIZE, 'Size'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORIES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'variation_category', 'variation_value')
        ordering = ('variation_category', 'variation_value')

    def __str__(self):
        return f'{self.product.product_name} - {self.variation_category}: {self.variation_value}'
