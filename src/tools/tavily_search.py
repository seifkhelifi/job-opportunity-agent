import getpass
import os

from dotenv import load_dotenv


from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()


def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


_set_if_undefined("TAVILY_API_KEY")


tavily_tool = TavilySearchResults(max_results=5)
