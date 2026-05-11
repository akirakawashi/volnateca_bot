from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from application.interface.repositories.task_completions import ITaskCompletionRepository
from application.interface.repositories.transactions import ITransactionRepository
from application.interface.repositories.users import IUserRepository
from domain.enums.task import TaskCompletionStatus
from domain.enums.transaction import TransactionSource, TransactionType
from domain.services.wallet import WalletService


class AwardTaskOutcomeStatus(str, Enum):
    """Унифицированный статус начисления/отклонения по конкретному заданию.

    Используется AwardTaskService как внутренний контракт между ним и
    interactor-ами. Каждый interactor сам мапит этот статус в публичный
    статус своего типа задания (репост, лайк, подписка и т.д.).
    """

    COMPLETED = "completed"
    ALREADY_COMPLETED = "already_completed"
    REJECTED = "rejected"
    USER_NOT_REGISTERED = "user_not_registered"


@dataclass(slots=True, frozen=True, kw_only=True)
class TaskAwardSpec:
    """Описание начисления для конкретного задания.

    Содержит идентификатор и сумму, чтобы AwardTaskService мог не зависеть
    от конкретного DTO задания (репост/лайк/подписка) и работать унифицированно.
    """

    tasks_id: int
    task_name: str
    points: int


@dataclass(slots=True, frozen=True, kw_only=True)
class AwardTaskOutcome:
    """Результат вызова AwardTaskService.award или .reject."""

    status: AwardTaskOutcomeStatus
    vk_user_id: int
    users_id: int | None = None
    tasks_id: int | None = None
    task_name: str | None = None
    task_completions_id: int | None = None
    transactions_id: int | None = None
    points_awarded: int = 0
    balance_points: int | None = None
    rejected_reason: str | None = None


