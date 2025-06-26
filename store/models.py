from django.db import models
from account.models import User
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to='category', default='category/default.jpg', blank=True, null=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Category"
        ordering = ['title']


class Product(models.Model):
    STATUS = (
        ("draft", "Draft"),
        ("desabled", "Desabled"),
        ("in_review", "In Review"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_thumbnail/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    old_price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    stock_qty = models.PositiveIntegerField(default=0)
    inStock = models.BooleanField(default=True)
    status = models.CharField(max_length=100, choices=STATUS, default="published")
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, blank=True, null=True)

    pid = ShortUUIDField(unique=True, length=10, alphabet="abcdefg12345")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def gallery(self):
        return Gallery.objects.filter(product=self)

    def color(self):
        return Color.objects.filter(product=self)

    def size(self):
        return Size.objects.filter(product=self)

    def specification(self):
        return Specification.objects.filter(product=self)

    def orders(self):
        return CartOrderItem.objects.filter(product=self).count()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.FileField(upload_to='product', default='default/product.png', blank=True, null=True)
    active = models.BooleanField(default=True, blank=True, null=True)
    gid = ShortUUIDField(unique=True, length=10, alphabet="abcdefg12345")

    def __str__(self):
        return str(self.product.title)

    class Meta:
        verbose_name_plural = "Product Images"


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Specification"


class Size(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)

    def __str__(self):
        return self.title


class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    color_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    text_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    country = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    cart_id = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart_id} - {self.product.title}"


class CartOrder(models.Model):
    PAYMENT_STATUS = (
        ("paid", "Paid"),
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Cancelled", "Cancelled"),
    )

    ORDER_STATUS = (
        ("Processing", "Processing"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    text_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    payment_Status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default="Pending")
    order_status = models.CharField(choices=ORDER_STATUS, max_length=100, default="Processing")

    initial_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    discount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=100, blank=True, null=True)

    stripe_session_id = models.CharField(max_length=100, blank=True, null=True)
    oid = ShortUUIDField(unique=True, length=10, alphabet="abcdefg12345")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.oid

    def orderItem(self):
        return CartOrderItem.objects.filter(order=self)


class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    text_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    country = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    
    initial_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    discount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    oid = ShortUUIDField(unique=True, length=10, alphabet="abcdefg12345")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.oid
