from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from accounts.views import home_view, signup_view, profile_view, activation_sent_view, activate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name="home"),
    path('signup/', signup_view, name="signup"),
    path('profile/', profile_view, name="profile"),




    path('sent/', activation_sent_view, name="activation_sent"),
    
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),
]
