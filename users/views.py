from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password , check_password
from django.views.generic import CreateView
from users.forms import *
# from users.models import Account
from django.contrib import messages
from .models import *
from .filters import TransactionFill
from .decorators import unauthenticated_user, allowed_users

#reports import
import datetime
import xlwt
import xlsxwriter
from xlwt import *
from xlsxwriter.workbook import Workbook
import xlrd
import io

#PDF reports import
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.contrib.staticfiles import finders


#for search import
from django.http import JsonResponse


#new Import
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# ================================================================================
#  PDF INDIVIDUAL
@login_required(login_url='Home')
def render_pdf_Individual(request):

	user_trac = request.POST.get("report")
	user = request.user
	# tables
	t = Transaction.objects.get(tracking_number=user_trac)
	fee = delivery_fee(t.item_size, t.delivery_select)
	context = {
		# tables
		"t_tracking" :t.tracking_number, 'user':user,
		"t_name": t.receiver_name, 't_address':t.receiver_address,
		't_contact': t.receiver_contact, 't_item': t.item_desc,
		't_pouch_size': t.item_size, 't_fee': fee,
		't_value': t.item_value,'t_payment': t.item_payment
		 }
	
	html = render_to_string('users/reports_individual_pdf.html',context)
	io_bytes = BytesIO()

	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), io_bytes, encoding='UTF-8')

	if not pdf.err:
		return HttpResponse(io_bytes.getvalue(), content_type='application/pdf')
	else:
		return HttpResponse("Error while rendering PDF", status=400)


# PDF REPORT ALL TRANSACTION
@login_required(login_url='Home')
def render_pdf(request):
	path = "users/reports_pdf.html"
	# tables
	transaction = Transaction.objects.all()[:100]
	deliveryPartner = DeliveryPartner.objects.all()[:100]
	courierPartner = CourierPartner.objects.all()[:100]
	prices = Prices.objects.all()[:100]
	
	# Summary data
	total_transact = Transaction.objects.all().count()
	total_delivery = DeliveryPartner.objects.all().count()
	total_courier = CourierPartner.objects.all().count()
	in_transit = Transaction.objects.filter(admin_approved=True).exclude(delivery_status='delivered').count() 
	pending = Transaction.objects.filter(admin_approved=False).count()

	ready = Transaction.objects.filter(delivery_status='ready_to_pickup').count()
	pickup = Transaction.objects.filter(delivery_status='picked_up').count()
	dispatched = Transaction.objects.filter(delivery_status='dispatched_for_delivery').count()
	delivered = Transaction.objects.filter(delivery_status='delivered').count()
	

	context = {
		# tables
		"transaction" :transaction , "deliveryPartner":deliveryPartner ,
		"courierPartner":courierPartner,"prices": prices,
		# Summary data
		"total_transact": total_transact, "total_delivery": total_delivery,
		"total_courier": total_courier, "in_transit": in_transit, "pending": pending,	
		
		"ready": ready, "pickup": pickup,
		"dispatched": dispatched, "delivered": delivered
		 }
	
	html = render_to_string('users/reports_pdf.html',context)
	io_bytes = BytesIO()

	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), io_bytes)

	if not pdf.err:
		return HttpResponse(io_bytes.getvalue(), content_type='application/pdf')
	else:
		return HttpResponse("Error while rendering PDF", status=400)

# ==================================================================================
# EXPORT EXCEL FILES 

