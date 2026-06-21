from business_rules.helpers import is_empty


def apply_rules(row, rules):
    errors = []

    for rule in rules:
        cell = row.get(rule.column)

        match = False

        if rule.operator == "==":
            match = str(cell) == rule.value
        elif rule.operator == "!=":
            match = str(cell) != rule.value
        elif rule.operator == "<":
            match = float(cell) < float(rule.value)
        elif rule.operator == ">":
            match = float(cell) > float(rule.value)
        elif rule.operator == "IN":
            match = str(cell) in rule.value
        elif rule.operator == "NOT IN":
            match = str(cell) not in rule.value
        elif rule.operator == "IS EMPTY":
            match = is_empty(cell)
        elif rule.operator == "IS NOT EMPTY":
            match = not is_empty(cell)

        if match:
            if rule.action == "ERROR":
                errors.append(rule.message)
            elif rule.action == "WARNING":
                errors.append("Warning: " + rule.message)

    return errors
