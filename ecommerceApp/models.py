from django.db import models
from django.utils.text import slugify
from PIL import Image
from authentications.models import CustomUser
from base.models import BaseModel
import uuid
import json



class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class ColorVariant(models.Model):
    color_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.color_name


class SizeVariant(models.Model):
    size_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.CASCADE, related_name='sizes')

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    material = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    color_variant = models.ManyToManyField(ColorVariant, null=True, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    def get_product_price_by_size(self, size):
        size_variants = self.size_variant.filter(size_name=size)
        if size_variants.exists():
            size_variant = size_variants.first()
            return size_variant.price 
        else:
            return None
        
    def get_product_price_by_color(self, color):
        try:
            color_variant = self.color_variant.get(color_name=color)
            return color_variant.price 
        except ColorVariant.DoesNotExist:
            return None


        
    def available_sizes_json(self):
        sizes_by_color = {}
        for color in self.color_variant.all():
            sizes_by_color[color.color_name] = [size.size_name for size in color.sizes.all()]
        return json.dumps(sizes_by_color)
    
    def available_sizes_for_color(self, color):
        try:
            color_variant = self.color_variant.get(color_name=color)
            return list(color_variant.sizes.values_list('size_name', flat=True))
        except ColorVariant.DoesNotExist:
            return []


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        img = img.resize((463, 612), Image.BICUBIC)
        img.save(self.image.path)


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=100)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_methods = models.CharField(max_length=50, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('Shipped', 'Shipped'),
        ('On the way', 'On the way'),
        ('Delivered', 'Delivered'),
        ('Cancelled','Cancelled'),
        ('Return', 'Return'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    delivery_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = sum(cart_item.get_total_price() for cart_item in cart_items)
        if self.coupon:
            price -= self.coupon.discount_price
        return price



class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    user = models.ForeignKey(CustomUser,  on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def get_product_price(self):
        price = [self.product.price]

        if self.color_variant:
            color_variant_price = self.color_variant.price
            price.append(color_variant_price)

        if self.size_variant:
            size_variant_price = self.size_variant.price
            price.append(size_variant_price)
        return sum(price)

    def increase_quantity(self):
        self.quantity += 1
        self.save()

    def decrease_quantity(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()

    '''def get_total_price(self):
        price = self.product.price
        if self.color_variant:
            price += self.color_variant.price
        if self.size_variant:
            price += self.size_variant.price
        return price * self.quantity'''
    
    def get_total_price(self):
        total_price = self.product.price
        if self.color_variant:
            total_price += self.product.get_product_price_by_color(self.color_variant)
        if self.size_variant:
            total_price += self.product.get_product_price_by_size(self.size_variant)
        return total_price * self.quantity


    def get_product_price_with_quantity(self):
        return self.get_product_price() * self.quantity

    def get_product_price_with_quantity_with_shipping(self):
        return self.get_product_price_with_quantity() * 20



class Checkout(BaseModel):
    checkout = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='checkouts')
    user = models.ForeignKey(CustomUser,  on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    address1 = models.CharField(max_length=555)
    address2 = models.CharField(max_length=555, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class CODTransaction(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='CODTransaction', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"COD Transaction - Amount: {self.amount}, Order ID: {self.order_id}"
    
class RazorpayTransaction(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='RazorpayTransaction', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Razorpay Transaction - Amount: {self.amount}, Order ID: {self.razor_pay_order_id}"
    

class Wishlist(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

class ReturnStatus(BaseModel):
    STATUS_CHOICES = [
    ('Requested', 'Requested'),
    ('Approved', 'Approved'),
    ('In Transit', 'In Transit'),
    ('Return Received', 'Return Received'),
    ]
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='return_status')
    user = models.ForeignKey(CustomUser,  on_delete=models.CASCADE)
    return_reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    return_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

class OrderCancel(BaseModel):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order_cancel')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cancellation_reason = models.TextField()
    cancellation_date = models.DateTimeField(auto_now_add=True)

class ContactUs(BaseModel):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()

