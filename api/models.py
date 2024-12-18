from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Image(BaseModel):
    default: str
    dark: str

class Meta(BaseModel):
    __typename: Optional[str] = None
    truncatedPan: Optional[str] = None

class Bonus(BaseModel):
    type: str
    amount: int
    extraInfo: str
    text: str

class AccountAmountV2(BaseModel):
    sign: str
    amount: int

class Item(BaseModel):
    id: str
    operationId: str
    purpose: str
    time: datetime
    merchantCategoryCode: str
    merchantName: str
    image: Image
    type: str
    status: str
    sbpMessage: str
    categoryGroupName: str
    accountAmount: int
    bonus: List[Bonus]
    meta: Meta
    accountAmountV2: AccountAmountV2
    isMkkMarked: bool

class Cursors(BaseModel):
    next: Optional[str] = None
    prev: Optional[str] = None

class ClientOperations(BaseModel):
    hasNextPage: bool
    cursors: Cursors
    items: List[Item]

    @classmethod
    def de_json(cls, json_str: str) -> 'ClientOperations':
        return cls.parse_obj(json_str)

    def to_json(self) -> dict:
        return self.json()