# Export Transaction Reports
@login_required(login_url='Home')
def export_transaction_excel(request):
	output = io.BytesIO()
	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet('Transaction')
	bold = workbook.add_format({'bold': True})

	# Some data we want to write to the worksheet.
	report = Transaction.objects.all() #my model

	# Start from the first cell. Rows and columns are zero indexed.
	row = 1
	col = 0

	# Iterate over the data and write it out row by row.
	for transact in report:
		worksheet.write(row, col, transact.transactor.username)
		worksheet.write(row, col + 1, transact.receiver_id)
		worksheet.write(row, col + 2, transact.tracking_number)
		worksheet.write(row, col + 3, transact.delivery_status)
		# Receiver Info
		worksheet.write(row, col + 4, transact.receiver_name)
		worksheet.write(row, col + 5, transact.receiver_email)
		worksheet.write(row, col + 6, transact.receiver_address)
		worksheet.write(row, col + 7, transact.receiver_contact)
		#  Item Descriptions
		worksheet.write(row, col + 8, transact.item_desc)
		worksheet.write(row, col + 9, transact.item_value)
		worksheet.write(row, col + 10, transact.item_size)
		worksheet.write(row, col + 11, transact.item_payment)
		worksheet.write(row, col + 12, transact.delivery_select)
		worksheet.write(row, col + 13, transact.requested_pickup)
		# Admin Side
		worksheet.write(row, col + 14, transact.admin_approved)
		worksheet.write(row, col + 15, transact.delivery_partner.partner_name)
		worksheet.write(row, col + 16, transact.courier_partner.company_name)
		# worksheet.write(row, col + 17, transact.pub_date)
		row += 1

	# HEADER TITLES 
	worksheet.write('A1', 'Transactor', bold)
	worksheet.write('B1', 'Transaction ID', bold)
	worksheet.write('C1', 'Tracking Number', bold)
	worksheet.write('D1', 'Status', bold)
	# Receiver info
	worksheet.write('E1', 'Receiver Name', bold)
	worksheet.write('F1', 'Receiver Email', bold)
	worksheet.write('G1', 'Receiver Address', bold)
	worksheet.write('H1', 'Receiver Contact', bold)
	# Item Descriptions
	worksheet.write('I1', 'Item Description', bold)
	worksheet.write('J1', 'Item Value', bold)
	worksheet.write('K1', 'Pouch Size', bold)
	worksheet.write('L1', 'Payment Option', bold)
	worksheet.write('M1', 'Location', bold)
	worksheet.write('N1', 'Requested Pickup Date', bold)
	# Admin Side
	worksheet.write('O1', 'Processing', bold)
	worksheet.write('P1', 'Delivery Partner', bold)
	worksheet.write('Q1', 'Courier Partner', bold)
	# worksheet.write('R1', 'Publication Date', bold)
	workbook.close()

	output.seek(0)
	response = HttpResponse(output.read(), content_type="'application/vnd.ms-excel'")
	response['Content-Disposition']='attachment; filename=Transaction '+ \
	str(datetime.datetime.now())+'.xlsx'

	return response
# ==================================================================================
# Export Users Reports
@login_required(login_url='Home')
def export_accounts_excel(request):
	output = io.BytesIO()
	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet('Accounts')
	bold = workbook.add_format({'bold': True})

	# Some data we want to write to the worksheet.
	print("---------------------------------------------",Account)
	report = Account.objects.all() #my model

	# Start from the first cell. Rows and columns are zero indexed.
	row = 1
	col = 0

	# Iterate over the data and write it out row by row.
	for a in report:
		worksheet.write(row, col, a.account_id)
		worksheet.write(row, col + 1, a.email)
		worksheet.write(row, col + 2, a.username)
		worksheet.write(row, col + 3, a.user_address)
		worksheet.write(row, col + 4, a.user_contact)
		worksheet.write(row, col + 5, a.date_joined)
		worksheet.write(row, col + 6, a.last_login)
		worksheet.write(row, col + 7, a.is_admin)
		worksheet.write(row, col + 8, a.is_active)
		worksheet.write(row, col + 9, a.is_staff)
		worksheet.write(row, col + 10, a.is_superuser)
		row += 1

	# HEADER TITLES 
	worksheet.write('A1', 'Acct ID', bold)
	worksheet.write('B1', 'Email', bold)
	worksheet.write('C1', 'Username', bold)
	worksheet.write('D1', 'Address', bold)
	worksheet.write('E1', 'Contact', bold)
	worksheet.write('F1', 'Date Joined', bold)
	worksheet.write('G1', 'Last Login', bold)
	worksheet.write('H1', 'Admin', bold)
	worksheet.write('I1', 'Active', bold)
	worksheet.write('J1', 'Staff', bold)
	worksheet.write('K1', 'SuperUser', bold)
	
	workbook.close()

	output.seek(0)
	response = HttpResponse(output.read(), content_type="'application/vnd.ms-excel'")
	response['Content-Disposition']='attachment; filename=Accounts '+ \
	str(datetime.datetime.now())+'.xlsx'

	return response

