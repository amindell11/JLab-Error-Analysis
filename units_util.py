prefix_multipliers = {
    'p': 1e-12,  # pico
    'n': 1e-9,   # nano
    'µ': 1e-6,   # micro
    'm': 1e-3,   # milli
    'c': 1e-2,   # centi
    'd': 1e-1,   # deci
    '': 1,       # base unit (no prefix)
    'k': 1e3,    # kilo
    'M': 1e6,    # mega
    'G': 1e9,    # giga
    'T': 1e12    # tera
}
def extract_unit(column_name):
    """Extracts unit from the column label, if present."""
    if '(' in column_name and ')' in column_name:
        name, unit = column_name.split('(')
        unit = unit.strip(')').strip()
        name = name.strip()
    else:
        name = column_name
        unit = ''
    return name, unit

def convert_to_base_units(value, unit):
    """Converts a value with a metric-prefixed unit to its base unit.
    
    Parameters:
    value (float): The numeric value to convert.
    unit (str): The unit with a possible metric prefix (e.g., 'mA', 'kΩ').

    Returns:
    float, str: The converted value and the base unit.
    """
    # Dictionary mapping metric prefixes to their multiplier

    
    # Extract the prefix and the base unit
    for prefix, multiplier in prefix_multipliers.items():
        if unit.startswith(prefix) and len(unit) > len(prefix):
            base_unit = unit[len(prefix):]  # Remove the prefix to get the base unit
            # Convert the value to the base unit
            return value * multiplier, base_unit

    # If no prefix is found, assume the unit is already in base form
    return value, unit

def convert_from_base_units(value, target_unit):
    """Converts a value in base units to the specified unit with a metric prefix.
    
    Parameters:
    value (float): The numeric value in base units to convert.
    target_unit (str): The target unit with a desired metric prefix (e.g., 'mA', 'kΩ').

    Returns:
    float, str: The converted value and the prefixed unit.
    """
    # Dictionary mapping metric prefixes to their multiplier
    for prefix, multiplier in prefix_multipliers.items():
        if target_unit.startswith(prefix) and len(target_unit) > len(prefix):
            base_unit = target_unit[len(prefix):]  # Remove prefix to get the base unit
            # Convert the value to the specified prefixed unit
            return value / multiplier, target_unit

    # If no prefix is found, assume the target unit is the base unit
    return value, target_unit
