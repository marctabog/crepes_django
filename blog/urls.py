from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^process$', views.process, name='process'),
    url(r'^accueil$', views.home),
    url(r'^contact/$', views.contact, name='contact')
]