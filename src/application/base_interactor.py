from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class Interactor(Generic[InputDTO, OutputDTO]):
    """Базовый контракт application use case.

    Каждый interactor принимает один command/DTO и возвращает один результат.
    Это сохраняет единый стиль вызова в DI, callback-обработчиках и тестах.
    """

    async def __call__(self, command_data: InputDTO) -> OutputDTO:
        raise NotImplementedError
