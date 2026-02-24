"""
AI Engine for CashScript Copilot
Handles LLM integration with CashScript-specific knowledge.
Supports Anthropic Claude and OpenAI APIs.
"""

import os
import json
import re
from pathlib import Path

from cashscript_knowledge import CASHSCRIPT_SYSTEM_PROMPT, EXAMPLE_CONTRACTS, AUDIT_CHECKLIST

# ─── Provider abstraction ─────────────────────────────────────────────────────

class AIEngine:
    """AI engine that routes to Anthropic or OpenAI based on config."""

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "anthropic").lower()
        self.model = os.getenv("AI_MODEL", "")
        self.client = None

        if self.provider == "anthropic":
            self.model = self.model or "claude-sonnet-4-20250514"
            self._init_anthropic()
        elif self.provider == "openai":
            self.model = self.model or "gpt-4o"
            self._init_openai()
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {self.provider}. Use 'anthropic' or 'openai'.")

    def _init_anthropic(self):
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("pip install anthropic")

    def _init_openai(self):
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("pip install openai")

    def _call_llm(self, system: str, user_message: str, max_tokens: int = 4096) -> str:
        """Call the configured LLM provider."""
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content

    # ─── Public API ───────────────────────────────────────────────────────────

    def generate(self, description: str) -> dict:
        """Generate a CashScript contract from natural language description."""
        examples_text = "\n\n".join(
            f"### {e['name']}\n{e['description']}\n```cashscript\n{e['code']}\n```"
            for e in EXAMPLE_CONTRACTS.values()
        )

        prompt = f"""Generate a complete CashScript smart contract based on this description:

{description}

## Reference Examples
{examples_text}

## Requirements
- Write complete, compilable CashScript code with `pragma cashscript ^0.10.0;`
- Include inline comments explaining each section
- Follow all security best practices (validate outputs, check signatures, prevent value drain)
- Use CashTokens if the use case involves tokens/NFTs
- Include all necessary constructor parameters and function arguments

Respond with:
1. A brief explanation of the contract design (2-3 sentences)
2. The complete CashScript code in a ```cashscript code block
3. Usage notes (how to deploy and use the contract)
4. Security considerations specific to this contract"""

        result = self._call_llm(CASHSCRIPT_SYSTEM_PROMPT, prompt)
        code = self._extract_code(result)

        return {
            "response": result,
            "code": code,
            "mode": "generate",
        }

    def audit(self, code: str) -> dict:
        """Audit a CashScript contract for security issues."""
        prompt = f"""Perform a comprehensive security audit on this CashScript contract:

```cashscript
{code}
```

{AUDIT_CHECKLIST}

## Audit Requirements
For each finding, provide:
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW / INFO
- **Title**: Brief description
- **Location**: Which function/line
- **Description**: What the issue is
- **Recommendation**: How to fix it
- **Fixed code** (if applicable)

Also provide:
- Overall security rating (A/B/C/D/F)
- Summary of findings
- Improved version of the contract with all fixes applied (in a ```cashscript code block)"""

        result = self._call_llm(CASHSCRIPT_SYSTEM_PROMPT, prompt)
        code_fixed = self._extract_code(result)

        return {
            "response": result,
            "code": code_fixed,
            "mode": "audit",
        }

    def explain(self, code: str) -> dict:
        """Explain a CashScript contract in plain language."""
        prompt = f"""Explain this CashScript contract in plain, accessible language:

```cashscript
{code}
```

Structure your explanation as:

1. **Overview**: What does this contract do? (1-2 sentences, non-technical)
2. **Constructor Parameters**: What configuration does it need?
3. **Functions**: For each function:
   - What it does
   - Who can call it
   - What conditions must be met
   - What happens when it executes
4. **Token Handling**: If CashTokens are involved, explain the token flow
5. **Security Model**: What protections are in place?
6. **Use Cases**: Real-world scenarios where this contract would be useful
7. **Flow Diagram**: ASCII diagram showing the transaction flow"""

        result = self._call_llm(CASHSCRIPT_SYSTEM_PROMPT, prompt)

        return {
            "response": result,
            "code": "",
            "mode": "explain",
        }

    def optimize(self, code: str) -> dict:
        """Suggest optimizations for a CashScript contract."""
        prompt = f"""Analyze and optimize this CashScript contract:

```cashscript
{code}
```

Provide:

1. **Current Issues**: List any inefficiencies, redundancies, or missing optimizations
2. **Security Improvements**: Additional checks or guards that should be added
3. **Code Quality**: Naming, structure, readability improvements
4. **Optimized Version**: Complete rewritten contract with all improvements applied

For each change, explain:
- What was changed
- Why it's better
- Impact (security / efficiency / readability)

Return the optimized contract in a ```cashscript code block."""

        result = self._call_llm(CASHSCRIPT_SYSTEM_PROMPT, prompt)
        code_optimized = self._extract_code(result)

        return {
            "response": result,
            "code": code_optimized,
            "mode": "optimize",
        }

    def chat(self, message: str, history: list[dict] | None = None) -> dict:
        """Free-form chat about CashScript development."""
        context = ""
        if history:
            context = "\n\n## Conversation History\n"
            for msg in history[-6:]:  # Last 6 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"\n**{role}**: {content}\n"

        prompt = f"""{context}

## User Message
{message}

Respond helpfully about CashScript and Bitcoin Cash development. If the user asks for code, provide complete, compilable CashScript. If they ask about concepts, explain clearly with examples."""

        result = self._call_llm(CASHSCRIPT_SYSTEM_PROMPT, prompt)
        code = self._extract_code(result)

        return {
            "response": result,
            "code": code,
            "mode": "chat",
        }

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extract the last CashScript code block from LLM response."""
        # Try cashscript-specific blocks first
        blocks = re.findall(r'```cashscript\n(.*?)```', text, re.DOTALL)
        if blocks:
            return blocks[-1].strip()
        # Fall back to generic code blocks
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
        if blocks:
            # Find the longest block (likely the main contract)
            return max(blocks, key=len).strip()
        return ""

    def get_examples(self) -> dict:
        """Return available example contracts."""
        return {
            name: {"name": ex["name"], "description": ex["description"]}
            for name, ex in EXAMPLE_CONTRACTS.items()
        }

    def get_example_code(self, name: str) -> str | None:
        """Return code for a specific example."""
        ex = EXAMPLE_CONTRACTS.get(name)
        return ex["code"] if ex else None
