"""Provider-agnostic structured LLM completion.

The LLM judge/extractor work with whichever API key is configured:

* ``OPENAI_API_KEY``    -> OpenAI (default model ``gpt-4o``; override with OPENAI_MODEL)
* ``ANTHROPIC_API_KEY`` -> Claude (default ``claude-opus-4-8``; override ANTHROPIC_MODEL)
* neither               -> returns None, and callers use their deterministic fallback.

Both providers support structured outputs against the SAME Pydantic schema, so the
judge/extractor code is written once and runs on either. SDKs are imported lazily,
so the package loads (and tests run) with no provider installed.
"""

from __future__ import annotations

import os


def provider() -> str:
    """Which backend is active, by env. OpenAI wins if both are set."""
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "none"


def structured_complete(system: str, prompt: str, schema_factory, max_tokens: int = 1500):
    """Run the active provider against the Pydantic schema and return a validated
    instance, or None if no provider/SDK is available (caller falls back).

    ``schema_factory`` is a *callable* returning the Pydantic class — built lazily
    here so the no-LLM fallback path never imports pydantic.
    """
    p = provider()
    try:
        if p == "openai":
            from openai import OpenAI

            resp = OpenAI().beta.chat.completions.parse(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": prompt}],
                response_format=schema_factory(),
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.parsed

        if p == "anthropic":
            import anthropic

            resp = anthropic.Anthropic().messages.parse(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8"),
                max_tokens=max_tokens,
                thinking={"type": "adaptive"},
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_format=schema_factory(),
            )
            return resp.parsed_output
    except ImportError:
        return None
    return None
