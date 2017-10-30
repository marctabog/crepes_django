from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^process$', views.process, name='process'),
    url(r'^some_view$', views.some_view, name='some_view'),
    url(r'^contact/$', views.contact, name='contact')
]