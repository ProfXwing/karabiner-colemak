# The Karabiner-Elements manipulator structure
class Manipulator:
    def __init__(self):
        setattr(self, 'from', {})
        self.to = [{}]
        self.type = 'basic'
        self.conditions = []

    # Adds the from key to the manipulator given a key and modifiers
    def basic_from(self, key_code: str, mandatoryModifiers: list[str] = [], optionalModifiers: list[str] = ["any"]):
        if key_code in text_to_keycode:
            key_code = text_to_keycode[key_code]
        getattr(self, 'from')["key_code"] = key_code
        if mandatoryModifiers or optionalModifiers:
            getattr(self, 'from')["modifiers"] = {}
            if mandatoryModifiers:
                getattr(self, 'from')[
                    "modifiers"]["mandatory"] = mandatoryModifiers
            if optionalModifiers:
                getattr(self, 'from')[
                    "modifiers"]["optional"] = optionalModifiers
        return self

    # Adds the to key to the manipulator given a key and modifiers
    def basic_to(self, key_code: str, modifiers: list[str] = []):
        self.to[0]["key_code"] = key_code
        if modifiers:
            self.to[0]["modifiers"] = modifiers
        return self

    # Turns the manipulator into a json string
    def serialize(self):
        serialized = {"from": getattr(
            self, "from"), "to": self.to, 'type': self.type}
        if self.conditions:
            serialized["conditions"] = self.conditions

        return serialized

    # Adds a variable condition to the manipulator
    def require_variable(self, variable: str, value: int):
        self.conditions.append(
            {"type": "variable_if", "name": variable, "value": value})
        return self

    # Sets the manipulator's to key to set a variable
    def set_variable_to(self, variable: str, value: int):
        self.to[0]["set_variable"] = {
            "name": variable,
            "value": value
        }
        return self

    # Adds a keyboard type condition to the manipulator
    def require_keyboard_types(self, keyboard_types: list[str]):
        self.conditions.append({
            "type": "keyboard_type_if",
            "keyboard_types": keyboard_types
        })
        return self
        

# So I can convert from string to keycodes
text_to_keycode = {
    '[': 'open_bracket',
    ']': 'close_bracket',
    ';': 'semicolon',
    "'": 'quote',
    ",": 'comma',
    ".": 'period',
    "/": 'slash',
    '\\': 'backslash',  # ISO makes me angey
    '`': 'grave_accent_and_tilde',
    '-': 'hyphen',
    '=': 'equal_sign',
}


# Not used in final script, creates manipulators given the original layout and the new layout
# Used ansi/iso combine function instead in layouts.py
def manipulators_from_keys(qwerty_keys: list[str], layout_keys: list[str], allow_duplicates=True) -> list[Manipulator]:
    manipulators = []
    for qwerty_key, layout_key in zip(qwerty_keys, layout_keys):
        if not allow_duplicates and qwerty_key == layout_key:
            continue

        if qwerty_key in text_to_keycode:
            qwerty_key = text_to_keycode[qwerty_key]
        if layout_key in text_to_keycode:
            layout_key = text_to_keycode[layout_key]

        manipulators.append(Manipulator().basic_from(
            qwerty_key).basic_to(layout_key))
    return manipulators

def create_virtual_modifier(key_code: str, variable_name: str):
    return {
        "from": {
            "key_code": key_code,
            "modifiers": {
                "mandatory": [],
                "optional": ["any"]
            }
        },
        "to": [{
            "set_variable": {
                "name": variable_name,
                "value": 1
            }
            }],
            "to_after_key_up": [{
            "set_variable": {
                "name": variable_name,
                "value": 0
            }
            }],
            "to_if_alone": [{
            "key_code": key_code
            }],
        "type": "basic"
    }