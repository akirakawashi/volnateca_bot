from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from application.common.dto.user import VKUserRegistrationDTO
from application.common.dto.wallet import UserBalanceSnapshot
from application.interface.repositories.users import IUserRepository
from domain.enums.transaction import TransactionSource, TransactionType
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository, IUserRepository):
    """Data access для пользователей VK и их баланса."""

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
        vk_screen_name: str | None,
        bonus_points: int,
    ) -> VKUserRegistrationDTO:
        """Создаёт пользователя с регистрационным бонусом идемпотентно.

        При гонке по уникальному vk_user_id возвращает уже созданного
        пользователя и дозаполняет профиль, если callback принёс новые данные.
        """

        try:
            async with self._session.begin_nested():
                user = User(
                    vk_user_id=vk_user_id,
                    first_name=first_name,
                    last_name=last_name,
                    vk_screen_name=vk_screen_name,
                    balance_points=bonus_points,
                    earned_points_total=bonus_points,
                )
                self._session.add(user)
                await self._session.flush()
                if user.users_id is None:
                    raise RuntimeError("Первичный ключ пользователя не был сгенерирован")
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
        except IntegrityError:
            result = await self._session.execute(
                select(User).where(col(User.vk_user_id) == vk_user_id).with_for_update(),
            )
            user = result.scalar_one()
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if vk_screen_name is not None:
                user.vk_screen_name = vk_screen_name
            return self._to_registration_dto(user=user, created=False)
        return self._to_registration_dto(user=user, created=True)

    async def update_vk_profile(
        self,
        *,
        vk_user_id: int,
        first_name: str | None,
        last_name: str | None,
        vk_screen_name: str | None,
    ) -> None:
        values: dict[str, str] = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if vk_screen_name is not None:
            values["vk_screen_name"] = vk_screen_name
        if not values:
            return

        await self._session.execute(
            update(User)
            .where(col(User.vk_user_id) == vk_user_id)
            .values(**values),
        )
        await self._session.flush()

    async def get_balance_snapshot_for_update(
        self,
        vk_user_id: int,
    ) -> UserBalanceSnapshot | None:
        """Блокирует пользователя и возвращает баланс для последующего начисления."""

        result = await self._session.execute(
            select(User).where(col(User.vk_user_id) == vk_user_id).with_for_update(),
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if user.users_id is None:
            raise RuntimeError("Первичный ключ пользователя не был сгенерирован")

        return UserBalanceSnapshot(
            users_id=user.users_id,
            vk_user_id=user.vk_user_id,
            balance_points=user.balance_points,
            earned_points_total=user.earned_points_total,
        )

    async def apply_balance_change(
        self,
        *,
        users_id: int,
        balance_points: int,
        earned_points_total: int,
        current_level: int,
    ) -> None:
        await self._session.execute(
            update(User)
            .where(col(User.users_id) == users_id)
            .values(
                balance_points=balance_points,
                earned_points_total=earned_points_total,
                current_level=current_level,
            ),
        )
        await self._session.flush()

    @staticmethod
    def _to_registration_dto(
        user: User,
        created: bool,
    ) -> VKUserRegistrationDTO:
        if user.users_id is None:
            raise RuntimeError("Первичный ключ пользователя не был сгенерирован")

        return VKUserRegistrationDTO(
            users_id=user.users_id,
            vk_user_id=user.vk_user_id,
            vk_screen_name=user.vk_screen_name,
            balance_points=user.balance_points,
            created=created,
        )
