# Fix Aircraft FOV (for Microsoft Flight Simulator)

## Overview

The **Fix Aircraft FOV** tool aims to provide a solution for modifying and restoring camera zoom settings in Microsoft Flight Simulator.

Most stock aircraft are set up correctly with a 0.35 zoom, and thus are consistent across models.
However, many third-party aricraft or aircraft mods change this zoom setting, altering the expected FOV, which can make it difficult to adjust.

This tool ensures camera FOV consistency across all aircraft by allowing users to easily adjust the zoom levels in the `cameras.cfg` files used by the simulator.
You can run it one time, or even script it into your MSFS startup flow so you're not surprised when an update botches this setting.


## Features

- Modify the `InitialZoom` settings for various camera views.
- Makes changes only when needed, and backups during modification.
- Has simple restore of original settings from backup files when needed.
- Supports dry-run mode to preview changes without applying them.
- Allows loose parsing to fix files that may have duplicate keys.

## Installation

1.  **Download:** Go to the [releases](https://github.com/IslandJohn/FixAircraftFOV/releases/) page of the project on GitHub and download the latest archive (e.g., `FixAircraftFOV-1.0.0.zip`).
2.  **Extract:** Extract the contents of the downloaded archive to a folder on your computer where you'd like to keep the tool. For example, you could create a folder called `FixAircraftFOV` in your `Documents` or `Downloads` directory.
3.  **Open Command Prompt or Terminal:** Press the Windows key, type `cmd`, and press Enter to open the Command Prompt.
4.  **Navigate to the Extracted Folder:** Use the `cd` command (change directory) to navigate to the folder where you extracted the files. For example, if you extracted the files to your `Documents\FixAircraftFOV` folder, you would type the following and press Enter:

    ```bash
    cd C:\Users\<YourName>\Documents\FixAircraftFOV
    ```
5. **Run the tool:** You should now be able to run the tool.

## Usage

To modify camera zoom settings, use the following command:

```
fix_aircraft_fov.exe --modify --community-folder <path_to_community_folder>
```

To restore the original settings from backups, use:

```
fix_aircraft_fov.exe --restore --community-folder <path_to_community_folder>
```

To see how other cameras and zoom levels can be changed:

```
fix_aircraft_fov.exe --h
```

By default the "Pilot" camera is modified to have a zoom level of 0.35 (like most stock aircraft).

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details. 

## Disclaimer

The authors of this software are not responsible for any damages or issues arising from the use of this software. Use at your own risk.
