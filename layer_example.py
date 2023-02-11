from manipulator import manipulators_from_keys, Manipulator, create_virtual_modifier
from layouts import Layout
from rule import Rule, create_ruleset
import json

# This layer will just be ansi colemak mirrored from left to right. 
# Change this to whatever you'd like the new layer to be
new_layer = "=-0987654321`\][;yuljgpfwq'oienhdtsra/.,mkbvcxz"

# This is the variable that will be used to toggle the layer. This variable must be unique for each layer
variable_name = "unique_layer_variable"
# This uses ANSI_QWERTY. If you are using ISO, change this to Layout.ISO_QWERTY
#    ANSI_QWERTY = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
#    ISO_QWERTY = "`1234567890-=qwertyuiop[]asdfghjkl;'#\\zxcvbnm,./"
layer_manipulators = manipulators_from_keys(Layout.ANSI_QWERTY, new_layer, allow_duplicates=False)

for manipulator in layer_manipulators:
    manipulator.require_variable(variable_name, 1)
  
# In this case, right_command is the virtual modifier key (switches to layer), replace with any key_code
modifier_key = create_virtual_modifier("right_command", variable_name)

rule = Rule("Layer Rule Example Description", [*layer_manipulators]).serialize([modifier_key])
ruleset = create_ruleset("Layer Ruleset Example Title", [rule])


# Place the outputted file in ~/.config/karabiner/assets/complex_modifications
# Enable the script in complex modifications within karabiner-elements
# Ensure the script is dragged near the top, above colemak if enabled
with open("layer_example.json", "w") as file:
    json.dump(ruleset, file)