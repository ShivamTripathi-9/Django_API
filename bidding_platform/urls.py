# bidding_platform/urls.py
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from auctions import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auctions/', views.AuctionCreateView.as_view(), name='create_auction'),  # POST
    path('auctions/active/', views.ActiveAuctionsView.as_view(), name='active_auctions'),  # GET
    path('auctions/<int:pk>/', views.AuctionDetailView.as_view(), name='auction_detail'),  # GET
    path('auctions/<int:auction_id>/bid/', views.PlaceBidView.as_view(), name='place_bid'),  # POST

    path('admin/auctions/', views.AdminAllAuctionsView.as_view(), name='admin_auctions'),  # GET
    path('admin/auctions/<int:auction_id>/force-close/', views.AdminForceCloseView.as_view(), name='admin_force_close'),  # POST
]
