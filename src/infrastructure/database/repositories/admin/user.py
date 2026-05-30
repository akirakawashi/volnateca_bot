import re

from sqlalchemy import func, or_, select
from sqlmodel import col

from application.admin.dto.user import (
    UserProfileAdminDTO,
    UserReferralRowDTO,
    UserReferralsAdminDTO,
    UserSearchHitDTO,
)
from application.admin.interface.repositories.user import IUserAdminRepository
from domain.enums.prize import PrizeRedemptionStatus
from domain.services.level import get_level_name
from infrastructure.database.models.prize_redemptions import PrizeRedemption
from infrastructure.database.models.referrals import Referral
from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import SQLAlchemyRepository

_REDEMPTION_CODE_PATTERN = re.compile(r"^VLT[-A-Z0-9]+$", re.IGNORECASE)


class UserAdminRepository(SQLAlchemyRepository, IUserAdminRepository):
    async def search(self, *, query: str, limit: int) -> tuple[UserSearchHitDTO, ...]:
        normalized = query.strip()
        if not normalized:
            return ()

        capped_limit = max(1, min(limit, 20))

        if _looks_like_redemption_code(normalized):
            return await self._search_by_redemption_code(
                code=normalized.replace(" ", "").upper(),
                limit=capped_limit,
            )

        if normalized.isdigit() and len(normalized) >= 5:
            by_id = await self._search_by_numeric_id(
                value=int(normalized),
                limit=capped_limit,
            )
            if by_id:
                return by_id

        return await self._search_by_name(normalized=normalized, limit=capped_limit)

    async def exists(self, *, users_id: int) -> bool:
        result = await self._session.execute(
            select(col(User.users_id)).where(col(User.users_id) == users_id).limit(1),
        )
        return result.scalar_one_or_none() is not None

    async def get_profile(self, *, users_id: int) -> UserProfileAdminDTO | None:
        result = await self._session.execute(select(User).where(col(User.users_id) == users_id))
        user = result.scalar_one_or_none()
        if user is None or user.users_id is None:
            return None

        referrals_sent_count = int(
            (
                await self._session.execute(
                    select(func.count())
                    .select_from(Referral)
                    .where(col(Referral.inviter_users_id) == users_id),
                )
            ).scalar_one(),
        )
        redemptions_reserved_count = int(
            (
                await self._session.execute(
                    select(func.count())
                    .select_from(PrizeRedemption)
                    .where(
                        col(PrizeRedemption.users_id) == users_id,
                        col(PrizeRedemption.prize_redemption_status) == PrizeRedemptionStatus.RESERVED,
                    ),
                )
            ).scalar_one(),
        )

        return UserProfileAdminDTO(
            users_id=user.users_id,
            vk_user_id=user.vk_user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            vk_screen_name=user.vk_screen_name,
            display_name=_build_display_name(user=user),
            balance_points=user.balance_points,
            earned_points_total=user.earned_points_total,
            spent_points_total=user.spent_points_total,
            current_level=user.current_level,
            level_name=get_level_name(user.current_level),
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            referrals_sent_count=referrals_sent_count,
            redemptions_reserved_count=redemptions_reserved_count,
        )

    async def list_referrals_for_user(self, *, users_id: int) -> UserReferralsAdminDTO:
        inviter_result = await self._session.execute(
            select(Referral, User)
            .join(User, col(User.users_id) == col(Referral.inviter_users_id))
            .where(col(Referral.invited_users_id) == users_id),
        )
        inviter_row = inviter_result.one_or_none()
        invited_by = None
        if inviter_row is not None:
            referral, inviter = inviter_row
            if referral.referrals_id is not None and inviter.users_id is not None:
                invited_by = _to_referral_row(referral=referral, user=inviter)

        invitees_result = await self._session.execute(
            select(Referral, User)
            .join(User, col(User.users_id) == col(Referral.invited_users_id))
            .where(col(Referral.inviter_users_id) == users_id)
            .order_by(col(Referral.created_at).desc()),
        )
        invited_users = tuple(
            _to_referral_row(referral=referral, user=invited)
            for referral, invited in invitees_result.all()
            if referral.referrals_id is not None and invited.users_id is not None
        )

        return UserReferralsAdminDTO(invited_by=invited_by, invited_users=invited_users)

    async def _search_by_redemption_code(
        self,
        *,
        code: str,
        limit: int,
    ) -> tuple[UserSearchHitDTO, ...]:
        result = await self._session.execute(
            select(User)
            .join(PrizeRedemption, col(PrizeRedemption.users_id) == col(User.users_id))
            .where(col(PrizeRedemption.redemption_code) == code)
            .limit(limit),
        )
        return tuple(_to_search_hit(user=user) for user in result.scalars().all())

    async def _search_by_numeric_id(
        self,
        *,
        value: int,
        limit: int,
    ) -> tuple[UserSearchHitDTO, ...]:
        result = await self._session.execute(
            select(User)
            .where(or_(col(User.vk_user_id) == value, col(User.users_id) == value))
            .limit(limit),
        )
        users = result.scalars().all()
        return tuple(_to_search_hit(user=user) for user in users)

    async def _search_by_name(self, *, normalized: str, limit: int) -> tuple[UserSearchHitDTO, ...]:
        pattern = f"%{normalized}%"
        result = await self._session.execute(
            select(User)
            .where(
                or_(
                    col(User.first_name).ilike(pattern),
                    col(User.last_name).ilike(pattern),
                    col(User.vk_screen_name).ilike(pattern),
                ),
            )
            .order_by(col(User.users_id))
            .limit(limit),
        )
        return tuple(_to_search_hit(user=user) for user in result.scalars().all())


def _looks_like_redemption_code(value: str) -> bool:
    compact = value.replace(" ", "").upper()
    return compact.startswith("VLT") or bool(_REDEMPTION_CODE_PATTERN.match(compact))


def _build_display_name(*, user: User) -> str:
    parts = [part for part in (user.first_name, user.last_name) if part]
    if parts:
        return " ".join(parts)
    if user.vk_screen_name:
        return user.vk_screen_name
    return f"VK {user.vk_user_id}"


def _to_search_hit(*, user: User) -> UserSearchHitDTO:
    if user.users_id is None:
        raise RuntimeError("Первичный ключ пользователя не был сгенерирован")

    return UserSearchHitDTO(
        users_id=user.users_id,
        vk_user_id=user.vk_user_id,
        display_name=_build_display_name(user=user),
        vk_screen_name=user.vk_screen_name,
        balance_points=user.balance_points,
        current_level=user.current_level,
    )


def _to_referral_row(*, referral: Referral, user: User) -> UserReferralRowDTO:
    if referral.referrals_id is None or user.users_id is None:
        raise RuntimeError("Некорректные данные реферальной связи")

    return UserReferralRowDTO(
        referrals_id=referral.referrals_id,
        users_id=user.users_id,
        vk_user_id=user.vk_user_id,
        display_name=_build_display_name(user=user),
        vk_screen_name=user.vk_screen_name,
        bonus_transactions_id=referral.bonus_transactions_id,
        created_at=referral.created_at,
    )


__all__ = ["UserAdminRepository"]