# ==================================================================================
# Export Delivery Partners Reports
@login_required(login_url='Home')
def export_partner_excel(request):
	output = io.BytesIO()
	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet('Delivery Partners')
	bold = workbook.add_format({'bold': True})

	# Some data we want to write to the worksheet.
	report = DeliveryPartner.objects.all() #my model

	# Start from the first cell. Rows and columns are zero indexed.
	row = 1
	col = 0

	# Iterate over the data and write it out row by row.
	for a in report:
		worksheet.write(row, col, a.partner_id)
		worksheet.write(row, col + 1, a.partner_name)
		worksheet.write(row, col + 2, a.partner_email)
		worksheet.write(row, col + 3, a.partner_address)
		worksheet.write(row, col + 4, a.partner_contact)
		worksheet.write(row, col + 5, a.partner_birthday)
		worksheet.write(row, col + 6, a.partner_vehicle)
		worksheet.write(row, col + 7, a.partner_gcash)
		worksheet.write(row, col + 8, a.partner_license)
		
		row += 1

	# HEADER TITLES 
	worksheet.write('A1', 'Partner ID', bold)
	worksheet.write('B1', 'Name', bold)
	worksheet.write('C1', 'Email', bold)
	worksheet.write('D1', 'Address', bold)
	worksheet.write('E1', 'Contact', bold)
	worksheet.write('F1', 'Birthday', bold)
	worksheet.write('G1', 'Vehicle', bold)
	worksheet.write('H1', 'GCash', bold)
	worksheet.write('I1', 'License', bold)
	
	workbook.close()

	output.seek(0)
	response = HttpResponse(output.read(), content_type="'application/vnd.ms-excel'")
	response['Content-Disposition']='attachment; filename=DeliveryPartners '+ \
	str(datetime.datetime.now())+'.xlsx'

	return response
# ==================================================================================
# Export Courier Partners Reports
@login_required(login_url='Home')
def export_courier_excel(request):
	output = io.BytesIO()
	workbook = xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet = workbook.add_worksheet('Courier Partners')
	bold = workbook.add_format({'bold': True})

	# Some data we want to write to the worksheet.
	report = CourierPartner.objects.all() #my model

	# Start from the first cell. Rows and columns are zero indexed.
	row = 1
	col = 0

	# Iterate over the data and write it out row by row.
	for a in report:
		worksheet.write(row, col, a.company_id)
		worksheet.write(row, col + 1, a.company_name)
		worksheet.write(row, col + 2, a.company_address)
		worksheet.write(row, col + 3, a.company_contact)
		
		row += 1

	# HEADER TITLES 
	worksheet.write('A1', 'Company ID', bold)
	worksheet.write('B1', 'Company Name', bold)
	worksheet.write('C1', 'Company Address', bold)
	worksheet.write('D1', 'Company Contact', bold)
	
	workbook.close()

	output.seek(0)
	response = HttpResponse(output.read(), content_type="'application/vnd.ms-excel'")
	response['Content-Disposition']='attachment; filename=CourierPartners '+ \
	str(datetime.datetime.now())+'.xlsx'

	return response
# ==================================================================================
def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect
# ===================================================================================
# DELIVERY PARTNER REGISTRATION
def deliveryPartner_reg(request):
	if request.method=='POST' and 'del_sub' in request.POST:
		deliveryPartner = DeliveryPartnerForm(request.POST)
		if deliveryPartner.is_valid():
			deliveryPartner.save()
			messages.info(request, 'Delivery Partner created successfully')	
			return redirect('Home')
		else:
			messages.info(request, 'Invalid Input')	
	return render(request, 'users/Delivery_AND_Courier/Delivery_Partner.html')
# ===================================================================================
# COURIER PARTNER REGISTRATION
def courierPartner(request):
	if request.method == 'POST' and 'cou_sub' in request.POST:
		courierPartner1 = CompanyPartnerForm(request.POST)
		if courierPartner1.is_valid():
			courierPartner1.save()
			messages.info(request, 'Courier Partner created successfully')	
			return redirect('Home')
		else:
			messages.info(request, 'Invalid Input')
	return render(request, 'users/Delivery_AND_Courier/Courier_Partner.html')
