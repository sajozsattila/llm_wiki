from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')

WIKI_DIR="./wiki"

async def _run_wiki_search(search_query: str) -> str:
    """Uses Claude Agent SDK to intelligently search the wiki directory."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Bash"],  # Read files, run grep/find
        cwd=WIKI_DIR,  # Scope to wiki directory
        permission_mode="acceptEdits",  # Read-only intent
        system_prompt=(
            "You are a wiki search engine. The current directory contains markdown "
            "wiki pages. Search, read, and synthesize information to answer queries. "
            "Do NOT create or edit files. Return a structured answer with source filenames."
        )
    )

    prompt = f"""Search the wiki for: "{search_query}"

   Steps:
   1. List available wiki pages (ls or find *.md)
   2. Search for relevant content (grep -r or read promising files)
   3. Synthesize a clear answer with citations (filename + excerpt)
   """

    result_parts = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    result_parts.append(block.text)

    return "\n".join(result_parts)

if __name__ == "__main__":
    result = asyncio.run(
        _run_wiki_search("Mi az a viszajátszás?")
    )
    print(result)