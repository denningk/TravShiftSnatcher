from django.conf.urls import url
from main import views

urlpatterns = [
	# The home view
	url(r'^$', views.home, name='home'),
	# Explicit home view
	url(r'^home/$', views.home, name='home'),
	# Redirect to get token ('/main/gettoken')
	url(r'^gettoken/$', views.gettoken, name='gettoken'),
	# Mail view ('/main/mail/')
	url(r'^mail/$', views.mail, name='mail'),
	# travWatch view ('/main/travwatch')
	url(r'^travwatch/$', views.travWatch, name='travWatch'),
	# loading view ('/main/loading')
	url(r'^loading/$', views.loading, name='loading'),
]