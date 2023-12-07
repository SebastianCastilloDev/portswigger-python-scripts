"""
Helpers for authentication_vulnerabilities
"""


def read_file(file_path):
    """Function to read files"""
    try:
        return open(file_path, "r", encoding='utf-8').read()
    except FileNotFoundError as e:
        print(e)
        return None
