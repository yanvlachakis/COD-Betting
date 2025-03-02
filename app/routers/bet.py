from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from datetime import datetime, timedelta
from app.schemas.bet_schemas import (
    BetCreate, BetOut, BetVerification, BetJoinRequest,
    BetType, BetCondition
)
from app.services.llm_ocr_service import LLMOCRService
from app.services.solana_service import SolanaService
import json

router = APIRouter()
llm_service = LLMOCRService()
solana_service = SolanaService()

@router.post("/create", response_model=BetOut)
async def create_bet(bet: BetCreate):
    try:
        # Validate bet conditions
        for condition in bet.conditions:
            if condition.type != BetType.CUSTOM:
                try:
                    float(condition.target_value)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Target value for {condition.type} must be numeric"
                    )

        # Create escrow account for the bet
        escrow_address = await solana_service.create_escrow(
            bet_amount=bet.stake_amount,
            creator_pubkey=str(bet.user_id)  # In reality, get from user's wallet
        )
        
        if not escrow_address:
            raise HTTPException(status_code=400, detail="Failed to create escrow")
        
        # Create bet record
        bet_out = BetOut(
            id=1,  # In reality, from DB
            match_id=bet.match_id,
            stake_amount=bet.stake_amount,
            conditions=bet.conditions,
            status="PENDING",
            created_by=bet.user_id,
            created_at=datetime.utcnow(),
            time_limit_minutes=bet.time_limit_minutes,
            min_kd_ratio=bet.min_kd_ratio,
            required_game_mode=bet.required_game_mode,
            required_map=bet.required_map,
            max_participants=bet.max_participants,
            current_participants=[bet.user_id],
            escrow_address=escrow_address
        )
        
        return bet_out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join")
async def join_bet(join_request: BetJoinRequest):
    try:
        # In reality, get bet details from DB
        bet = {
            "id": join_request.bet_id,
            "stake_amount": join_request.stake_amount,
            "escrow_address": "mock_escrow",
            "min_kd_ratio": 1.5,
            "current_participants": [1],
            "max_participants": 2,
            "time_limit_minutes": 30,
            "created_at": datetime.utcnow() - timedelta(minutes=10)
        }
        
        # Validate time limit
        time_elapsed = datetime.utcnow() - bet["created_at"]
        if time_elapsed > timedelta(minutes=bet["time_limit_minutes"]):
            raise HTTPException(status_code=400, detail="Bet time limit exceeded")

        # Validate max participants
        if len(bet["current_participants"]) >= bet["max_participants"]:
            raise HTTPException(status_code=400, detail="Bet is full")

        # Validate K/D ratio if required
        if bet["min_kd_ratio"] and join_request.player_stats:
            kd_ratio = join_request.player_stats.get("kd_ratio", 0)
            if kd_ratio < bet["min_kd_ratio"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"K/D ratio {kd_ratio} below minimum {bet['min_kd_ratio']}"
                )
        
        # Join the bet on Solana
        success = await solana_service.join_bet(
            escrow_address=bet["escrow_address"],
            joiner_pubkey=str(join_request.user_id),
            bet_amount=join_request.stake_amount
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to join bet")
        
        return {"message": "Successfully joined bet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
async def verify_bet(
    bet_verification: BetVerification,
    screenshot: UploadFile = File(...)
):
    try:
        # Process the COD screenshot
        contents = await screenshot.read()
        match_stats = await llm_service.process_image(contents)
        
        if not match_stats:
            raise HTTPException(status_code=400, detail="Failed to process match stats")
            
        # Validate the stats
        if not llm_service.validate_stats(match_stats):
            raise HTTPException(status_code=400, detail="Invalid match stats")

        # Get bet conditions from DB (mock for now)
        bet_conditions = [
            BetCondition(
                type=BetType.KILLS,
                target_value=20,
                comparison=">",
                description="Must get more than 20 kills"
            )
        ]

        # Verify game mode and map if required
        if bet_verification.game_mode:
            if match_stats["game_info"]["mode"] != bet_verification.game_mode:
                raise HTTPException(
                    status_code=400,
                    detail="Game mode does not match requirement"
                )

        if bet_verification.map_name:
            if match_stats["game_info"]["map"] != bet_verification.map_name:
                raise HTTPException(
                    status_code=400,
                    detail="Map does not match requirement"
                )

        # Check if conditions are met
        conditions_met = True
        for condition in bet_conditions:
            if condition.type == BetType.KILLS:
                player_kills = match_stats["player_stats"]["kills"]
                target = int(condition.target_value)
                if condition.comparison == ">":
                    conditions_met = player_kills > target
                elif condition.comparison == ">=":
                    conditions_met = player_kills >= target
                # Add other comparisons as needed

            if not conditions_met:
                break

        if not conditions_met:
            raise HTTPException(
                status_code=400,
                detail="Bet conditions not met"
            )
            
        # Settle the bet on Solana
        success = await solana_service.settle_bet(
            escrow_address="mock_escrow",
            winner_pubkey=str(bet_verification.verified_by)
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to settle bet")
        
        return {
            "message": "Bet verified and settled",
            "winner_id": bet_verification.verified_by,
            "match_stats": match_stats,
            "conditions_met": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=List[BetOut])
async def get_active_bets(
    game_mode: Optional[str] = None,
    min_stake: Optional[float] = None,
    max_stake: Optional[float] = None
):
    """
    Get list of active bets that users can join.
    Supports filtering by game mode and stake amount.
    """
    # Mock active bets
    bets = [
        BetOut(
            id=1,
            match_id="COD_123",
            stake_amount=100,
            conditions=[
                BetCondition(
                    type=BetType.KILLS,
                    target_value=20,
                    comparison=">",
                    description="Must get more than 20 kills"
                )
            ],
            status="ACTIVE",
            created_by=1,
            created_at=datetime.utcnow(),
            time_limit_minutes=30,
            min_kd_ratio=1.5,
            required_game_mode="Team Deathmatch",
            required_map="Shipment",
            max_participants=2,
            current_participants=[1],
            escrow_address="mock_escrow"
        )
    ]

    # Apply filters
    if game_mode:
        bets = [b for b in bets if b.required_game_mode == game_mode]
    if min_stake:
        bets = [b for b in bets if b.stake_amount >= min_stake]
    if max_stake:
        bets = [b for b in bets if b.stake_amount <= max_stake]

    return bets 