from few_shot_engine.src.general_models.oai import get_chat_completion, count_tokens
class ModelFactory:
    def __init__(self, model="openAI", args="GPT3.5"):
        if model == "openAI":
            if args == "GPT3.5":
                self.get_chat_completion = get_chat_completion
                self.count_tokens = count_tokens
            else:
                raise ValueError("The only valid argument for OpenAI is GPT3.5")
        else:
            raise ValueError("The only valid model is OpenAI")