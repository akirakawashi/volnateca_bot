from dataclasses import dataclass

from application.base_interactor import Interactor
from application.command.process_referral import ProcessReferralCommand, ProcessReferralHandler
from application.command.register_vk_user_and_check_subscription import (
    RegisterVKUserAndCheckSubscriptionCommand,
    RegisterVKUserAndCheckSubscriptionDTO,
    RegisterVKUserAndCheckSubscriptionHandler,
)
from application.common.dto.referral import ProcessReferralDTO
from application.common.helpers import parse_vk_user_id
from application.interface.repositories.referral_intents import IReferralIntentRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserWithReferralContextCommand:
    event_id: str | None
    vk_user_id: int
    first_name: str | None = None
    last_name: str | None = None
    raw_ref: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterVKUserWithReferralContextDTO:
    registration_result: RegisterVKUserAndCheckSubscriptionDTO
    referral_result: ProcessReferralDTO | None


class RegisterVKUserWithReferralContextHandler(
    Interactor[
        RegisterVKUserWithReferralContextCommand,
        RegisterVKUserWithReferralContextDTO,
    ],
):
    """Регистрирует VK пользователя и обрабатывает сохраненный ref-контекст."""

    def __init__(
        self,
        register_vk_user_interactor: RegisterVKUserAndCheckSubscriptionHandler,
        process_referral_interactor: ProcessReferralHandler,
        referral_intent_repository: IReferralIntentRepository,
    ) -> None:
        self._register_vk_user_interactor = register_vk_user_interactor
        self._process_referral_interactor = process_referral_interactor
        self._referral_intent_repository = referral_intent_repository

    async def __call__(
        self,
        command_data: RegisterVKUserWithReferralContextCommand,
    ) -> RegisterVKUserWithReferralContextDTO:
        registration_result = await self._register_vk_user_interactor(
            command_data=RegisterVKUserAndCheckSubscriptionCommand(
                event_id=command_data.event_id,
                vk_user_id=command_data.vk_user_id,
                first_name=command_data.first_name,
                last_name=command_data.last_name,
            ),
        )

        referral_result = None
        raw_ref = await self._resolve_raw_ref(
            vk_user_id=command_data.vk_user_id,
            raw_ref=command_data.raw_ref,
        )
        if registration_result.registration.created:
            inviter_vk_user_id = parse_vk_user_id(raw_ref)
            if inviter_vk_user_id is not None:
                referral_result = await self._process_referral_interactor(
                    command_data=ProcessReferralCommand(
                        invited_vk_user_id=command_data.vk_user_id,
                        inviter_vk_user_id=inviter_vk_user_id,
                    ),
                )

        return RegisterVKUserWithReferralContextDTO(
            registration_result=registration_result,
            referral_result=referral_result,
        )

    async def _resolve_raw_ref(
        self,
        *,
        vk_user_id: int,
        raw_ref: str | None,
    ) -> str | None:
        clean_ref = raw_ref.strip() if raw_ref is not None else ""
        if clean_ref and parse_vk_user_id(clean_ref) is not None:
            return clean_ref
        return await self._referral_intent_repository.get_raw_ref(invited_vk_user_id=vk_user_id)
