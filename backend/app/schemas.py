from pydantic import BaseModel, constr


class FAQBase(BaseModel):
    question: str
    answer: str


class FAQCreate(FAQBase):
    pass


class FAQ(FAQBase):
    id: int

    class Config:
        orm_mode = True


class ChatInput(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
