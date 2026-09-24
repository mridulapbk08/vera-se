from typing import Optional

from vera.models import (
    VerificationResult,
)


class PatchSelector:
    def select(
        self,
        results,
    ) -> Optional[VerificationResult]:

        accepted = [
            result
            for result in results
            if result.accepted
        ]

        if not accepted:
            return None

        return max(
            accepted,
            key=lambda result:
                result.final_score,
        )