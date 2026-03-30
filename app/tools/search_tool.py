from langchain_community.tools import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(output_format="list")


async def search(query: str):
    return await search_tool.ainvoke(query)