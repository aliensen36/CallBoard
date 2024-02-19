from django.urls import path
from .views import index, other_page, category_ads, AdvertCreateView, LoginView, profile, LogoutView, ProfileEditView, \
    PasswordEditView, RegisterDoneView, RegisterView, user_activate, ProfileDeleteView, ad_detail, profile_ad_add, \
    profile_ad_detail, profile_ad_edit, profile_ad_delete

app_name = 'board'
urlpatterns = [
    path('add/', AdvertCreateView.as_view(), name='add'),
    path('<int:category_pk>/<int:pk>/', ad_detail, name='ad_detail'),
    path('<int:pk>/', category_ads, name='category_ads'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/add/', profile_ad_add, name='profile_ad_add'),
    path('accounts/profile/<int:pk>/', profile_ad_detail, name='profile_ad_detail'),
    path('accounts/profile/edit/<int:pk>/', profile_ad_edit, name='profile_ad_edit'),
    path('accounts/profile/delete/<int:pk>/', profile_ad_delete, name='profile_ad_delete'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/password/edit/', PasswordEditView.as_view(), name='password_edit'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/activate/<str:sign>/', user_activate, name='activate'),
    path('accounts/profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
]
