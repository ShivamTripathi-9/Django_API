# auctions/tasks.py
from django.utils import timezone
from .models import Auction, Bid
from django.db import transaction
from django.db.models import Max

def close_auction(auction_id, force=False):
    """
    Close an auction (determine the winner according to rules).
    Returns a dict with outcome.
    """
    from django.shortcuts import get_object_or_404
    with transaction.atomic():
        auction = Auction.objects.select_for_update().get(pk=auction_id)
        if auction.status == 'closed':
            return {"status":"already_closed"}

        now = timezone.now()
        if not force and auction.end_time > now:
            return {"status":"not_ended"}

        # get highest bid(s)
        # order by amount desc, then created_at asc to ensure earliest wins on same amount
        bids = Bid.objects.filter(auction=auction).order_by('-amount', 'created_at')
        if not bids.exists():
            auction.status = 'closed'
            auction.winner = None
            auction.winner_bid = None
            auction.save(update_fields=['status','winner','winner_bid','updated_at'])
            return {"status":"closed_no_bids"}

        # highest amount
        highest_amount = bids[0].amount
        # candidate bids with same amount ordered by created_at (earliest first)
        candidate_bids = Bid.objects.filter(auction=auction, amount=highest_amount).order_by('created_at')
        winner_bid = candidate_bids.first()

        # reserve price check
        if auction.reserve_price is not None and highest_amount < auction.reserve_price:
            # highest bid didn't meet reserve -> no winner
            auction.status = 'closed'
            auction.winner = None
            auction.winner_bid = None
            auction.save(update_fields=['status','winner','winner_bid','updated_at'])
            return {"status":"closed_reserve_not_met", "highest_amount": float(highest_amount)}

        # assign winner
        auction.status = 'closed'
        auction.winner = winner_bid.bidder
        auction.winner_bid = winner_bid
        auction.save(update_fields=['status','winner','winner_bid','updated_at'])
        return {"status":"closed_with_winner", "winner": winner_bid.bidder.username, "amount": float(winner_bid.amount)}
