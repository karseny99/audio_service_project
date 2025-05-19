from src.domain.users.repository import UserRepository
from src.core.exceptions import UserNotFoundError, InvalidPasswordError

class AuthUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
    ):
        self._repo = user_repo

    async def execute(self, username: str, password: str) -> str:
        user = await self._repo.get_by_username(username)
        if user is None:
            raise UserNotFoundError(f"User {user.user_id} does not exists")

        if password != user.password_hash.value:
            raise InvalidPasswordError(f"Invalid credentials")
        
        return str(user.user_id)