from agno.models.litellm import LiteLLM

def switch_model(id=None, provider=None, api_key=None, **kwargs):
    if provider and id and not id.startswith(provider + "/"):
        id = f"{provider}/{id}"
    else:
        id = id
    return LiteLLM(
        id=id,
        provider=provider,
        api_key=api_key,
        **kwargs
    )