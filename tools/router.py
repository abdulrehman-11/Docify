import logging
from typing import Callable, Dict, TypeVar, Generic, Any
from pydantic import BaseModel, ValidationError

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)

logger = logging.getLogger(__name__)


class ToolRouter:
  def __init__(self) -> None:
    self._handlers: Dict[str, Callable[[BaseModel], BaseModel]] = {}
    self._inputs: Dict[str, type[BaseModel]] = {}
    self._outputs: Dict[str, type[BaseModel]] = {}

  def register(self, name: str, input_model: type[I], output_model: type[O], handler: Callable[[I], O]) -> None:
    self._handlers[name] = handler  # type: ignore[assignment]
    self._inputs[name] = input_model
    self._outputs[name] = output_model
    logger.info(f"Registered tool: {name}")

  def unregister(self, name: str) -> None:
    """Remove a tool from the registry"""
    if name in self._handlers:
      del self._handlers[name]
      del self._inputs[name]
      del self._outputs[name]
      logger.info(f"Unregistered tool: {name}")
    else:
      logger.warning(f"Attempted to unregister non-existent tool: {name}")

  def update_handler(self, name: str, input_model: type[I], output_model: type[O], handler: Callable[[I], O]) -> None:
    """Update an existing tool's handler"""
    if name in self._handlers:
      self._handlers[name] = handler  # type: ignore[assignment]
      self._inputs[name] = input_model
      self._outputs[name] = output_model
      logger.info(f"Updated tool: {name}")
    else:
      logger.warning(f"Tool {name} not found. Use register() instead.")

  def list_tools(self) -> list[str]:
    """Return list of registered tool names"""
    return list(self._handlers.keys())

  async def dispatch(self, name: str, payload: dict) -> dict:
    logger.info(f"Dispatching tool: {name}")

    if name not in self._handlers:
      logger.error(f"No handler for tool: {name}")
      raise RuntimeError(f"No handler for tool: {name}")

    try:
      input_model = self._inputs[name].model_validate(payload)
    except ValidationError as e:
      logger.error(f"Invalid input for {name}: {e}")
      raise RuntimeError(f"Invalid input for {name}: {e}") from e

    out_model = await self._handlers[name](input_model)  # type: ignore[arg-type]

    try:
      output = self._outputs[name].model_validate(out_model.model_dump())
    except ValidationError as e:
      logger.error(f"Invalid output from {name}: {e}")
      raise RuntimeError(f"Invalid output from {name}: {e}") from e

    logger.info(f"Successfully dispatched tool: {name}")
    return output.model_dump()


