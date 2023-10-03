"""
Utilities for handling JSON configurations for X-EOS.
Uses Python's built-in json module.
"""

import json

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
