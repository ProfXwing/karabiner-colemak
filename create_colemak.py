import json
from itertools import product
from manipulator import Manipulator, text_to_keycode
from rule import Rule, create_ruleset
from layouts import Layout, combine_ansi_iso, rotate_from_alternate, rotate_from_original
import copy

base_extend: dict = json.load(open("extend_rule.json", "r"))
wide_extend: dict = json.load(open("wide_extend_rule.json", "r"))

ansi_colemak = "`1234567890-=qwfpgjluy;[]\\arstdhneio'zxcvbkm,./"
iso_colemak = "`1234567890-=qwfpgjluy;[]arstdhneio'#\\zxcvbkm,./"

# Generate all combinations of layouts
for curl, angle, wide, symbol in product((0, 1), repeat=4):
    # ansi and colemak variants for each layout
    layouts = []
    for iso in (0, 1):
        if iso:
            layout = iso_colemak
        else:
            layout = ansi_colemak

        # Base description to be added with each mod
        layout_description = "Colemak "

        # Adds curl mod
        if curl:
            layout_description += "C"
            layout = rotate_from_alternate(
                layout, ["d", "v", "b", "g"], ['h', 'm'])

        # Adds angle mod
        if angle:
            layout_description += "A"

            if not iso:
                layout = rotate_from_original(layout, Layout.ANSI_QWERTY, [
                    'b', 'v', 'c', 'x', 'z'])
            else:
                layout = rotate_from_original(layout, Layout.ISO_QWERTY, [
                    'b', 'v', 'c', 'x', 'z', '\\'])

        # Adds wide mod
        if wide:
            layout_description += "W"

            if not iso:
                layout = rotate_from_original(layout, Layout.ANSI_QWERTY, list(
                    "hjkl;']"), list('nm,./'), list('yuiop['), list('7890-='))
            else:
                layout = rotate_from_original(layout, Layout.ISO_QWERTY, list(
                    "hjkl;'#nm,./]"), list('yuiop['), list('7890-='))

        # Adds symbol mod
        if symbol:
            layout_description += "S"

            if iso or not wide:
                layout = rotate_from_alternate(layout, list(";'"), list("=-["))
            elif wide:
                layout = rotate_from_alternate(layout, list("\\=-';"))

        # Adds ISO/ANSI to layouts
        layouts.append(layout)

    # Account for no mods
    if layout_description == "Colemak ":
        layout_description = "Vanilla Colemak"

    # Toggle layout on and off
    toggle_layout_on = Manipulator().basic_from('`', ['left_command', 'left_shift']).set_variable_to(
        'qwerty', 1).require_variable('qwerty', 0)
    toggle_layout_off = Manipulator().basic_from('`', ['left_command', 'left_shift']).set_variable_to(
        'qwerty', 0).require_variable('qwerty', 1)

    # Turn string layouts into karabiner manipulators
    layout_manipulators = combine_ansi_iso(*layouts)
    for manipulator in layout_manipulators:
        manipulator.require_variable('qwerty', 0)
        manipulator.require_variable('extend', 0)

    # Turn manipulators into a rule with the layout description
    new_layout = Rule(layout_description, [
                      *layout_manipulators, toggle_layout_on, toggle_layout_off])

    # Extend variations
    for extend in (0, 1):
        rules = [new_layout]

        # Complicated logic for a simple task: give the extend layer the \zxcvb keys (in qwerty) as command keybinds for the layout
        if extend:
            if wide:
                layout_extend = copy.deepcopy(wide_extend)
            else: 
                layout_extend = copy.deepcopy(base_extend)
                
            for qwerty_key in ['z', 'x', 'c', 'v', 'b', '\\']:
                if qwerty_key != '\\':
                    key_position = Layout.ANSI_QWERTY.index(qwerty_key)
                    layout_key = layouts[0][key_position]

                    if layout_key in text_to_keycode:
                        layout_key = text_to_keycode[layout_key]

                    new_manipulator = Manipulator().basic_from(qwerty_key, optionalModifiers=[
                        "any"]).basic_to(layout_key, modifiers=["left_command"]).require_variable('extend', 1)

                key_position = Layout.ISO_QWERTY.index(qwerty_key)
                iso_key = layouts[1][key_position]

                if iso_key in text_to_keycode:
                    iso_key = text_to_keycode[iso_key]

                if layout_key == iso_key and qwerty_key != '\\':
                    new_manipulator.require_keyboard_types(['ansi', 'iso'])
                    layout_extend["manipulators"].append(
                        new_manipulator.serialize())
                else:
                    if qwerty_key != '\\':
                        new_manipulator.require_keyboard_types(['ansi'])
                        layout_extend["manipulators"].append(
                            new_manipulator.serialize())

                    if qwerty_key == '\\':
                        qwerty_key = 'non_us_backslash'

                    if iso_key == '\\':
                        iso_key = 'non_us_backslash'

                    layout_extend["manipulators"].append(Manipulator().basic_from(qwerty_key, optionalModifiers=["any"]).basic_to(
                        iso_key, modifiers=["left_command"]).require_variable('extend', 1).require_keyboard_types(["iso"]).serialize())

            # Adds extend rule for the extend variation
            rules.append(layout_extend)

        # Creates the karabiner ruleset with the variation's rules
        ruleset = create_ruleset("Colemak", rules)

        # Writes it to a file using curlanglewidesymbolextend.json, where each variation is a 1 or a 0
        # CAWS without extend will output to 11110.json, CA with extend will output to 11001.json, etc.
        json.dump(ruleset, open(
            f"layouts/{curl}{angle}{wide}{symbol}{extend}.json", "w"))
