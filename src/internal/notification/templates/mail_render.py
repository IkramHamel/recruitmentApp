
from pydantic import BaseModel


class MailContextSchema(BaseModel):
    name: str
    day: str


class MailRenderEngine:
    def __init__(self, template_text):
        """
        Initialize the engine with a simple template.

        :param template_text: The template string containing placeholders in the format {{ variable }}.
        """
        if not isinstance(template_text, str):
            raise ValueError("Template text must be a string.")
        self.template_text = template_text

    def render(self, context):
        """
        Render the template with the given context by replacing placeholders with their values.

        :param context: A dictionary of values to replace the placeholders in the template.
        :return: The rendered string with placeholders replaced by context values.
        """
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary.")

        result = self.template_text
        for key, value in context.items():
            if not isinstance(key, str):
                raise ValueError("Context keys must be strings.")

            placeholder = f"{{{{ {key} }}}}"  # Matches {{ variable }}
            result = result.replace(placeholder, str(value))
        return result


