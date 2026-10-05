"""A slot for an external verification service ("Jev") in the comparison harness.

The spec planned a third-party verifier; no free API exists to call, and guessing its API
would be fiction. It implements the same interface and fails loudly, so the comparison
path stays wired and tested. This is the one deliberate unimplemented provider.
"""

from provenance.llm.errors import ProviderRejected


class ProviderNotConfigured(ProviderRejected):
    def __init__(self, name: str) -> None:
        super().__init__(name, 501, f"{name} is not configured: no free API exists to call")


class JevProvider:
    name = "jev"

    def confidence(self, claim: str, evidence: list[str]) -> float:
        raise ProviderNotConfigured(self.name)
