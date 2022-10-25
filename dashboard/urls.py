from django.contrib import admin
from django.urls import path
from django.urls import include
from dashboard import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
	path('admin/', admin.site.urls, name='admin'),
	path('api/', include('api.urls')),

	path('', views.handle_index, name='index'),
]
urlpatterns += staticfiles_urlpatterns()
