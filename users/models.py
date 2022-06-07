from django.db import models
from datetime import datetime
from django.utils import timezone
from django.utils.html import mark_safe
import os, random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

now = timezone.now()
# CHOICES
LOCATION = (
	('Metro Manila', 'METRO MANILA'), 
	('Provincial', 'PROVINCIAL'), 
	('Mega Manila', 'MEGA MANILA')
)
POUCH_SIZES = (
	('Small', 'SMALL'), 
	('Medium', 'MEDIUM'), 
	('Large', 'LARGE'), 
	('Extra Large', 'EXTRA LARGE'), 
	('Box', 'BOX')
)
STATUS = (
	('On process','ON PROCESS'),
	('Picked Up','PICKED UP'),
	('Dispatched','DISPATCHED'),
	('Delivered','DELIVERED'),
	('Cancelled','CANCELLED'),
	('Not Delivered','NOT DELIVERED'),
	('Reschedule','RESCHEDULE'),
	('Return to Sender','RETURN TO SENDER'),
)
# STATUS = (
# 	('On process','ON PROCESS'),
# 	('Ready to pickup', 'READY TO PICKUP'),
# 	('Picked up', 'PICKED UP'),
# 	('Dispatched for deliver','DISPATCHED FOR DELIVER'),
# 	('Delivered','DELIVERED')
# )
# PAYMENT_METHOD = (
# 	('Cash on Delivery', 'Cash on delivery'),
# 	('Over the Counter', 'Over the Counter'),
# 	('E Wallet', 'E Wallet'),
# 	('Credit or Debit', 'Credit/Debit Card')
# )
PAYMENT_METHOD = (
	('Paid by Sender', 'Paid by Sender'),
	('COD (All Not Paid)', 'COD (All Not Paid)'),
	('Paid by Receiver', 'Paid by Receiver'),
	('COD (Items Not Paid)', 'COD (Items Not Paid)'),
	('GCash', 'GCash'),
	('Bank Transfer', 'Bank Transfer')
)
class MyAccountManger(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("Users must have an email address")
		if not username:
			raise ValueError("Users must have an username.")
		
		user = self.model(
			email=self.normalize_email(email),
			username=username,
			)
		
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			username=username,
			password=password,
			)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

# class Account(AbstractBaseUser, PermissionsMixin):
class Account(AbstractBaseUser):
	account_id = models.AutoField(primary_key=True, verbose_name='Account ID',unique=True)
	email = models.EmailField(verbose_name="Email", max_length=60, unique=True)
	username = models.CharField(max_length=100, unique=True)
	user_address = models.CharField(max_length=150,verbose_name='Address')
	user_contact = models.CharField(max_length=11, verbose_name='Contact Number')
	date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
	last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
	
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	
	hide_email = models.BooleanField(default=True)

	object = MyAccountManger()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ['username']

	def __str__(self):
		return self.username
	
	@property
	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

# Create your models here.

class DeliveryPartner(models.Model):
	partner_id = models.AutoField(primary_key=True, verbose_name='Partner ID')
	partner_name = models.CharField(max_length=100, verbose_name='Full Name')
	partner_email = models.EmailField(unique=True, max_length=50, verbose_name='Email')
	partner_address = models.CharField(max_length=150,verbose_name='Address')
	partner_contact = models.CharField(max_length=11, verbose_name='Contact Number')
	
	partner_birthday = models.DateField(verbose_name='Birth Date')
	partner_vehicle = models.CharField(max_length=50, verbose_name='Vehicle')
	partner_gcash = models.CharField(max_length=11, verbose_name='GCash Number')
	partner_license = models.CharField(unique=True, max_length=20,verbose_name="Driver's License")

	pub_date = models.DateTimeField(default=timezone.now, verbose_name='Publication Date')

	def __str__(self):
		return self.partner_name

class CourierPartner(models.Model):
	company_id = models.AutoField(primary_key=True, verbose_name='Company ID')
	company_name = models.CharField(max_length=100, verbose_name='Company Name')
	company_address = models.CharField(max_length=150, verbose_name='Company Address')
	company_contact =models.CharField(max_length=11, verbose_name='Contact Number')
	
	def __str__(self):
		return self.company_name

