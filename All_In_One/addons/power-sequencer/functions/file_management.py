"""Functions related to file management:
Fetching, loading and saving files to the disk."""
import bpy


def get_working_directory():
    """
    Takes the path to the current .blend file and
    returns the project's root directory (where the .blend file is saved)
    """
    full_path = bpy.data.filepath
    project_name = bpy.path.basename(full_path)
    working_directory = full_path[:len(full_path) - (len(project_name) + 1)]
    return working_directory


def create_text_file(name):
    """
    Create a new text file, change its name and return it
    Args:
    - name, the name of the text file, a string"""
    if not name and isinstance(name, str):
        raise TypeError('The name of the text file has to be a string')

    bpy.ops.text.new()
    import re
    re_text = re.compile(r'^Text.[0-9]{3}$')

    text_name = ''
    text_index, max_index = 0, 0
    for text in bpy.data.texts:
        if re_text.match(text.name):
            text_index = int(text.name[-3:])
            if text_index > max_index:
                max_index = text_index
                text_name = text.name
    if not text_name:
        text_name = 'Text'

    bpy.data.texts[text_name].name = name
    return bpy.data.texts[name]