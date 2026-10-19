"""Ortam yapılandırması. .env okunur; eksik değerler DRY_RUN'a düşürür."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo kökü
DATA = ROOT / "data"
OUT = DATA / "out"
PROMPTS = ROOT / "pipeline" / "prompts"


def _load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


@dataclass
class Settings:
    supabase_url: str = ""
    supabase_key: str = ""
    llm_provider: str = "none"
    llm_model: str = ""
    anthropic_key: str = ""
    openai_key: str = ""
    dry_run: bool = True
    user_agent: str = "DisGundemBot/0.1 (+https://github.com/mcmahonnnjohn-arch/dis-gundem; baslik/metadata toplama)"
    http_timeout: float = 15.0
    concurrency: int = 8
    extra: dict = field(default_factory=dict)

    @property
    def has_db(self) -> bool:
        return bool(self.supabase_url and self.supabase_key) and not self.dry_run


def load() -> Settings:
    _load_dotenv()
    env = os.environ.get
    s = Settings(
        supabase_url=env("SUPABASE_URL", ""),
        supabase_key=env("SUPABASE_SERVICE_KEY", ""),
        llm_provider=env("LLM_PROVIDER", "none").lower(),
        llm_model=env("LLM_MODEL", ""),
        anthropic_key=env("ANTHROPIC_API_KEY", ""),
        openai_key=env("OPENAI_API_KEY", ""),
        dry_run=env("DRY_RUN", "1") not in ("0", "false", "False"),
    )
    if not (s.supabase_url and s.supabase_key):
        s.dry_run = True
    OUT.mkdir(parents=True, exist_ok=True)
    return s
