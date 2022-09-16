from manipulator import Manipulator


# Karabiner-Elements rule structure
class Rule:
    def __init__(self, description: str, manipulators: list[Manipulator]):
        self.manipulators = manipulators
        self.description = description

    # Convert rule to json
    def serialize(self):
        return {
            "description": self.description,
            "manipulators": [manipulator.serialize() for manipulator in self.manipulators]
        }

    # Require keyboard type for all manipulators in the rule
    def global_require_keyboard(self, keyboard_types: list[str]):
        for manipulator in self.manipulators:
            manipulator.require_keyboard_types(keyboard_types)
        return self


# Creates a karabiner elements ruleset
def create_ruleset(title: str, rules: list[Rule]):
    ruleset = {"title": title, "rules": []}

    for rule in rules:
        if isinstance(rule, Rule):
            ruleset["rules"].append(rule.serialize())
        elif isinstance(rule, dict):
            ruleset["rules"].append(rule)

    return ruleset
