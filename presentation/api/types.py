from typing import Annotated, Any
from pydantic import BeforeValidator
import uuid

def validate_uuid7(v: Any) -> str:
    try:
        val_str = str(v)
        parsed = uuid.UUID(val_str)
    except (ValueError, AttributeError, TypeError):
        raise ValueError("Formato de UUID inválido")

    if parsed.version != 7:
        raise ValueError("O UUID deve ser da versão 7")

    return val_str

UUID7Str = Annotated[str, BeforeValidator(validate_uuid7)]

