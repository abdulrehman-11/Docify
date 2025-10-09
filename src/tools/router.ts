import {
  ToolName,
  ToolInputByName,
  ToolOutputByName,
  validateInput,
  validateOutput,
} from "./schemas";

export type ToolHandler<N extends ToolName> = (
  input: ToolInputByName[N]
) => Promise<ToolOutputByName[N]>;

export class ToolRouter {
  private handlers: Partial<{
    [K in ToolName]: ToolHandler<K>;
  }> = {};

  register<N extends ToolName>(name: N, handler: ToolHandler<N>): void {
    this.handlers[name] = handler as any;
  }

  async dispatch<N extends ToolName>(
    name: N,
    rawInput: unknown
  ): Promise<ToolOutputByName[N]> {
    const toolName = name;
    const input = validateInput(toolName, rawInput) as ToolInputByName[N];

    const handler = this.handlers[toolName];
    if (!handler) {
      throw new Error(`No handler registered for tool: ${toolName}`);
    }

    const result = await (handler as ToolHandler<N>)(input);
    return validateOutput(toolName, result) as ToolOutputByName[N];
  }
}

// Convenience: create a router with typed registration helpers
export function createToolRouter() {
  const router = new ToolRouter();
  return router;
}