# ===================================================================================
# LOGIN/ SIGIN PAGE
@unauthenticated_user
def register_view(request, *args, **kwargs):
	
	#DISPLAY THE LATEST ENTRY FOR THE PRICES
	if Prices.objects.all().last() != None:
		price = Prices.objects.all().last()
		context = {
	 		'metro_manila_small': price.metro_manila_price_small,
	 		'metro_manila_medium': price.metro_manila_price_medium,
	 		'metro_manila_large': price.metro_manila_price_large,
	 		'metro_manila_extra_large': price.metro_manila_price_extra_large,
	 		'metro_manila_box': price.metro_manila_price_box,

	 		'mega_manila_small': price.mega_manila_price_small, 
	 		'mega_manila_medium': price.mega_manila_price_medium,
	 		'mega_manila_large': price.mega_manila_price_large,
	 		'mega_manila_extra_large': price.mega_manila_price_extra_large,
	 		'mega_manila_box': price.mega_manila_price_box,

	 		'provincial_small': price.provincial_price_small,
	 		'provincial_medium': price.provincial_price_medium,
	 		'provincial_large': price.provincial_price_large,
	 		'provincial_extra_large': price.provincial_price_extra_large,
	 		'provincial_box': price.provincial_price_box
	 	}
	else:
	 	context = {}
    #================================================================================ 
    # REGISTRATION
	if request.method=='POST' and 'signUp' in request.POST:
		form = RegistrationForm(request.POST)
		
		if form.is_valid():
			# Account created successfully
			user = form.save()

			# After registration they are to be logged in
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email,password=raw_password)
			login(request,account,backend='django.contrib.auth.backends.ModelBackend')
			
			# san to nakuha??
			destination = get_redirect_if_exists(request)
			
			if destination:
				return redirect(destination)

			messages.info(request, 'Account created successfully')
			return redirect("Home")
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form

	
	destination = get_redirect_if_exists(request)
    #===============================================================================
	# SIGNIN 
	if request.method=='POST' and 'signIn' in request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)
			
			messages.info(request, 'You logged in.')
			if user:
				login(request, user)
				if destination:
					return redirect(destination)
				return redirect("user_dashboard")
			else: 
				print("--------------------------------------------")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	return render(request,'users/login_register.html', context)

# =====================================================================
# USER PROFILE UPDATE
@login_required(login_url='Home')
def profile(request):
	context = {}
	if request.method == 'POST' and 'user_sub' in request.POST:
		form = ProfileUpdate(request.POST, instance=request.user)
		
		if form.is_valid():
			form.save()
			messages.info(request, 'Profile Updated successfully')	
			return redirect('user_profile')
		else:
			context['registration_form'] = form
	else:
		form = ProfileUpdate()
		context['registration_form'] = form
	return render(request, 'users/user_profile.html',context)

# ===============================================================================
@login_required(login_url='Home')
# USER TRANSACTION PAGE
def transaction(request):
	form = TransactionForm()
	if request.method == 'POST' and 'transact_sub' in request.POST:
		transact = Transaction()
		
		if (DeliveryPartner.objects.all().count() != 0) and (CourierPartner.objects.all().count() != 0): 
		
			# Initialized inputs
			dp = DeliveryPartner.objects.all()
			cp = CourierPartner.objects.all()
			
			transact.delivery_partner = dp[0]
			transact.courier_partner = cp[0]
			
			transact.transactor = request.user
			 
			# receiver info 
			transact.receiver_name = request.POST.get('receiver_name')
			transact.receiver_email = request.POST.get('receiver_email')
			transact.receiver_address = request.POST.get('receiver_address')
			transact.receiver_contact = request.POST.get('receiver_contact')
			
			# item info
			transact.item_desc = request.POST.get('item_desc')
			transact.item_value = request.POST.get('item_value')
			transact.item_size = request.POST.get('item_size')
			transact.delivery_select = request.POST.get('delivery_select')
			transact.item_payment = request.POST.get('item_payment')
			if request.POST.get('requested_pickup') == '':
				messages.info(request, 'Transaction cannot be proccess')
			else:
				transact.requested_pickup = request.POST.get('requested_pickup')
				transact.save()
				messages.info(request, 'Transaction created successfully')	
		
		else:
			messages.info(request, 'Transaction cannot be proccess. Try again later.')
			print(DeliveryPartner.objects.all().count(), "==========================")
			print(CourierPartner.objects.all().count() , "==========================")
	
	context = {'form':form}
	return render(request, 'users/user_transaction.html',context)
	


