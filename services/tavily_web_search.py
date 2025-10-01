from tavily import AsyncTavilyClient
import os
from dotenv import load_dotenv
from services.logger_service import get_logger
load_dotenv()

tavily = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
logger = get_logger("tavily_web_search")
allowed_domains = [
    "support.microsoft.com",
    "learn.microsoft.com",
    "excel-easy.com",
    "w3schools.com",
    "gcfglobal.org",
    "trumpexcel.com",
    "excel-practice-online.com",
    "excelexercises.com",
    "simplilearn.com",
    "corporatefinanceinstitute.com",
    "datacamp.com"
]

async def search_and_extract(query, top_k=3):
    """
    Performs a web search and extracts relevant content from top results using Tavily.
    Restricts search to allowed_domains if provided.
    """
    logger.info(f"Searching web for query: {query}")
    if len(query) > 400:
        query = query[:400]  
        logger.info("Query truncated to 400 characters.")
    search_kwargs = {"query": query, "max_results": top_k}
    if allowed_domains:
        search_kwargs["include_domains"] = allowed_domains

    try:
        results = await tavily.search(**search_kwargs, search_depth='basic')
        logger.info(f"Search completed. {len(results['results'])} results found.")
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return ""

    extracted_texts = []
    result_urls = [result.get("url") for result in results["results"]]
    
    try:
        texts = await tavily.extract(
            urls=result_urls,
            include_favicon=False,
            include_images=False,
            extract_depth='basic',
            timeout=30
        )
        
        if isinstance(texts, list):  # multiple URLs
            for t in texts:
                extracted_texts.append(t.get("content", "")[:2000])
        else:  # single URL
            extracted_texts.append(texts.get("content", "")[:2000])
        
        logger.info(f"Extracted content from {len(result_urls)} URLs")
    except Exception as e:
        logger.error(f"Failed to extract {result_urls}: {e}")

    # Concatenate top-k results into a single context string
    context = "\n\n".join(extracted_texts)
    return context