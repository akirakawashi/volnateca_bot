from application.common.dto.task import TaskCompletionResult, TaskCompletionResultStatus
from application.services.award_task_service import AwardTaskOutcome, AwardTaskOutcomeStatus


def build_task_completion_result(outcome: AwardTaskOutcome) -> TaskCompletionResult:
    return TaskCompletionResult(
        status=map_award_task_outcome_status(outcome=outcome.status),
        vk_user_id=outcome.vk_user_id,
        users_id=outcome.users_id,
        tasks_id=outcome.tasks_id,
        task_name=outcome.task_name,
        task_completions_id=outcome.task_completions_id,
        transactions_id=outcome.transactions_id,
        points_awarded=outcome.points_awarded,
        balance_points=outcome.balance_points,
        level_up=outcome.level_up,
        rejected_reason=outcome.rejected_reason,
    )


def map_award_task_outcome_status(
    *,
    outcome: AwardTaskOutcomeStatus,
) -> TaskCompletionResultStatus:
    match outcome:
        case AwardTaskOutcomeStatus.COMPLETED:
            return TaskCompletionResultStatus.COMPLETED
        case AwardTaskOutcomeStatus.ALREADY_COMPLETED:
            return TaskCompletionResultStatus.ALREADY_COMPLETED
        case AwardTaskOutcomeStatus.REJECTED:
            return TaskCompletionResultStatus.REJECTED
        case AwardTaskOutcomeStatus.USER_NOT_REGISTERED:
            return TaskCompletionResultStatus.USER_NOT_REGISTERED
