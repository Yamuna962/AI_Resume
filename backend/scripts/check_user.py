"""Quick DB check for a user email."""
import asyncio
import sys

from sqlalchemy import text

from app.core.security import verify_password
from app.database.session import engine


async def main(email: str, password: str | None = None) -> None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT email, full_name, hashed_password FROM users WHERE email = :email"),
            {"email": email},
        )
        row = result.fetchone()

    if not row:
        print(f"NOT FOUND: no user with email {email}")
        return

    print(f"FOUND: {row[0]} ({row[1]})")
    if password:
        ok = verify_password(password, row[2])
        print(f"Password '{password}' matches: {ok}")


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "anilkallakuri@gmail.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "anilkumar123"
    asyncio.run(main(email, pwd))
