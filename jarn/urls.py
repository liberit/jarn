
from django.conf.urls import patterns, include, url
from jarn.views import index, authzone, logout_redirect, upload

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', index),
    url(r'^auth$', authzone),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', logout_redirect),
    url(r'^upload$', upload),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # url(r'^jarn/', include('jarn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
