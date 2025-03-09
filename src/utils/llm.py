import getpass
import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq


load_dotenv()


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(temperature=1, model_name="llama-3.3-70b-specdec")
