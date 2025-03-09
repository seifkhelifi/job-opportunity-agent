from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import getpass
import os

from dotenv import load_dotenv

load_dotenv()


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("GROQ_API_KEY")

llm = ChatGroq(temperature=0, model_name="qwen-2.5-32b")
# prompt = ChatPromptTemplate.from_messages([("human", "Write a haiku about {topic}")])
# chain = prompt | chat
# for chunk in chain.stream({"topic": "The Moon"}):
#     print(chunk.content, end="", flush=True)

from typing import Optional

from pydantic import BaseModel, Field


# Pydantic
class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )


structured_llm = llm.with_structured_output(Joke)

response = structured_llm.invoke("Tell me a joke about cats")
print(response)

