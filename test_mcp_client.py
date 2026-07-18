import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["tools/mcp_servers/crm_server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            print("\nCalling lookup_client...")
            result = await session.call_tool(
                "lookup_client", {"email": "sarah.jones@acmewidgets.com"}
            )
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())