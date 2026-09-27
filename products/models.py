from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from accounts.models import CustomUser


# ─────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────
class Category(models.Model):
    """
    Hierarchical category tree using a self-referential ForeignKey.
    e.g.  Electronics → Phones → Smartphones

    Relationship:
      • Self-referential ForeignKey: a category can have a parent category.
        parent=None means it is a root category.
        Deleting a parent sets children's parent to NULL (SET_NULL).
      • One Category ──► Many Product
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    parent = models.ForeignKey(
        'self',                          # refers to same model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',    # access as: cat.subcategories.all()
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────
# BRAND
# ─────────────────────────────────────────────────────────
class Brand(models.Model):
    """
    A product brand (Apple, Samsung, Nike, etc.).

    Relationship:
      • One Brand ──► Many Product
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────────────────────
class Product(models.Model):
    """
    The core product listing.

    Relationships:
      • ForeignKey → Category  (many products belong to one category)
      • ForeignKey → Brand     (many products belong to one brand)
      • ForeignKey → CustomUser (seller who listed this product)
      • One Product ──► Many ProductImage
      • One Product ──► Many ProductVariant
      • One Product ──► One Inventory
      • One Product ──► Many Review
      • One Product ──► Many CartItem
      • One Product ──► Many OrderItem
    """

    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('active',    'Active'),
        ('inactive',  'Inactive'),
        ('deleted',   'Deleted'),
    ]

    # Core fields
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text='Stock Keeping Unit – unique product code',
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='The seller who listed this product.',
    )

    # Pricing — always use DecimalField for money
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Original price before discount, shown as strikethrough.',
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Internal cost — not shown to customers.',
    )

    # Physical dimensions (for shipping calculation)
    weight = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text='Weight in kilograms.',
    )

    # Flags
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(
        default=False,
        help_text='Digital products skip shipping.',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=350, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['seller']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f'{self.name} (PKR {self.price})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        """Returns how much % cheaper the product is vs compare_at_price."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return round((1 - self.price / self.compare_at_price) * 100)
        return 0

    @property
    def thumbnail(self):
        """Returns the primary image or None."""
        img = self.images.filter(is_primary=True).first()
        return img.image if img else None


# ─────────────────────────────────────────────────────────
# PRODUCT IMAGE
# ─────────────────────────────────────────────────────────
class ProductImage(models.Model):
    """
    Multiple images per product; one is flagged as primary (thumbnail).

    Relationship:
      • ForeignKey → Product (many images belong to one product).
        Deleting the product deletes all its images (CASCADE).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(
        default=False,
        help_text='The primary image shown on product cards.',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Display order (lower = first).',
    )

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', '-is_primary']

    def __str__(self):
        return f'Image for {self.product.name} (primary={self.is_primary})'


# ─────────────────────────────────────────────────────────
# PRODUCT VARIANT
# ─────────────────────────────────────────────────────────
class ProductVariant(models.Model):
    """
    Size / colour / material variants of a single product.
    e.g. iPhone 15 Pro → Color: Black, Size: 256GB

    Relationship:
      • ForeignKey → Product (many variants for one product).
        Deleting the product deletes all variants (CASCADE).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    name = models.CharField(
        max_length=100,
        help_text='e.g. "Black / 256GB"',
    )
    sku_suffix = models.CharField(
        max_length=50,
        blank=True,
        help_text='Appended to product SKU to form variant SKU.',
    )
    price_modifier = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text='Added to or subtracted from the base product price.',
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text='Stock level for this specific variant.',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = [('product', 'name')]   # no duplicate variant names per product

    def __str__(self):
        return f'{self.product.name} – {self.name}'

    @property
    def final_price(self):
        return self.product.price + self.price_modifier


# ─────────────────────────────────────────────────────────
# INVENTORY
# ─────────────────────────────────────────────────────────
class Inventory(models.Model):
    """
    Tracks stock quantity for a product (non-variant stock).
    If the product has variants, each variant tracks its own stock.

    Relationship:
      • OneToOne → Product (one inventory record per product).
        Deleting the product deletes inventory (CASCADE).
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
    )
    quantity = models.PositiveIntegerField(
        default=0,
        help_text='Current stock. Cannot go negative (PositiveIntegerField).',
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        help_text='Alert when stock falls to or below this value.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f'{self.product.name} — stock: {self.quantity}'

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.low_stock_threshold

