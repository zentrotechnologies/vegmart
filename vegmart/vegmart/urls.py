"""
URL configuration for vegmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # backend
    path('api/Audits/', include('Audits.urls')),
    path('api/Customers/', include('Customers.urls')),
    path('api/Inventory/', include('Inventory.urls')),
    path('api/Logistics/', include('Logistics.urls')),
    path('api/Masters/', include('Masters.urls')),
    path('api/Orders/', include('Orders.urls')),
    path('api/Partners/', include('Partners.urls')),
    path('api/Procurement/', include('Procurement.urls')),
    path('api/Production/', include('Production.urls')),
    path('api/User/', include('User.urls')),
    
    #frontend
    path('inventory/',include(('Frontend_Inventory.urls', 'Frontend_Inventory'),namespace='Frontend_Inventory')),
    path('logistics/',include(('Frontend_Logistics.urls', 'Frontend_Logistics'),namespace='Frontend_Logistics')),
    path('masters/',include(('Frontend_Masters.urls', 'Frontend_Masters'),namespace='Frontend_Masters')),
    path('orders/',include(('Frontend_Orders.urls', 'Frontend_Orders'),namespace='Frontend_Orders')),
    path('procurement/',include(('Frontend_Procurement.urls', 'Frontend_Procurement'),namespace='Frontend_Procurement')),
    path('report/',include(('Frontend_Reports.urls', 'Frontend_Reports'),namespace='Frontend_Reports')),
    path('',include(('Frontend_User.urls', 'Frontend_User'),namespace='Frontend_User')),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
