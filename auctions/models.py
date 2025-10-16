# auctions/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('buyer', 'Buyer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

class Auction(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_price = models.DecimalField(max_digits=12, decimal_places=2)
    reserve_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    min_increment = models.DecimalField(max_digits=12, decimal_places=2, default=10.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    winner = models.ForeignKey('auctions.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='won_auctions')
    winner_bid = models.ForeignKey('Bid', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # optional: created_by, if admin who created
    created_by = models.ForeignKey('auctions.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_auctions')

    def __str__(self):
        return f"{self.title} ({self.status})"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey('auctions.User', on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # optional metadata: ip address, etc.

    class Meta:
        ordering = ['-amount', 'created_at']  # important for winner tie logic (earliest wins on same amount via created_at)
