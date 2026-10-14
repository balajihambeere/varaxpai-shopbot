# Evidence: LangChain import-path check (ADR-005)

Date: 2026-10-14
Command:
```
python -c "from langchain.schema import SystemMessage, HumanMessage"
python -c "from langchain.prompts import ChatPromptTemplate"
python -c "from langchain_core.messages import SystemMessage, HumanMessage"
python -c "from langchain_core.prompts import ChatPromptTemplate"
```
Environment: Python 3.12.13, langchain 1.4.5, langchain-openai (latest resolved), langchain-ollama (latest resolved), venv at `shopbot/venv`.

Output:
```
FAIL langchain.schema: No module named 'langchain.schema'
OK: langchain_core.messages
FAIL langchain.prompts: No module named 'langchain.prompts'
OK: langchain_core.prompts
OK: RunnablePassthrough
OK: StrOutputParser
OK: langchain_openai
OK: langchain_ollama
```
Conclusion: book's exact import paths (Ch7) are stale against the installed langchain version; `langchain_core.messages` / `langchain_core.prompts` are the correct replacements. See ADR-005.
