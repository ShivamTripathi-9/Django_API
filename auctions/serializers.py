# auctions/serializers.py
from rest_framework import serializers
from .models import User, Auction, Bid
from django.utils import timezone

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class BidSerializer(serializers.ModelSerializer):
    bidder = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = ('id', 'auction', 'bidder', 'amount', 'created_at')
        read_only_fields = ('id', 'bidder', 'created_at')

class AuctionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id','title','description','starting_price','reserve_price','start_time','end_time','min_increment')
    
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("end_time must be after start_time")
        if data['end_time'] <= timezone.now():
            raise serializers.ValidationError("end_time must be in the future")
        return data

class AuctionDetailSerializer(serializers.ModelSerializer):
    bids = BidSerializer(many=True, read_only=True)
    winner = serializers.StringRelatedField(read_only=True)
    winner_bid = BidSerializer(read_only=True)

    class Meta:
        model = Auction
        fields = ('id','title','description','starting_price','reserve_price','start_time','end_time','min_increment','status','bids','winner','winner_bid')
