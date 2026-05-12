"""
Handler для запуска dev-сценариев засеивания БД.
Логика переиспользуется из dev_scripts.seed_dev_scenarios.

TODO: удалить перед релизом — только для локальной отладки.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from application.base_interactor import Interactor
from settings.vk import VKSettings

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dev_scripts.seed_dev_scenarios import get_target_user, seed_target_scenario


@dataclass(slots=True, frozen=True, kw_only=True)
class SeedDevScenarioCommand:
    scenario: str
    users_id: int = 1


@dataclass(slots=True, frozen=True, kw_only=True)
class SeedDevScenarioDTO:
    messages: tuple[str, ...]


class SeedDevScenarioHandler(Interactor[SeedDevScenarioCommand, SeedDevScenarioDTO]):
    """Запускает dev-сценарий засеивания БД для указанного пользователя."""

    def __init__(self, session: AsyncSession, vk_settings: VKSettings) -> None:
        self._session = session
        self._vk_settings = vk_settings

    async def __call__(self, command_data: SeedDevScenarioCommand) -> SeedDevScenarioDTO:
        user = await get_target_user(self._session, users_id=command_data.users_id)
        lines = await seed_target_scenario(
            self._session,
            user=user,
            scenario=command_data.scenario,
            group_id=self._vk_settings.GROUP_ID,
            post_external_id="wall-238388485_912001",
        )
        return SeedDevScenarioDTO(messages=tuple(lines))
