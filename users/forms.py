from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import Account, CourierPartner, DeliveryPartner, Transaction
from django.utils.translation import ugettext_lazy as _ 

from django.contrib.auth import authenticate
from django.contrib.auth import views


#ACCOUNT AUTHENTICATION
class AccountAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")

# ==========================================================================
# CUSTOM USERCREATION FORMS 
class RegistrationForm(UserCreationForm):

	username = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder':'Username', 'class':'form-control', 'id':'validationCustom01'})
		)

	password1 = forms.CharField(
		widget=forms.PasswordInput(attrs={'type':'password','placeholder':'Password', 'class':'form-control', 'id':'validationCustom05'})
		)
	password2 = forms.CharField(
		widget=forms.PasswordInput(attrs={'type':'password','placeholder':'Password Confirmation', 'class':'form-control', 'id':'validationCustom06'})
		)
	# UserCreationForm has built in fields, the following are fields that are not default
	email = forms.EmailField(max_length=50, help_text="Required. Add valid email address", label='Email : ',widget=forms.TextInput(attrs={'placeholder': 'Email', 'class':'form-control', 'id':'validationCustom03'}))
	user_address = forms.CharField(max_length=50, help_text="Required. Add user address", label='Address : ',widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control', 'id':'validationCustom04'}))
	user_contact = forms.CharField(max_length=11, help_text="Required. Add user contact", label='contact : ',widget=forms.TextInput(attrs={'placeholder': 'Contact Number', 'onkeypress':'isInputNumber(event)',
		 'class':'form-control', 'id':'validationCustom02'}))

	class Meta:
		model = Account
		fields = ('username','user_contact', 'user_address', 'email', 'password1', 'password2',)

	def clean_email(self):

		email = self.cleaned_data['email'].lower()
		try:
			account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
		except Exception as e:
			return email
		raise forms.ValidationError('Email "%s" is already in use.' % account)

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
		except  Exception as e:
			return username
		raise forms.ValidationError('Username "%s" is already in use.' % username)

class DeliveryPartnerForm(ModelForm):
	class Meta:
		model = DeliveryPartner
		fields = [
			'partner_name', 'partner_email', 'partner_address', 'partner_contact', 
			'partner_birthday', 'partner_vehicle', 'partner_gcash', 'partner_license', 
		]


class CompanyPartnerForm(ModelForm):
	class Meta:
		model = CourierPartner
		fields = ['company_name','company_address', 'company_contact']


class TransactionForm(ModelForm):
	class Meta:
		model = Transaction
		fields = '__all__'


class ProfileUpdate(UserCreationForm):

	email = forms.EmailField(max_length=50, help_text="Required. Add valid email address")
	user_address = forms.CharField(max_length=50, help_text="Required. Add user address")
	user_contact = forms.CharField(max_length=11, help_text="Required. Add user contact")

	class Meta:
		model = Account
		fields =  ('username','user_contact', 'user_address', 'email', 'password1', 'password2',)

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		try:
			account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
		except Exception as e:
			return email
		raise forms.ValidationError('Email "%s" is already in use.' % account)

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

class searchForm(ModelForm):
	class Meta:
		model = Transaction
		fields = ('receiver_name',)




  