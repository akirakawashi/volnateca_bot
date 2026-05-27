from dataclasses import dataclass

from application.base_interactor import Interactor
from application.interface.repositories.referral_intents import IReferralIntentRepository
from application.interface.uow import IUnitOfWork


@dataclass(slots=True, frozen=True, kw_only=True)
class CaptureVKReferralIntentCommand:
    invited_vk_user_id: int
    raw_ref: str


class CaptureVKReferralIntentHandler(Interactor[CaptureVKReferralIntentCommand, None]):
    """Сохраняет первый ref пользователя до его согласия на регистрацию."""

    def __init__(
        self,
        referral_intent_repository: IReferralIntentRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._referral_intent_repository = referral_intent_repository
        self._uow = uow

    async def __call__(self, command_data: CaptureVKReferralIntentCommand) -> None:
        if _parse_vk_user_id(command_data.raw_ref) is None:
            return

        await self._referral_intent_repository.create_if_absent(
            invited_vk_user_id=command_data.invited_vk_user_id,
            raw_ref=command_data.raw_ref,
        )
        await self._uow.commit()


def _parse_vk_user_id(raw_ref: str) -> int | None:
    try:
        return int(raw_ref)
    except (TypeError, ValueError):
        return None
