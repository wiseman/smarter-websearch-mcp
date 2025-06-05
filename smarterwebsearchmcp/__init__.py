from agents import Agent, ModelSettings


def make_agent(*, name: str, instructions: str, tools=None, output_type=None, model=None, model_settings=None):
    """Convenience wrapper to create an Agents SDK agent."""
    return Agent(
        name=name,
        instructions=instructions,
        tools=tools or [],
        output_type=output_type,
        model=model,
        model_settings=model_settings or ModelSettings(),
    )
