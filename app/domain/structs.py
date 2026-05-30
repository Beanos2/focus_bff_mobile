from enum import Enum
from typing import List, Optional, TypeVar, Type, Any
import msgspec


T = TypeVar("T", bound="BaseModel")

class BaseModel(msgspec.Struct):
    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtins(self) # type: ignore

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        return msgspec.convert(data, type=cls)

class UserRole(str, Enum):
    STUDENT = "student"
    DM = "dm"
    ADMIN = "admin"

# IN

class LoginPayload(BaseModel):
    email: str
    password: str

class RegisterPayload(BaseModel):
    email: str
    password: str
    role: Optional[UserRole] = UserRole.STUDENT

class SessionItem(BaseModel):
    activity_type: str
    start_time: str
    end_time: str
    room_id: Optional[str] = None

class SyncPayload(BaseModel):
    sessions: List[SessionItem]

# OUT

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RegisterResponse(BaseModel):
    id: str
    email: str

class RewardItem(BaseModel):
    id: str
    name: str

class SyncResponse(BaseModel):
    status: str
    processed_sessions_count: int
    total_exp_gained: int
    current_level: int
    leveled_up: bool
    levels_gained: int
    rewards: List[RewardItem]