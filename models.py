from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict


class MsgPayload(BaseModel):
    msg_id: int
    msg_name: str


class MsgRequestPayload(BaseModel):
    msg_name: str


class TransactionCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    OTHER = "other"


class TransactionRequest(BaseModel):
    text: str
    amount: Optional[float] = None


class Transaction(BaseModel):
    id: int
    text: str
    amount: Optional[float] = None
    category: TransactionCategory = TransactionCategory.OTHER
    confidence: float = 1.0


class TransactionResponse(BaseModel):
    transaction: Transaction
    message: str = "Transaction classified successfully"


class TransactionStatsResponse(BaseModel):
    total_transactions: int
    stats: Dict[str, int]