# ================================================================================
@login_required(login_url='Home')
def dashboard(request):
	# Individual PDF report
	if request.method =='POST' and 'report' in request.POST:
		render_pdf_Individual(request)
	
	transact1 = Transaction.objects.all()
	transaction = Transaction.objects.all().filter(transactor=request.user)
	
	# Monitoring (ADMIN)
	if request.user.is_authenticated and request.user.is_staff:
		total = transact1.all().count()
		
		processing = transact1.filter(admin_approved=True).exclude(delivery_status='Delivered').count()
		pending = transact1.filter(admin_approved=False).count()
		delivered = transact1.filter(delivery_status='Delivered').count()

	else:
		# Monitoring (USER)
		total = transaction.all().count()
		processing = transaction.filter(admin_approved=True).exclude(delivery_status='Delivered').count()
		pending = transaction.filter(admin_approved=False).count()
		delivered = transaction.filter(delivery_status='Delivered').count()
	
	
	myFilter = TransactionFill(request.GET, queryset=transaction)
	transaction = myFilter.qs

	if 'term' in request.GET:
		qs = Transaction.objects.filter(receiver_name__icontains=request.GET.get('term'))
		titles = list()
		for transact in qs:
			titles.append(transact.receiver_name)
		return JsonResponse(title, safe=False)

	context = {
		'transaction': transaction,'total':total, 
		'processing':processing, 'pending':pending, 
		'delivered':delivered, 'myFilter':myFilter,
		'transact1':transact1,

	}

	return render(request, 'users/user_dashboard.html',context)


# ========================================================================
# TRACKING SEARCH
def tracking(request):
	context = {'invalid': False, 'reveal': False}
	track = request.GET.get('tracking')	

	if request.method == 'GET' and 'find' in request.GET:
		try:
			t = Transaction.objects.get(tracking_number=track)
			fee = delivery_fee(t.item_size, t.delivery_select)
			invalid = False
			
			context = {
				'invalid': invalid, 'reveal': True, 'tracking_number': t.tracking_number,
				't_status': t.delivery_status, 't_pub_date': t.pub_date, 't_item_s': t.item_size,
				'value': t.item_value, 't_requested_pickup': t.requested_pickup, 't_fee':fee,
			}
		
		except Transaction.DoesNotExist:
			context = {'invalid': True, 'reveal': False}
	return render(request,'users/Delivery_AND_Courier/tracking.html', context)

# =============================================================
# DELIVERY FEE
def delivery_fee(size, location):
	price = Prices.objects.all().last()
	if size == "Small":
		if location == "Metro Manila":
			return	price.metro_manila_price_small
		elif location == "Mega Manila":
			return	price.mega_manila_price_small
		else:
			return price.provincial_price_small
	elif size == "Medium":
		if location == "Metro Manila":
			return price.metro_manila_price_medium
		elif location == "Mega Manila":
			return price.mega_manila_price_medium
		else:
			return price.provincial_price_medium
	elif size == "Large":
		if location == "Metro Manila":
			return price.metro_manila_price_large
		elif location == "Mega Manila":
			return price.mega_manila_price_large
		else:
			return price.provincial_price_large
	elif size == "Extra Large":
		if location == "Metro Manila":
			return price.metro_manila_price_extra_large
		elif location == "Mega Manila":
			return price.mega_manila_price_extra_large
		else:
			return price.provincial_price_extra_large
	else:
		if location == "Metro Manila":
			return	price.metro_manila_price_box
		elif location == "Mega Manila":
			return price.mega_manila_price_box
		else:
			return price.provincial_price_box

# =============================================================
def logoutUser(request):
	logout(request)
	messages.info(request, 'You logged out.')
	return redirect('Home')
