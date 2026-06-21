import re
from pathlib import Path

RULES_FILE = Path("business_rules/local_rules.txt")


class BusinessRule:
    def __init__(self, column, operator, value, action, message):
        self.column = column
        self.operator = operator
        self.value = value
        self.action = action
        self.message = message


def load_local_rules():
    if RULES_FILE.exists():
        return RULES_FILE.read_text(encoding="utf-8")
    return ""


def save_local_rules(text):
    RULES_FILE.write_text(text, encoding="utf-8")


def clear_local_rules():
    RULES_FILE.write_text("", encoding="utf-8")


def parse_custom_rules(text):
    if not text:
        return []

    rules = []

    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("IF "):
            continue

        try:
            condition, action_part = line[3:].split(" THEN ")
            action, message = action_part.split(" ", 1)
            message = message.strip().strip('"')

            # Parse condition
            if " NOT IN " in condition:
                col, rest = condition.split(" NOT IN ")
                operator = "NOT IN"
                value = eval(rest)
            elif " IN " in condition:
                col, rest = condition.split(" IN ")
                operator = "IN"
                value = eval(rest)
            elif "==" in condition:
                col, value = condition.split("==")
                operator = "=="
            elif "!=" in condition:
                col, value = condition.split("!=")
                operator = "!="
            elif "<" in condition:
                col, value = condition.split("<")
                operator = "<"
            elif ">" in condition:
                col, value = condition.split(">")
                operator = ">"
            elif "IS EMPTY" in condition:
                col = condition.replace("IS EMPTY", "").strip()
                operator = "IS EMPTY"
                value = None
            elif "IS NOT EMPTY" in condition:
                col = condition.replace("IS NOT EMPTY", "").strip()
                operator = "IS NOT EMPTY"
                value = None
            else:
                continue

            rules.append(
                BusinessRule(
                    col.strip(),
                    operator,
                    value.strip() if isinstance(value, str) else value,
                    action,
                    message
                )
            )

        except Exception:
            continue

    return rules
