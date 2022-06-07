import django_filters
from django_filters import DateFilter
from .models import *

class TransactionFill(django_filters.FilterSet):

	class Meta:
		model = Transaction
		fields = ['receiver_email']
# 		exclude=['transact','receiver_name','receiver_email','receiver_address',

# 'item_desc','date_pickup','delivery_select','delivery_partner',
# 'courier_partner','transact_time','pub_date']