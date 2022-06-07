from django.urls import path 
from django.conf import settings
from . import views  

urlpatterns = [


	path('logout/', views.logoutUser, name="logout"),
	path('', views.register_view, name="Home"),
	# ============================================================
	
	# REPORTS 
	# Reports - Excel
	path('export_transaction_excel',views.export_transaction_excel, name="export-transact-excel" ),
	path('export_courier_excel',views.export_courier_excel, name="export-courier-excel" ),
	path('export_partner_excel',views.export_partner_excel, name="export-partner-excel" ),
	# Reports - PDF 
	path('export_pdf',views.render_pdf, name="export-pdf" ),
	path('export_pdf_Individual',views.render_pdf_Individual, name="Individual" ),
	# ============================================================
	
	# Dashboard links
	path('dashboard/', views.dashboard, name="user_dashboard"),
	path('transaction/', views.transaction, name="user_transaction"),
	path('profile/', views.profile, name="user_profile"),
	path('deliveryReg/',views.deliveryPartner_reg, name="deliveryReg"),
	# path('courierReg/',views.courierPartner, name="courierPartner"),

	path('tracking/',views.tracking, name="tracking"),

]