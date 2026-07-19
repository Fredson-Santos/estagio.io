import json
import os
from pathlib import Path
from typing import Dict, Optional

RULES_FILE = Path(__file__).parent.parent.parent.parent / "data" / "scraper_rules.json"

def _ensure_rules_file():
    if not RULES_FILE.parent.exists():
        RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not RULES_FILE.exists():
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_rules(domain: str) -> Optional[Dict[str, str]]:
    """Carrega os seletores CSS conhecidos para um domínio específico."""
    _ensure_rules_file()
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)
            return rules.get(domain)
    except Exception:
        return None

def save_rules(domain: str, selectors: Dict[str, str]):
    """Salva os novos seletores CSS gerados pelo LLM."""
    _ensure_rules_file()
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)
            
        rules[domain] = selectors
        
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar regras para {domain}: {e}")
