from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup',
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change',
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done',
    ),
    # Ещё добавить Password_Reset
]
