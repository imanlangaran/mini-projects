from domain.entities.bid import Bid
from ports.repositories.auction_repository import AuctionRepository
from use_cases.exceptions import AuctionNotFoundError


class SubmitBidUseCase:
    def __init__(self, auction_repository: AuctionRepository):
        self._auction_repository = auction_repository

    async def __call__(self, bid: Bid) -> None:
        auction = await self._auction_repository.get(id=bid.auction_id)
        if not auction:
            raise AuctionNotFoundError(bid.auction_id)