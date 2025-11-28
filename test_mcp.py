import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Connected to MCP server. Found {len(tools.tools)} tools.")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Test get_sentiment
            print("\nTesting get_sentiment...")
            result = await session.call_tool("get_sentiment", arguments={"query": "smart toaster price"})
            print(f"Result: {result.content[0].text}")

            # Test save_report
            print("\nTesting save_report...")
            report_content = "# Test Report\nThis is a test."
            result = await session.call_tool("save_report", arguments={"content": report_content, "filename": "test_report.md"})
            print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run())
