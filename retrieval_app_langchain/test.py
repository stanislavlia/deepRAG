from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

print(search.run("Big data libraries for Python"))