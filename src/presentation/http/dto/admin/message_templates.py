from pydantic import BaseModel, Field

from application.common.dto.message_template import MessageTemplateDTO


class MessageTemplateUpsertRequestSchema(BaseModel):
    template_text: str = Field(min_length=1)


class MessageTemplateResponseSchema(BaseModel):
    code: str
    description: str
    variables: list[str]
    default_template: str
    override_template: str | None
    effective_template: str

    @classmethod
    def from_dto(cls, dto: MessageTemplateDTO) -> "MessageTemplateResponseSchema":
        return cls(
            code=dto.code,
            description=dto.description,
            variables=list(dto.variables),
            default_template=dto.default_template,
            override_template=dto.override_template,
            effective_template=dto.effective_template,
        )
