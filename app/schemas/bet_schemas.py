from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class BetStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BetType(str, Enum):
    KILLS = "KILLS"
    SCORE = "SCORE"
    PLACEMENT = "PLACEMENT"
    CUSTOM = "CUSTOM"

class BetCondition(BaseModel):
    type: BetType
    target_value: Union[int, str]  # Number for kills/score, string for custom conditions
    comparison: str = Field(
        description="Comparison operator: '>', '<', '>=', '<=', '==', '!='",
        default=">"
    )
    description: Optional[str] = None

class BetCreate(BaseModel):
    match_id: str
    stake_amount: float
    conditions: List[BetCondition]  # Multiple conditions can be combined
    user_id: int
    time_limit_minutes: Optional[int] = Field(
        default=30,
        description="Time limit in minutes to join the bet"
    )
    min_kd_ratio: Optional[float] = Field(
        default=None,
        description="Minimum K/D ratio required to join"
    )
    required_game_mode: Optional[str] = Field(
        default=None,
        description="Required game mode (e.g., 'Team Deathmatch', 'Warzone')"
    )
    required_map: Optional[str] = Field(
        default=None,
        description="Required map name"
    )
    max_participants: Optional[int] = Field(
        default=2,
        description="Maximum number of participants (2 for head-to-head, >2 for pool)"
    )

class BetOut(BaseModel):
    id: int
    match_id: str
    stake_amount: float
    conditions: List[BetCondition]
    status: BetStatus
    created_by: int
    created_at: datetime
    time_limit_minutes: int
    min_kd_ratio: Optional[float]
    required_game_mode: Optional[str]
    required_map: Optional[str]
    max_participants: int
    current_participants: List[int]
    escrow_address: str
    winner_id: Optional[int] = None

    class Config:
        from_attributes = True

class BetVerification(BaseModel):
    bet_id: int
    match_stats: dict  # Parsed stats from the COD screenshot
    verified_by: int
    game_mode: Optional[str]
    map_name: Optional[str]
    match_duration: Optional[int]  # in seconds
    player_stats: dict  # Additional player stats for verification

class BetJoinRequest(BaseModel):
    bet_id: int
    user_id: int
    stake_amount: float
    player_stats: Optional[dict] = Field(
        default=None,
        description="Optional player stats to verify K/D ratio requirement"
    ) 