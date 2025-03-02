from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction
from typing import Optional, Tuple
import os

class SolanaService:
    def __init__(self, rpc_url: str = None, program_id: str = None):
        self.rpc_url = rpc_url or "https://api.devnet.solana.com"
        self.client = Client(self.rpc_url)
        self.program_id = PublicKey(program_id) if program_id else None
        self.token_mint = None  # Your COD betting token mint address

    async def create_escrow(self, bet_amount: float, creator_pubkey: str) -> Optional[str]:
        """
        Create an escrow account for a new bet.
        This is a placeholder - you'll need to implement the actual Solana program logic.
        """
        try:
            # In reality, you would:
            # 1. Create a PDA for the escrow
            # 2. Transfer tokens from creator to escrow
            # 3. Create escrow account with bet details
            
            # Mock successful escrow creation
            return f"escrow_{creator_pubkey[:8]}_{bet_amount}"
        except Exception as e:
            print(f"Error creating escrow: {str(e)}")
            return None

    async def join_bet(self, escrow_address: str, joiner_pubkey: str, bet_amount: float) -> bool:
        """
        Allow a user to join an existing bet by matching the stake.
        """
        try:
            # In reality, you would:
            # 1. Verify escrow exists and is open
            # 2. Transfer tokens from joiner to escrow
            # 3. Update escrow account state
            
            return True
        except Exception as e:
            print(f"Error joining bet: {str(e)}")
            return False

    async def settle_bet(self, escrow_address: str, winner_pubkey: str) -> bool:
        """
        Settle a bet by transferring tokens from escrow to winner.
        """
        try:
            # In reality, you would:
            # 1. Verify bet is ready to settle
            # 2. Transfer all tokens to winner
            # 3. Close escrow account
            
            return True
        except Exception as e:
            print(f"Error settling bet: {str(e)}")
            return False

    async def get_token_balance(self, wallet_address: str) -> Optional[float]:
        """
        Get the COD token balance for a wallet.
        """
        try:
            # Convert address string to PublicKey
            pubkey = PublicKey(wallet_address)
            
            # Get token account info
            # This is simplified - you'll need proper token account derivation
            response = await self.client.get_token_accounts_by_owner(
                pubkey,
                {"mint": self.token_mint}
            )
            
            if response["result"]["value"]:
                # Parse balance from the first token account
                balance = float(response["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])
                return balance
            
            return 0.0
        except Exception as e:
            print(f"Error getting token balance: {str(e)}")
            return None 