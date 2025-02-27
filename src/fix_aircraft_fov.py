#!/usr/bin/env python3

import argparse
import configparser
import shutil
from pathlib import Path
import os

# Global variable to track dry-run state
DRY_RUN = False

# Global state tracking dictionary
FILE_STATS = {"total": 0, "modified": 0, "unchanged": 0, "errors": 0}

# Version Number
VERSION = "1.0.0"


class CasePreservingConfigParser(configparser.ConfigParser):
    """
    A ConfigParser that preserves the case of keys (option names).
    """

    def optionxform(self, optionstr):
        return optionstr


def find_camera_cfg_files(community_folder):
    """
    Recursively locates all cameras.cfg files within the community folder,
    following symbolic links.

    Args:
        community_folder (str): The path to the community folder.

    Yields:
        Path: The path to each cameras.cfg file found.
    """
    community_path = Path(community_folder)
    if not community_path.is_dir():
        print(f"Error: Community folder '{community_folder}' does not exist or is not a directory.")
        return

    for root, dirs, files in os.walk(community_path, followlinks=True):  # Added followlinks=True
        for file in files:
            if file == "cameras.cfg":
                file_path = Path(root) / file
                yield file_path


def get_backup_file_path(file_path, backup_ext):
    """
    Ensures the backup extension starts with a dot.

    Args:
        file_path (Path): The path to the cameras.cfg file
        backup_ext (str): The backup extension.

    Returns:
        Path: The backup file_path
    """
    backup_ext = backup_ext if backup_ext.startswith(".") else "." + backup_ext
    return file_path.with_suffix(file_path.suffix + backup_ext)


def backup_camera_cfg(file_path, backup_ext):
    """
    Backs up a single cameras.cfg file.

    Args:
        file_path (Path): The path to the cameras.cfg file.
        backup_ext (str): The extension to use for the backup file.
    """
    backup_file_path = get_backup_file_path(file_path, backup_ext)
    if DRY_RUN:
        print(f"  Dry-run: Would backup: '{file_path}' to '{backup_file_path}'")
    else:
        shutil.copy2(file_path, backup_file_path)
        print(f"  Backed up: '{file_path}' to '{backup_file_path}'")


def section_matches_camera(config, section, camera_name):
    """
    Checks if a given section in a config matches the target camera name.

    Args:
        config (configparser.ConfigParser): The loaded config.
        section (str): The name of the section to check.
        camera_name (str): The target camera name.

    Returns:
        bool: True if the section matches, False otherwise.
    """
    return "Title" in config[section] and (
        config[section]["Title"] == camera_name or config[section]["Title"] == f'"{camera_name}"'
    )


def modify_section_initialzoom(config, section, camera_zoom):
    """
    Modifies the InitialZoom in a given section of a config.

    Args:
        config (configparser.ConfigParser): The loaded config.
        section (str): The name of the section to modify.
        camera_zoom (float): The new value for InitialZoom.

    Returns:
        bool: True if the section was modified, False otherwise.
    """
    if "InitialZoom" not in config[section]:
        print(f"  Warning: Section '{section}' does not contain 'InitialZoom'.")
        return False

    original_zoom = config[section]["InitialZoom"]
    if original_zoom == str(camera_zoom):
        print(f"  Info: Section '{section}' InitialZoom already set to '{camera_zoom}'.")
        return False

    if DRY_RUN:
        print(
            f"  Dry-run: Would modify section '{section}', InitialZoom would change from '{original_zoom}' to '{camera_zoom}'"
        )
    else:
        config[section]["InitialZoom"] = str(camera_zoom)
        print(f"  Modified section '{section}', InitialZoom changed from '{original_zoom}' to '{camera_zoom}'")
    return True


def modify_single_camera_cfg(file_path, camera_name, camera_zoom, backup_ext, disable_strict):
    """
    Modifies a single cameras.cfg file based on camera_name and camera_zoom,
    and backs up the original file only if changes were made.

    Args:
        file_path (Path): The path to the cameras.cfg file.
        camera_name (str): The camera name to search for within each section's "Title" key.
        camera_zoom (float): The new value for InitialZoom.
        backup_ext (str): The extension to use for the backup file.
        disable_strict (bool): if true the configparser will be set to non-strict mode
    """
    global FILE_STATS
    print(f"Processing: '{file_path}'")
    modified = False
    found_matching_title = False

    try:
        config = CasePreservingConfigParser(strict=not disable_strict)  # Create with strict mode option
        config.read(file_path)

        for section in config.sections():
            if section_matches_camera(config, section, camera_name):
                found_matching_title = True
                if modify_section_initialzoom(config, section, camera_zoom):
                    modified = True

        if not found_matching_title:
            print(f"  Info: No section found with Title matching '{camera_name}'.")

        if not modified:
            print(f"  Info: No changes needed for '{file_path}'.")
            FILE_STATS["unchanged"] += 1
            print()
            return

        backup_camera_cfg(file_path, backup_ext)
        FILE_STATS["modified"] += 1

        if DRY_RUN:
            print(f"  Dry-run: Would write changes to '{file_path}'")
        else:
            with open(file_path, "w") as configfile:
                config.write(configfile)
            print(f"  Updated: '{file_path}'")
        print()

    except Exception as e:
        print(f"Error: {e}")
        FILE_STATS["errors"] += 1
        print()


