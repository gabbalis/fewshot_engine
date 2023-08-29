from typing import List
import openai
from loguru import logger

from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken

tokenizer = tiktoken.get_encoding(
    "cl100k_base"
)
def count_tokens(string,  model="gpt-3.5-turbo"):
    if model == "gpt-3.5-turbo":
        return len(tokenizer.encode(string))
    else:
        raise ValueError(f"{model} is not a valid model name.")

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion(
    messages,
    model="gpt-3.5-turbo",  # use "gpt-4" for better results
    deployment_id = None
)->str:
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
        messages: The list of messages in the chat history.
        model: The name of the model to use for the completion. Default is gpt-3.5-turbo, which is a fast, cheap and versatile model. Use gpt-4 for higher quality but slower results.

    Returns:
        A string containing the chat completion.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    # Note: Azure Open AI requires deployment id
    response = {}
    if deployment_id == None:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
    else:
        response = openai.ChatCompletion.create(
            deployment_id = deployment_id,
            messages=messages,
        )


    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    logger.info(f"Completion: {completion}")
    return completion
