from django.conf.urls import patterns, include, url
from django.contrib import admin

from website import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.home, name='home'),
    url(r'^player/(?P<playlist_id>\d{0,10})/(?P<action>\w{0,10})$', views.player, name='player'),
    url(r'^generator/$', views.generator, name='generator'),
    url(r'^artists/', views.artists, name='artists'),
    url(r'^genres/', views.genres, name='genres'),
    url(r'^countries/', views.countries, name='countries'),
    url(r'^find/', views.find, name='find'),
    url(r'^checkName/', views.checkName, name='checkName'),
)
