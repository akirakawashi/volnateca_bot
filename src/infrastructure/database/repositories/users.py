from sqlalchemy import select
from sqlmodel import col

from application.common.dto.user import VKUserRegistrationDTO
from application.interface.repositories.users import IUserRepository
from domain.enums.transaction import TransactionSource, TransactionType
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository, IUserRepository):
    async def get_by_vk_user_id(
        self,
        vk_user_id: int,
    ) -> VKUserRegistrationDTO | None:
        result = await self._session.execute(
            select(User).where(col(User.vk_user_id) == vk_user_id),
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._to_registration_dto(user=user, created=False)

    async def create_registered_user(
        self,
        vk_user_id: int,
        first_name: str | None,
        last_name: str | None,
        bonus_points: int,
    ) -> VKUserRegistrationDTO:
        user = User(
            vk_user_id=vk_user_id,
            first_name=first_name,
            last_name=last_name,
            balance_points=bonus_points,
            earned_points_total=bonus_points,
        )
        self._session.add(user)
        await self._session.flush()
        if user.users_id is None:
            raise RuntimeError("User primary key was not generated")

        self._session.add(
            Transaction(
                users_id=user.users_id,
                transaction_type=TransactionType.ACCRUAL,
                transaction_source=TransactionSource.REGISTRATION,
                amount=bonus_points,
                balance_before=0,
                balance_after=bonus_points,
                description="Бонус за регистрацию в VK-боте",
            ),
        )

        return self._to_registration_dto(user=user, created=True)

    async def update_profile(
        self,
        users_id: int,
        first_name: str | None,
        last_name: str | None,
    ) -> VKUserRegistrationDTO:
        user = await self._session.get(User, users_id)
        if user is None:
            raise RuntimeError(f"User with users_id={users_id} was not found")

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        return self._to_registration_dto(user=user, created=False)

    @staticmethod
    def _to_registration_dto(
        user: User,
        created: bool,
    ) -> VKUserRegistrationDTO:
        if user.users_id is None:
            raise RuntimeError("User primary key was not generated")

        return VKUserRegistrationDTO(
            users_id=user.users_id,
            vk_user_id=user.vk_user_id,
            balance_points=user.balance_points,
            created=created,
        )
