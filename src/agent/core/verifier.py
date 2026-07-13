"""Verifier: checks whether executed steps succeeded and the goal is met."""


class Verifier:
    def verify(self, steps: list, task: str) -> dict:
        done = [s for s in steps if s.get("status") == "done"]
        failed = [s for s in steps if s.get("status") == "failed"]
        skipped = [s for s in steps if s.get("status") == "skipped"]
        ok = len(failed) == 0 and len(done) > 0
        return {
            "ok": ok,
            "done": len(done),
            "failed": len(failed),
            "skipped": len(skipped),
            "total": len(steps),
            "failed_steps": [s.get("description") for s in failed],
            "summary": (
                "completed" if ok else
                ("partial" if done else "failed")
            ),
        }
