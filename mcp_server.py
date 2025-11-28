from mcp.server.fastmcp import FastMCP
from pydantic import Field
from duckduckgo_search import DDGS
from textblob import TextBlob
import json

# Initialize FastMCP server
mcp = FastMCP("CrowdSimAI_Tools")

@mcp.tool()
def web_search(query: str, limit: int = 3) -> str:
    """
    Performs a web search using DuckDuckGo.
    Use this tool when you need to find real-time information, news, or product details.
    
    Args:
        query: The search query string.
        limit: The number of results to return (default: 3).
    """
    print(f"Executing Web Search: {query}")
    try:
        results = DDGS().text(query, max_results=limit)
        if not results:
            return "No results found."
        
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}")
        
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@mcp.tool()
def get_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text using TextBlob.
    Returns a score (-1.0 to 1.0) and a label.
    
    Args:
        text: The text to analyze.
    """
    print(f"Analyzing Sentiment for text length: {len(text)}")
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            label = "Positive"
        elif polarity < -0.1:
            label = "Negative"
        else:
            label = "Neutral"
            
        return json.dumps({
            "score": polarity,
            "label": label,
            "subjectivity": blob.sentiment.subjectivity
        })
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

@mcp.tool()
def save_report(content: str, filename: str) -> str:
    """
    Saves the analysis report to a local file.
    
    Args:
        content: The content to save.
        filename: The filename to save to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Report successfully saved to {filename}"
    except Exception as e:
        return f"Error saving report: {str(e)}"

if __name__ == "__main__":
    mcp.run()
