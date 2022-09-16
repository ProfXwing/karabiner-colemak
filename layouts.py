from manipulator import Manipulator, manipulators_from_keys, text_to_keycode
from rule import Rule
from itertools import zip_longest


# Unused for my end use, but could be useful.
# A Layout specific rule for karabiner
class Layout(Rule):
    ANSI_QWERTY = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
    ISO_QWERTY = "`1234567890-=qwertyuiop[]asdfghjkl;'#\\zxcvbnm,./"

    def __init__(self, description: str, layout: str, keyboard_type: str = 'ansi'):
        self.string_layout = layout
        if keyboard_type == 'ansi':
            manipulators = manipulators_from_keys(
                self.ANSI_QWERTY, layout, allow_duplicates=False)
        else:
            raise Exception('Keyboard type not supported')

        super().__init__(description, manipulators)

    def add_global_variable(self, variable: str, value: int):
        for manipulator in self.manipulators:
            manipulator.require_variable(variable, value)
        return self

    def add_manipulators(self, new_manipulators: list[Manipulator]):
        self.manipulators.extend(new_manipulators)


# "Rotates" a list of keys in the alternate layout
# E.g. passing in ['a', 's', 'd'] will move a -> s -> d -> a
def rotate_from_alternate(alternate_layout: str, *to_rotate: list[str]):
    new_layout = list(alternate_layout)
    for original_order in to_rotate:
        new_order = original_order.copy()
        new_order.insert(0, new_order.pop())

        for original_key, layout_key in zip(original_order, new_order):
            key_position = alternate_layout.index(original_key)
            new_layout[key_position] = layout_key

    return "".join(new_layout)


# Rotates a list of keys from the original layout. Useful for position specific rotations.
# E.g. passing in ['b', 'v', 'c', 'x', 'z'] will move whatever layout key is in the qwerty position of b -> v -> c -> x -> z -> b
# This is used to implement angle and wide mods
def rotate_from_original(alternate_layout: str, original_layout: str, *to_rotate: list[str]):
    # rotate original layout in the opposite direction
    original_rotated = rotate_from_alternate(
        original_layout, *[rotation[::-1] for rotation in to_rotate])

    new_layout = list(alternate_layout)
    for original_order in to_rotate:
        # rotate the keys given
        new_order = original_order.copy()
        new_order.insert(0, new_order.pop())

        # replace keys in layout with rotated keys
        for qwerty_key in original_order:
            # find the position of the qwerty key
            original_position = original_layout.index(qwerty_key)

            # find the new key after layout rotation
            new_position = original_rotated.index(qwerty_key)
            new_key = alternate_layout[new_position]

            # replace the key in the layout
            new_layout[original_position] = new_key

    return "".join(new_layout)


# Separates a layout into rows
def row_separation(alternate_layout: str):
    # Detect ansi/iso
    if len(alternate_layout) == 47:  # ANSI
        row_lengths = [13, 13, 11, 10]
    elif len(alternate_layout) == 48:  # ISO
        row_lengths = [13, 12, 12, 11]
    else:
        raise Exception("Keyboard type not supported")

    separated_layout = [
        [],
        [],
        [],
        []
    ]
    row_num = 0
    for count, key in enumerate(alternate_layout):
        if count >= sum(row_lengths[:row_num + 1]):
            row_num += 1
        separated_layout[row_num].append(key)

    return separated_layout


# Combines ansi and iso strings into a single set of karabiner manipulators.
def combine_ansi_iso(ansi_layout: str, iso_layout: str):
    common_keys = []
    ansi_keys = []
    iso_keys = []

    # Pad ansi and iso to make them the same length
    ansi_rows = row_separation(ansi_layout)
    ansi_rows[2].append(None)
    ansi_rows[3].insert(0, None)
    iso_rows = row_separation(iso_layout)
    iso_rows[1].append(None)

    # Sort the keys into common, ansi, and iso
    # This is necessary to reduce file size and reuse manipulators that are common between the two layouts
    for ansi_row, iso_row in zip_longest(ansi_rows, iso_rows):
        for ansi_key, iso_key in zip_longest(ansi_row, iso_row):
            if ansi_key == iso_key:
                common_keys.append(ansi_key)
            else:
                if ansi_key:
                    ansi_keys.append(ansi_key)
                if iso_key:
                    iso_keys.append(iso_key)

    # Creates the manipulators
    manipulators: list[Manipulator] = []
    for keyboard_type in ['ansi', 'iso']:
        if keyboard_type == 'ansi':
            original_layout = Layout.ANSI_QWERTY
            new_layout = ansi_layout
        else:
            original_layout = Layout.ISO_QWERTY
            new_layout = iso_layout

        for qwerty_key, layout_key in zip(original_layout, new_layout):
            if qwerty_key == layout_key:
                continue

            in_global = layout_key in common_keys

            if layout_key == '\\' and keyboard_type == 'iso':
                layout_key = 'non_us_backslash'

            if qwerty_key in text_to_keycode:
                qwerty_key = text_to_keycode[qwerty_key]
            if layout_key in text_to_keycode:
                layout_key = text_to_keycode[layout_key]

            if qwerty_key == '\\' and keyboard_type == 'iso':
                qwerty_key = 'non_us_backslash'

            manipulators.append(Manipulator().basic_from(
                qwerty_key).basic_to(layout_key))

            if in_global:
                manipulators[-1].require_keyboard_types(['ansi', 'iso'])
            else:
                manipulators[-1].require_keyboard_types([keyboard_type])

    return manipulators