def find_and_modify_cameras(community_folder, camera_name, camera_zoom, backup_ext, disable_strict):
    """
    Orchestrates the process of finding and modifying camera.cfg files.
    """
    global FILE_STATS
    FILE_STATS["total"] = 0
    FILE_STATS["modified"] = 0
    FILE_STATS["unchanged"] = 0
    FILE_STATS["errors"] = 0
    file_paths = list(find_camera_cfg_files(community_folder))
    FILE_STATS["total"] = len(file_paths)
    print(f"Found {FILE_STATS['total']} 'cameras.cfg' file(s) to modify.")
    print()

    for file_path in file_paths:
        modify_single_camera_cfg(file_path, camera_name, camera_zoom, backup_ext, disable_strict)

    print(f"Processed files: {FILE_STATS['total']}")
    print(f"Modified files: {FILE_STATS['modified']}")
    print(f"Unchanged files: {FILE_STATS['unchanged']}")
    print(f"Files with errors: {FILE_STATS['errors']}")


def restore_single_camera_cfg(file_path, backup_ext):
    """
    Restores a single cameras.cfg file from its backup.

    Args:
        file_path (Path): The path to the cameras.cfg file.
        backup_ext (str): The extension used for the backup file.
    """
    global FILE_STATS
    backup_file_path = get_backup_file_path(file_path, backup_ext)

    if backup_file_path.exists():
        print(f"Restoring: '{file_path}' from '{backup_file_path}'")
        if DRY_RUN:
            print(f"  Dry-run: Would copy '{backup_file_path}' to '{file_path}'")
            print(f"  Dry-run: Would remove '{backup_file_path}'")
        else:
            try:
                shutil.copy2(backup_file_path, file_path)
                print(f"  Successfully restored '{file_path}'")
                os.remove(backup_file_path)
            except Exception as e:
                print(f"Error restoring '{file_path}': {e}")
                FILE_STATS["errors"] += 1
        FILE_STATS["modified"] += 1
        print()
    else:
        print(f"No backup for: '{file_path}'")
        FILE_STATS["unchanged"] += 1
        print()


def find_and_restore_cameras(community_folder, backup_ext):
    """
    Orchestrates the process of finding and restoring camera.cfg files.
    """
    global FILE_STATS
    FILE_STATS["total"] = 0
    FILE_STATS["modified"] = 0
    FILE_STATS["unchanged"] = 0
    FILE_STATS["errors"] = 0
    file_paths = list(find_camera_cfg_files(community_folder))
    FILE_STATS["total"] = len(file_paths)
    print(f"Found {FILE_STATS['total']} 'cameras.cfg' file(s) to restore.")
    print()

    for file_path in file_paths:
        restore_single_camera_cfg(file_path, backup_ext)

    print(f"Processed files: {FILE_STATS['total']}")
    print(f"Restored files: {FILE_STATS['modified']}")
    print(f"Backup not found: {FILE_STATS['unchanged']}")
    print(f"Files with errors: {FILE_STATS['errors']}")


def main():
    """
    Parses command line arguments and calls the appropriate function.
    """
    parser = argparse.ArgumentParser(description="Modify or restore InitialZoom in MSFS cameras.cfg files.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--modify", action="store_true", help="Modify cameras.cfg files with new zoom.")
    group.add_argument("--restore", action="store_true", help="Restore cameras.cfg files from backups.")

    parser.add_argument("--community-folder", required=True, help="Path to the community folder or specific add-on.")
    parser.add_argument(
        "--backup-ext",
        help="The extension used for the backup file (default: '.fix_aircraft_fov', e.g., '.bak')",
        default="fix_aircraft_fov",
    )

    parser.add_argument(
        "--camera-name",
        help="The camera name to search for within each section's 'Title' key (default: 'Pilot', required for --modify).",
        default="Pilot",
    )
    parser.add_argument(
        "--camera-zoom", type=float, help="The new value for InitialZoom (default: 0.35, required for --modify).", default=0.35
    )

    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without actually doing it.")
    parser.add_argument("--disable-strict", action="store_true", help="Disable strict mode in configparser (discard duplicate keys).")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    args = parser.parse_args()

    global DRY_RUN
    DRY_RUN = args.dry_run
    
    print(f"FixAircraftFOV {VERSION}")

    if args.modify:
        if not args.camera_name or not args.camera_zoom:
            parser.error("--modify requires --camera-name and --camera-zoom")
        find_and_modify_cameras(args.community_folder, args.camera_name, args.camera_zoom, args.backup_ext, args.disable_strict)
    elif args.restore:
        find_and_restore_cameras(args.community_folder, args.backup_ext)


if __name__ == "__main__":
    main()
