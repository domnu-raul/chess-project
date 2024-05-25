from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    username: str = Field(
        title="The username.", pattern="^\w+$", examples=["john_doe123"]
    )
    email: EmailStr


class UserIn(User):
    password: str = Field(
        title="The password.",
        max_length=255,
        min_length=8,
    )
