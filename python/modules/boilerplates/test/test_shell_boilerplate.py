#!/usr/bin/env python
"""Common test logic for shell interactions"""

# --- Global Shell Commands ---
# :-Helper-:        format_resource, is_valid_resource, random_password
# JSON:             is_json_parse, is_json_str, parse_json, convert_json, save_json
# Utility:          shift_directory, change_directory, is_list_of_strings, list_differences, print_command
# Process:          exit_process, fail_process, process_id, process_parent_id
# Path:             current_path, expand_path, join_path, path_exists, path_dir, path_basename, path_filename
# Directory:        list_directory, create_directory, delete_directory, copy_directory, sync_directory
# File:             read_file, write_file, delete_file, rename_file, copy_file, hash_file, file_match, backup_file
# Signal:           max_signal, handle_signal, send_signal
# SubProcess:       run_subprocess, log_subprocess

import shell_boilerplate as sh

# ------------------------ Global Test Commands ------------------------

# --- Helper Commands ---


def test_format_resource():
    """Verify the output of 'format_resource' function"""
    mock_name = "rg-001"
    output = sh.format_resource(mock_name)
    assert output == "rg-001"


def test_is_valid_resource():
    """Verify the output of 'is_valid_resource' function"""
    mock_name = "rg-001"
    output = sh.is_valid_resource(mock_name)
    assert output is True
