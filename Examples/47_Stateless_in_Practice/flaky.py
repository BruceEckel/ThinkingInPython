# flaky.py
from dataclasses import dataclass
from stateless import Effect, Need, need, throws

class Crashed(Exception):
    pass

@dataclass
class Database:
    failures: int
    attempts: int = 0
    def save(self, user: str) -> str:
        self.attempts += 1
        print(f"attempt {self.attempts}: saving {user}")
        if self.attempts <= self.failures:
            raise Crashed("database crashed")
        return f"{user} saved"

@throws(Crashed)
def store(db: Database, user: str) -> str:
    return db.save(user)

def save_user(user: str) -> Effect[
    Need[Database], Crashed, str
]:
    db = yield from need(Database)
    result = yield from store(db, user)
    return result
