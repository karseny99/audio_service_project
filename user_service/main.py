import asyncio
from src.domain.users.services import UserRegistrationService
from src.infrastructure.database.repositories.user_repository \
    import PostgresUserRepository
from src.domain.users.models import User


async def main():
    user_repo = PostgresUserRepository()
    registr_service = UserRegistrationService(user_repo)

    try:
        user = await registr_service.register_user(
            email="test@example.com",
            hash_password="secure123",
            username="test_user"
        )
        print(f"User registered: {user}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