class Prices(models.Model):
	update_id = models.AutoField(primary_key=True, verbose_name='Update Price ID')
	# PROVINCIAL PRICES
	provincial_price_small = models.CharField(max_length=30, verbose_name='Provincial Price Small')
	provincial_price_medium = models.CharField(max_length=30, verbose_name='Provincial Price Medium')
	provincial_price_large = models.CharField(max_length=30, verbose_name='Provincial Price Large')
	provincial_price_extra_large = models.CharField(max_length=30, verbose_name='Provincial Price Extra Large')
	provincial_price_box = models.CharField(max_length=30, verbose_name='Provincial Price Box')
	# METRO MANILA PRICES
	metro_manila_price_small = models.CharField(max_length=30, verbose_name='Metro Manila Price Small')
	metro_manila_price_medium = models.CharField(max_length=30, verbose_name='Metro Manila Price Medium')
	metro_manila_price_large = models.CharField(max_length=30, verbose_name='Metro Manila Price Large')
	metro_manila_price_extra_large = models.CharField(max_length=30, verbose_name='Metro Manila Price Extra Large')
	metro_manila_price_box = models.CharField(max_length=30, verbose_name='Metro Manila Price Box')
	# MEGA MANILA PRICES
	mega_manila_price_small = models.CharField(max_length=30, verbose_name='Mega Manila Price Small')
	mega_manila_price_medium = models.CharField(max_length=30, verbose_name='Mega Manila Price Medium')
	mega_manila_price_large = models.CharField(max_length=30, verbose_name='Mega Manila Price Large')
	mega_manila_price_extra_large = models.CharField(max_length=30, verbose_name='Mega Manila Price Extra Large')
	mega_manila_price_box = models.CharField(max_length=30, verbose_name='Mega Manila Price Box')
	
	pub_date = models.DateTimeField(default=timezone.now, verbose_name='Published Date')	

	def __str__(self):
		return 'Prices Update:' + str(self.pub_date)

class Transaction(models.Model):
	# USER ID
	transactor = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transaction', verbose_name='Account ID')

	# RECEIVER DATA
	receiver_id = models.AutoField(primary_key=True, verbose_name='Receiver ID')
	receiver_name = models.CharField(max_length=100,verbose_name='Receiver Full Name', blank=True) 
	receiver_email = models.EmailField(max_length=100, verbose_name='Receiver Email', blank=True)
	receiver_address = models.CharField(max_length=150,verbose_name='Receiver Address')
	receiver_contact = models.CharField(max_length=11, verbose_name='Contact Number')

	# ITEM DESCRIPTIONS
	item_desc = models.TextField(max_length=250, verbose_name='Item Description' )
	item_value = models.CharField(max_length=30, verbose_name='Item Value')
	item_size = models.CharField(max_length=30, verbose_name='Pouch Size', choices=POUCH_SIZES, default='SMALL')
	item_payment = models.CharField(max_length=50, choices=PAYMENT_METHOD, default='Cash on delivery', verbose_name='Payment method')
	delivery_select = models.CharField(max_length=50, verbose_name='Delivery Selection', choices=LOCATION, default='METRO MANILA')
	requested_pickup = models.DateField(verbose_name='Requested Date Pickup')

	# ADMIN SIDE TRANSACTION (ONLY ADMIN CAN VIEW AND EDIT)	
	admin_approved = models.BooleanField(default=False, verbose_name='Admin Approved')
	delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='delivery_partner', verbose_name='Delivery Partner')
	courier_partner = models.ForeignKey(CourierPartner, on_delete=models.CASCADE, related_name='courier_partner', verbose_name='Courier Partner')
	delivery_status = models.CharField(max_length=100, verbose_name="Delivery Status", choices=STATUS, default='On process')
	pub_date = models.DateTimeField(default=timezone.now, verbose_name='Publication Date')	
	
	now = datetime.now()
	year = str(now.strftime('%Y'))	
	month = str(now.strftime('%m'))
	day = str(now.strftime('%d'))
	trk_num = month + day + year

	# As of now this is only the current date
	tracking_number = models.CharField(max_length=50, verbose_name='Tracking Number', default=trk_num)
	
	def save_tracking_number(self):
		current_id = Transaction.objects.get(tracking_number=self.tracking_number).receiver_id
		
		if current_id > 99:
			current_id = str(current_id)
			a = current_id[-2]
			b = current_id[-1]
			current_id = a + b
		elif current_id < 10:
			current_id = '0' + str(current_id)
		
		if len(self.tracking_number) < 10:
			Transaction.objects.filter(receiver_id=current_id).update(tracking_number=self.tracking_number + str(current_id))
	
	def save(self, *args, **kwargs): 
		super(Transaction, self).save(*args, **kwargs)
		self.save_tracking_number()
	
	def __str__(self):
		return 'Transaction of {} for {}'.format(self.transactor,self.receiver_name)
