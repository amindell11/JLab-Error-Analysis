import pandas as pd

def load_systematic_error_table(file_path):
    """Loads the systematic error parameters from a CSV file."""
    table = pd.read_csv(file_path)
        # Check the number of columns and print if it doesn’t match expectations
    if table.shape[1] != 4:
        print("Warning: The systematic error table does not have the expected 4 columns.")
        print("Columns found:", table.columns)
        print("Ensure the CSV file matches the expected format: [Measurement Type, %Reading Err, %Range Err, Range]")
    
    # Rename columns to match the expected headers if the file has exactly 4 columns
    table.columns = ["Measurement Type", "%Reading Err", "%Range Err", "Range"]

    table.columns = ["Measurement Type", "%Reading Err", "%Range Err", "Range"]
    return table

def load_and_prepare_data(file_path):
    """Loads CSV data and identifies groups of trials based on non-NaN values in the 'N' column."""
    data = pd.read_csv(file_path)
    if (len(data[data.columns[0]]) <=4):
        data = handle_single_point_data(data)
    data['group'] = data[data.columns[0]].ffill()  # Forward fill 'N' to group data
    print(data)
    data = data.dropna(subset=data.columns[2]).reset_index(drop=True)  # Drop rows with NaN in data columns
    return data

def handle_single_point_data(data):
    """Prepends a new column to the DataFrame at column position 0."""
    
    # Define the new column data, using a default value or calculation if needed
    new_column_data = [0] * len(data)  # Example: a column of zeroes, same length as DataFrame
    
    # Insert the new column at position 0
    data.insert(0, 'N', new_column_data)  # 'NewColumn' is the name of the new column
    
    return data
import pandas as pd

def export_results(dataframe, file_path, file_type='csv'):
    """Exports the resulting DataFrame to a specified file format.
    
    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the results.
    file_path (str): The path where the file should be saved.
    file_type (str): The file format to save as ('csv' or 'excel'). Defaults to 'csv'.
    """
    if file_type == 'csv':
        dataframe.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"Results successfully saved to {file_path} as a CSV file.")
    elif file_type == 'excel':
        dataframe.to_excel(file_path, index=False, encoding='utf-8-sig')
        print(f"Results successfully saved to {file_path} as an Excel file.")
    else:
        raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")
