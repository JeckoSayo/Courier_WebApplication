from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import DeliveryPartner,CourierPartner, Transaction, Prices
from users.models import Account

from .forms import RegistrationForm
from django import forms


from typing import Set

from django.utils.translation import ugettext_lazy as _
# Register your models here.

admin.site.site_header = "CourierApp Admin"
admin.site.site_title = "CourierApp Admin Area"
admin.site.index_title = "CourierApp Administration Area"


class TransactAdmin(admin.ModelAdmin):
	list_display = [
		'admin_approved', 'receiver_id', 'tracking_number','transactor', 
		'receiver_name', 'receiver_email', 'receiver_address', 'receiver_contact',
		'item_desc', 'item_value', 'item_payment', 'delivery_select', 'requested_pickup',
		'delivery_partner', 'courier_partner', 'delivery_status', 'pub_date'
	]
	search_fields = [
		 'receiver_id', 'tracking_number','receiver_name','receiver_contact',
		 'receiver_email','receiver_address', 'receiver_contact','delivery_select', 'requested_pickup',
		 'item_value','delivery_status',
		
	]
	readonly_fields = ['tracking_number']

class PriceUpdateAdmin(admin.ModelAdmin):
	list_display = [
		'update_id', 'pub_date',
		'provincial_price_small', 'provincial_price_medium', 'provincial_price_large', 
		'provincial_price_extra_large', 'provincial_price_box',
		'metro_manila_price_small', 'metro_manila_price_medium', 'metro_manila_price_large',
		'metro_manila_price_extra_large', 'metro_manila_price_box',
		'mega_manila_price_small', 'mega_manila_price_medium', 'mega_manila_price_large',
		'mega_manila_price_extra_large', 'mega_manila_price_box',
	]
	search_fields = ['update_id','pub_date']

class DeliveryPartnerAdmin(admin.ModelAdmin):
	list_display = [
		'partner_id','partner_name','partner_email','partner_address','partner_contact',
		'partner_birthday','partner_vehicle','partner_gcash','partner_license'
	]
	search_fields = [
		'partner_id','partner_name','partner_email','partner_address','partner_contact',
		'partner_birthday','partner_vehicle','partner_gcash','partner_license'
	]

class CourierPartnerAdmin(admin.ModelAdmin):
	list_display = ['company_id','company_name','company_address','company_contact']
	search_fields = ['company_id','company_name','company_address','company_contact']


# REGISTRATION TO THE ADMIN PANEL



'''
	REFERENCE LINK FOR ADMIN CONFIGURATION
	
	https://realpython.com/manage-users-in-django-admin/

'''
@admin.register(User)
class AccountAdmin(UserAdmin):
	def get_form(sel, request, obj=None, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		is_superuser = request.user.is_superuser
		disabled_fields = set()

		if not is_superuser:
			disabled_fields |= {'is_admin','is_superuser', 'user_permissions', 'groups'}

		if (not is_superuser and obj is not None and obj == request.user):
			disabled_fields |= {
			'is_staff'
			'is_superuser',
			'groups',
			'user_permissions',
			}

		for f in disabled_fields:
			if f in form.base_fields:
				form.base_fields[f].disabled = True
		return form


	list_display = ('email','account_id', 'username', 'user_address','user_contact','password','date_joined', 'last_login', 'is_admin', 'is_staff')
	search_fields = ('email', 'username', 'account_id')
	
	readonly_fields = ('account_id', 'date_joined', 'last_login')
	
	# filter_horizontal = ('groups', 'user_permissions',)
	filter_horizontal = ()

	list_filter = ('is_staff', 'is_active', 'is_admin')
	
	fieldsets = (
		(None, {'fields': ('email','username', 'password')}),
		(_('Personal info'), {'fields': ('user_address', 'user_contact')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','is_admin')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
		)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'username', 'password1', 'password2')}
			),
		)

	#def has_add_permission(self, request, obj=None):  # Can't add users
		#return request.user.is_superuser

	#def has_delete_permission(self, request, obj=None):
		#return request.user.is_superuser

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		user = request.user
		return qs if user.is_superuser else qs.filter(is_admin = False)


	# def has_change_permission(self, request, obj=None):
	# 	return request.user.is_superuser or (obj and obj.account_id == request.user.account_id)



# REGISTRATION TO THE ADMIN PANEL

admin.site.register(DeliveryPartner,DeliveryPartnerAdmin)
admin.site.register(CourierPartner,CourierPartnerAdmin)
admin.site.register(Prices,PriceUpdateAdmin)
admin.site.register(Transaction,TransactAdmin)
admin.site.register(Account, AccountAdmin)
