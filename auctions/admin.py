# auctions/admin.py
from django.contrib import admin
from .models import User, Auction, Bid
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra', {'fields': ('role',)}),
    )

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id','title','status','start_time','end_time','starting_price','reserve_price','winner')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('id','auction','bidder','amount','created_at')
