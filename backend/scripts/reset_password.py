"""Reset a user's password in the database."""
import asyncio
import sys

from sqlalchemy import text

from app.core.security import get_password_hash
from app.database.session import engine


async def main(email: str, new_password: str) -> None:
    hashed = get_password_hash(new_password)
    async with engine.begin() as conn:
        result = await conn.execute(
            text("UPDATE users SET hashed_password = :hash WHERE email = :email RETURNING email"),
            {"hash": hashed, "email": email},
        )
        row = result.fetchone()

    if row:
        print(f"Password updated for {row[0]}")
    else:
        print(f"No user found with email {email}")


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "anilkallakuri@gmail.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "anilkumar123"
    asyncio.run(main(email, password))
