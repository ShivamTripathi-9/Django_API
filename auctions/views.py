# auctions/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from .models import Auction, Bid, User
from .serializers import UserRegisterSerializer, AuctionCreateSerializer, AuctionDetailSerializer, BidSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
import datetime

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

# Use SimpleJWT's TokenObtainPairView for login.

class AuctionCreateView(generics.CreateAPIView):
    serializer_class = AuctionCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_admin():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admin users can create auctions")
        serializer.save(created_by=user, status='scheduled')

class ActiveAuctionsView(generics.ListAPIView):
    serializer_class = AuctionDetailSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        now = timezone.now()
        # Active auctions where start_time <= now < end_time, and status not 'closed'
        qs = Auction.objects.filter(start_time__lte=now, end_time__gt=now).exclude(status='closed')
        # Also ensure status is 'active' or scheduled but currently active:
        # optionally update status to active on-the-fly - for response we can set those
        return qs

class AuctionDetailView(generics.RetrieveAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer
    permission_classes = (permissions.AllowAny,)

class PlaceBidView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, auction_id):
        user = request.user
        if user.role != 'buyer' and not user.is_admin():
            return Response({"detail":"Only buyers can place bids."}, status=status.HTTP_403_FORBIDDEN)

        try:
            bid_amount = request.data.get('amount')
            if bid_amount is None:
                return Response({"detail":"amount is required"}, status=status.HTTP_400_BAD_REQUEST)
            bid_amount = float(bid_amount)
        except ValueError:
            return Response({"detail":"invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        # Use transaction + select_for_update on auction row
        from django.shortcuts import get_object_or_404
        with transaction.atomic():
            auction = Auction.objects.select_for_update().select_related('winner').get(pk=auction_id)

            now = timezone.now()
            # check active window
            if not (auction.start_time <= now < auction.end_time):
                return Response({"detail":"Auction is not active."}, status=status.HTTP_400_BAD_REQUEST)

            # check user's last bid frequency (e.g., 1 bid per 5 seconds)
            min_seconds_between_bids = 5
            last_bid = Bid.objects.filter(bidder=user).order_by('-created_at').first()
            if last_bid:
                delta = (now - last_bid.created_at).total_seconds()
                if delta < min_seconds_between_bids:
                    return Response({"detail":f"Too many bids. Please wait {min_seconds_between_bids - int(delta)} seconds."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # find current highest valid bid (amount)
            highest_bid = Bid.objects.filter(auction=auction).order_by('-amount', 'created_at').first()
            if highest_bid:
                current_highest = float(highest_bid.amount)
            else:
                current_highest = float(auction.starting_price)

            min_increment = float(auction.min_increment or 10.0)
            required_min = current_highest + min_increment

            if bid_amount < required_min:
                return Response({"detail":f"Bid must be at least {required_min:.2f} (current highest {current_highest:.2f} + min increment {min_increment:.2f})."}, status=status.HTTP_400_BAD_REQUEST)

            # all checks passed, create bid
            bid = Bid.objects.create(auction=auction, bidder=user, amount=bid_amount)
            # optional: update auction status to active
            if auction.status != 'active':
                auction.status = 'active'
                auction.save(update_fields=['status','updated_at'])

            serializer = BidSerializer(bid)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class AdminAllAuctionsView(generics.ListAPIView):
    serializer_class = AuctionDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_admin():
            return Response({"detail":"Admin only."}, status=status.HTTP_403_FORBIDDEN)
        qs = Auction.objects.all().order_by('-created_at')
        serializer = AuctionDetailSerializer(qs, many=True)
        return Response(serializer.data)

class AdminForceCloseView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, auction_id):
        user = request.user
        if not user.is_admin():
            return Response({"detail":"Admin only."}, status=status.HTTP_403_FORBIDDEN)
        try:
            auction = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            return Response({"detail":"Auction not found."}, status=status.HTTP_404_NOT_FOUND)

        # close and determine winner similarly to background job
        from .tasks import close_auction
        closed = close_auction(auction.id, force=True)
        return Response({"detail":"Auction force-closed.", "result": closed}, status=status.HTTP_200_OK)
