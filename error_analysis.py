from unicodedata import decimal
import pandas as pd
import numpy as np
import units_util as uut
import data_util as dut
from math import sqrt

SYSTEMATIC_ERROR_FILE = 'measurement_error.csv'

def calculate_best_value(samples):
    """Calculates the best value as the mean of samples."""
    return np.mean(samples)

def calculate_random_error(samples):
    """Calculates random error as the standard deviation divided by sqrt(3)."""
    return np.std(samples, ddof=1) / sqrt(3)

def determine_appropriate_range(reading, unit, table):
    """Determines the smallest range that can contain the reading based on the table."""
    filtered_table = table[table["Measurement Type"].str.contains(unit, na=False)]
    suitable_ranges = filtered_table[filtered_table["Range"] >= reading]
    if not suitable_ranges.empty:
        # Select the row with the smallest range that contains the reading
        best_fit = suitable_ranges.loc[suitable_ranges["Range"].idxmin()]
        return best_fit["Measurement Type"], float(best_fit["%Reading Err"]), float(best_fit["%Range Err"]), float(best_fit["Range"])
    else:
        # Return zeroes if no suitable range is found
        return 0.0, 0.0, 0.0

def calculate_systematic_error_with_table(reading, unit, table):
    """Calculates the systematic error based on the closest range for the reading and column."""
    measurement_type, reading_err, range_err, range_value = determine_appropriate_range(reading, unit, table)
    print(f"using range {measurement_type} for value {reading} {unit}")
    return calculate_systematic_error(reading, reading_err, range_err, range_value)

def calculate_systematic_error(reading, reading_err, range_err, range_value):
    systematic_error = (reading_err / 100) * reading + (range_err / 100) * range_value
    return systematic_error

def calculate_total_error(random_error, systematic_error):
    """Calculates the total error as the geometric sum of random and systematic errors."""
    return sqrt(random_error**2 + systematic_error**2)

def format_result(best_value, total_error, unit, include_units):
    """Formats the result to display with specific decimal places based on the precision of total error and best value."""

    # Format best_value and total_error with the determined precision
    formatted_total_error, decimal_places = format_error(total_error)
    formatted_best_value = format_best_value(best_value,decimal_places)
    
    # Append units if specified
    if include_units and unit:
        return f"{formatted_best_value} ± {formatted_total_error} {unit}"
    else:
        return f"{formatted_best_value} ± {formatted_total_error}"

def format_best_value(best_value, decimal_places):
        return f"{best_value:.{decimal_places}f}"

def format_error(total_error):
        # Calculate decimal places based on the total error's magnitude
    if total_error != 0:
        decimal_places = max(0, -int(np.floor(np.log10(total_error))))
    else:
        decimal_places = 1

    # Convert total_error to scientific notation to find the first significant digit
    total_error_sci_str = f"{total_error:.{decimal_places+2}e}"
    first_significant_digit = total_error_sci_str.split('e')[0].replace(".", "").lstrip("0")[0]

    # Enforce two decimal places if the first significant figure of total_error is 1
    if first_significant_digit == '1':
        decimal_places += 1
    return f"{total_error:.{decimal_places}f}", decimal_places

def calculate_group_errors(data, include_units=True,format_results=True,format_values=True):
    """Calculates the errors for each group of trials in the dataset, including systematic error."""
    results = []
    grouped = data.groupby('group')
    for name, group in grouped:
        if len(group) != 3:
            continue  # Skip if not exactly 3 trials

        group_results = {"N": name}
        
        for column in group.columns[2:-1]:  # Exclude 'N', 'Unnamed: 1', and 'group'
            samples = group[column].dropna().values
            if len(samples) < 3:
                group_results[column] = "Insufficient data"
                continue
            col_name, unit = uut.extract_unit(column)
            best_value = calculate_best_value(samples)
            random_error = calculate_random_error(samples)
            stripped_value,base_unit = uut.convert_to_base_units(best_value, unit)
            systematic_error_table = dut.load_systematic_error_table(SYSTEMATIC_ERROR_FILE)
            base_systematic_error = calculate_systematic_error_with_table(stripped_value, base_unit, systematic_error_table)
            converted_systematic_error = uut.convert_from_base_units(base_systematic_error, unit)[0]
            total_error = calculate_total_error(random_error, converted_systematic_error)
            if format_results:
                # Format the result as a string with error if `format_results` is True
                result = format_result(best_value, total_error, unit, include_units)
            else:
                total_error_str,decimal_places = format_error(total_error)
                best_value_str = format_best_value(best_value, decimal_places)
                unit_str = f"({unit})" if include_units else ""
                group_results[f"{col_name} {unit_str}"] = best_value_str if format_values else best_value 
                group_results[f"{col_name} Err {unit_str}"] = total_error_str if format_values else total_error
        results.append(group_results)

    return pd.DataFrame(results)

# Example usage:
data_file = 'resistor_data.csv'  # Replace with the actual data file path
output_file = 'resistor_data_errors.csv'
data = dut.load_and_prepare_data(data_file)
results_df = calculate_group_errors(data, include_units=True, format_results=False, format_values=True)
print(results_df)
dut.export_results(results_df,output_file)
