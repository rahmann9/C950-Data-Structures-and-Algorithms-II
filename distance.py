# Distance matrix and address lookup utilities

import csv

def load_distance_data(file_path):
    """
    Loads a symmetric distance matrix from a CSV file.
    Returns a 2D list of distances.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        distance_matrix = [list(map(lambda x: float(x) if x else 0.0, row[1:])) for row in reader]
    return distance_matrix

def load_address_indices(file_path):
    """
    Loads addresses and maps each to a unique index (used for distance matrix lookups).
    Returns a dictionary {address_string: index}.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        address_dict = {}
        index = 0
        for row in reader:
            address = row[0].strip()
            address_dict[address] = index
            index += 1
    return address_dict
