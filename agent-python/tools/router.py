from typing import Callable, Dict, TypeVar, Generic, Any
from pydantic import BaseModel, ValidationError

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)


class ToolRouter:
  def __init__(self) -> None:
    self._handlers: Dict[str, Callable[[BaseModel], BaseModel]] = {}
    self._inputs: Dict[str, type[BaseModel]] = {}
    self._outputs: Dict[str, type[BaseModel]] = {}

  def register(self, name: str, input_model: type[I], output_model: type[O], handler: Callable[[I], O]) -> None:
    self._handlers[name] = handler  # type: ignore[assignment]
    self._inputs[name] = input_model
    self._outputs[name] = output_model

  def dispatch(self, name: str, payload: dict) -> dict:
    if name not in self._handlers:
      raise RuntimeError(f"No handler for tool: {name}")
    try:
      input_model = self._inputs[name].model_validate(payload)
    except ValidationError as e:
      raise RuntimeError(f"Invalid input for {name}: {e}") from e

    out_model = self._handlers[name](input_model)  # type: ignore[arg-type]
    try:
      output = self._outputs[name].model_validate(out_model.model_dump())
    except ValidationError as e:
      raise RuntimeError(f"Invalid output from {name}: {e}") from e
    return output.model_dump()