class AwardTaskService:
    """Единственное место, где происходит «выполнено задание -> +N очков».

    Сервис оркестрирует:
      1. блокировку строки пользователя (SELECT ... FOR UPDATE);
      2. идемпотентность по (users_id, tasks_id, completion_key);
      3. расчёт нового баланса через WalletService;
      4. запись новой транзакции;
      5. вставку или обновление task_completions.

    Эта логика раньше была размазана по infrastructure-репозиторию tasks.py
    и дублировалась трижды (репост, лайк, подписка). Теперь репозитории
    отвечают только за data access, а бизнес-логика начисления — здесь.
    """

    def __init__(
        self,
        users: IUserRepository,
        task_completions: ITaskCompletionRepository,
        transactions: ITransactionRepository,
    ) -> None:
        self._users = users
        self._task_completions = task_completions
        self._transactions = transactions

    async def award(
        self,
        *,
        vk_user_id: int,
        task: TaskAwardSpec,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
    ) -> AwardTaskOutcome:
        snapshot = await self._users.get_balance_snapshot_for_update(vk_user_id=vk_user_id)
        if snapshot is None:
            return AwardTaskOutcome(
                status=AwardTaskOutcomeStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
            )

        completion = await self._task_completions.get_for_update(
            users_id=snapshot.users_id,
            tasks_id=task.tasks_id,
            completion_key=completion_key,
        )
        if (
            completion is not None
            and completion.task_completion_status == TaskCompletionStatus.COMPLETED
        ):
            return AwardTaskOutcome(
                status=AwardTaskOutcomeStatus.ALREADY_COMPLETED,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                task_completions_id=completion.task_completions_id,
                transactions_id=completion.transactions_id,
                points_awarded=0,
                balance_points=snapshot.balance_points,
            )

        accrual = WalletService.accrue(
            balance_before=snapshot.balance_points,
            earned_points_total_before=snapshot.earned_points_total,
            amount=task.points,
        )

        await self._users.apply_balance_change(
            users_id=snapshot.users_id,
            balance_points=accrual.balance_after,
            earned_points_total=accrual.earned_points_total_after,
        )

        transaction = await self._transactions.create(
            users_id=snapshot.users_id,
            tasks_id=task.tasks_id,
            prizes_id=None,
            transaction_type=TransactionType.ACCRUAL,
            transaction_source=TransactionSource.TASK,
            amount=accrual.amount,
            balance_before=accrual.balance_before,
            balance_after=accrual.balance_after,
            description=f"Начисление за задание: {task.task_name}",
        )

        now = datetime.now(tz=UTC)
        if completion is None:
            completion = await self._task_completions.create(
                users_id=snapshot.users_id,
                tasks_id=task.tasks_id,
                completion_key=completion_key,
                task_completion_status=TaskCompletionStatus.COMPLETED,
                points_awarded=accrual.amount,
                transactions_id=transaction.transactions_id,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                rejected_reason=None,
                checked_at=now,
            )
        else:
            completion = await self._task_completions.update_status(
                task_completions_id=completion.task_completions_id,
                task_completion_status=TaskCompletionStatus.COMPLETED,
                points_awarded=accrual.amount,
                transactions_id=transaction.transactions_id,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                rejected_reason=None,
                checked_at=now,
            )

        return AwardTaskOutcome(
            status=AwardTaskOutcomeStatus.COMPLETED,
            vk_user_id=vk_user_id,
            users_id=snapshot.users_id,
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            task_completions_id=completion.task_completions_id,
            transactions_id=transaction.transactions_id,
            points_awarded=accrual.amount,
            balance_points=accrual.balance_after,
        )

    async def reject(
        self,
        *,
        vk_user_id: int,
        task: TaskAwardSpec,
        completion_key: str,
        event_id: str | None,
        evidence_external_id: str | None,
        rejected_reason: str,
    ) -> AwardTaskOutcome:
        snapshot = await self._users.get_balance_snapshot_for_update(vk_user_id=vk_user_id)
        if snapshot is None:
            return AwardTaskOutcome(
                status=AwardTaskOutcomeStatus.USER_NOT_REGISTERED,
                vk_user_id=vk_user_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                rejected_reason=rejected_reason,
            )

        completion = await self._task_completions.get_for_update(
            users_id=snapshot.users_id,
            tasks_id=task.tasks_id,
            completion_key=completion_key,
        )
        if (
            completion is not None
            and completion.task_completion_status == TaskCompletionStatus.COMPLETED
        ):
            return AwardTaskOutcome(
                status=AwardTaskOutcomeStatus.ALREADY_COMPLETED,
                vk_user_id=vk_user_id,
                users_id=snapshot.users_id,
                tasks_id=task.tasks_id,
                task_name=task.task_name,
                task_completions_id=completion.task_completions_id,
                transactions_id=completion.transactions_id,
                points_awarded=0,
                balance_points=snapshot.balance_points,
            )

        now = datetime.now(tz=UTC)
        if completion is None:
            completion = await self._task_completions.create(
                users_id=snapshot.users_id,
                tasks_id=task.tasks_id,
                completion_key=completion_key,
                task_completion_status=TaskCompletionStatus.REJECTED,
                points_awarded=0,
                transactions_id=None,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                rejected_reason=rejected_reason,
                checked_at=now,
            )
        else:
            completion = await self._task_completions.update_status(
                task_completions_id=completion.task_completions_id,
                task_completion_status=TaskCompletionStatus.REJECTED,
                points_awarded=0,
                transactions_id=None,
                external_event_id=event_id,
                evidence_external_id=evidence_external_id,
                rejected_reason=rejected_reason,
                checked_at=now,
            )

        return AwardTaskOutcome(
            status=AwardTaskOutcomeStatus.REJECTED,
            vk_user_id=vk_user_id,
            users_id=snapshot.users_id,
            tasks_id=task.tasks_id,
            task_name=task.task_name,
            task_completions_id=completion.task_completions_id,
            transactions_id=None,
            points_awarded=0,
            balance_points=snapshot.balance_points,
            rejected_reason=rejected_reason,
        )
