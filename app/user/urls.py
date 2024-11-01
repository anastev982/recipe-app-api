"""URL mapping for the user API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'user'

# Create a router and register the UserViewSet.
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('token/', TokenObtainPairView.as_view(), name='token'),  # JWT Token obtain view
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   # JWT Token refresh view
]


urlpatterns += router.urls
