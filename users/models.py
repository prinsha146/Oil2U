from django.contrib.auth.models import AbstractUser, Permission, Group, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, profile_picture, password=None, is_admin=False, is_staff=False, is_active=True, is_superuser=True):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not full_name:
            raise ValueError("User must have a full name")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.full_name = full_name
        user.set_password(password)  # change password to hash
        user.profile_picture = profile_picture
        user.admin = is_admin
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.admin = True
        user.is_staff = True
        user.active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Customer(AbstractUser):
    objects = CustomUserManager()
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_query_name="custom_user",
        help_text=(
            'The permissions this user has. '
            'Those with the "Can change users" permission '
            'can edit other users.'
        ),
        related_name="custom_user_permissions",
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        related_name="custom_user_groups",
        related_query_name="custom_user",
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    username = None
    email = models.EmailField(unique=True, blank=True)

    # Set the email field as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    company_name= models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_joined = models.DateField(auto_now_add=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        super(Customer, self).save(*args, **kwargs)

    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} has email ${self.email}"

class Order(models.Model):
    class FrequncyEnum(models.TextChoices):
        WEEKLY = 'weekly', ('weekly')
        FORTNIGHT = 'fortnight', ('fortnight') 
    
    class Status(models.TextChoices):
        PROCESSING = 'processing', ('processing')
        CREATED = 'created', ('created')
        PENDING = 'pending', ('pending')
        COMPLETED = 'completed', ('completed')

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=100, blank=True)
    start_date = models.DateField( blank=True)
    next_date = models.DateField( blank=True)
    frequency = models.CharField(
            max_length=20,  choices=FrequncyEnum.choices,
            default=FrequncyEnum.WEEKLY, blank=True,
        )
    status = models.CharField( 
                        max_length=20, 
                        choices=Status.choices,
                        default=Status.CREATED,
                        blank=True,
                    )
    duration = models.DecimalField( max_digits=5, decimal_places=2, blank=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="order")
    
    def __str__(self) -> str:
        return f"{self.email} {self.duration}"

    def save(self, *args, **kwargs):
        self.price = self.quantity * 10
        super(Order, self).save(*args, **kwargs)


class UrgentDelivery(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing', ('processing')
        CREATED = 'created', ('created')
        PENDING = 'pending', ('pending')
        COMPLETED = 'completed', ('completed')

   
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=100,blank=True)
    date = models.DateField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    status = models.CharField( 
                        max_length=20, 
                        choices=Status.choices,
                         default=Status.CREATED,)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="urgent_delivery")
                       
    
    def __str__(self):
        return f"{self.email} has urgernt develivery to {self.address}"

    def save(self, *args, **kwargs):
        self.price = self.quantity * 10
        super(UrgentDelivery, self).save(*args, **kwargs)
    
    
class Invoice(models.Model):
    class PaymentEnum(models.TextChoices):
        Order = 'scheduled', ('scheduled')
        UrgentDelivery = 'urgent', ('urgent')
    
    urgent_delivery = models.ForeignKey(UrgentDelivery, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    user= models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    is_paid = models.BooleanField(default=True)
    payment_type= models.CharField(max_length=20,   choices=PaymentEnum.choices,
        default=PaymentEnum.UrgentDelivery, blank=True)
    payment_date  = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.order_id} has been paid in ${self.payment_date}"

    
class Maintainence(models.Model):

    email = models.EmailField(blank=True)
    address = models.CharField(max_length=100,blank=True)
    date = models.DateField()
    phone_number = models.CharField(max_length=20)
    problem_statment = models.TextField()
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="maintained")
    
    def __str__(self):
        return f"{self.user} has  maintained  to {self.address}"
    

class Notification(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'processing', ('processing')
        CREATED = 'created', ('created')
        PENDING = 'pending', ('pending')
        COMPLETED = 'completed', ('completed')
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    urgent_delivery = models.ForeignKey(UrgentDelivery, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    is_seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField( 
                        max_length=20, 
                        choices=Status.choices,
                        default=Status.CREATED,
                    )
    def __str__(self):
        return f"{self.status} is {self.is_seen}"