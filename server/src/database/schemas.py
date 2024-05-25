from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(
        title="The username.", pattern="^\w+$", examples=["john_doe123"]
    )
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        title="The password.",
        max_length=255,
        min_length=8,
    )


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
