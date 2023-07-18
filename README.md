# Subnautica Nitrox Game Manager

Manage different worlds for Subnautica Nitrox with built-in backups.

## Overview
- Easily create backups with a single button click.
- Manage an unlimited number of worlds and switch between them effortlessly with just two clicks.

## Setup
- The Nitrox Game Manager works out-of-the-box by double-clicking `SubnauticaNitroxGameManager.exe` in the source directory.
- Make sure to provide the absolute path to Nitrox's files. This path should be the highest directory where Nitrox stores its files, containing folders such as "`AssetBundles`", "`LanguageFiles`", "`lib`", and more.

## Worlds
### Creating Worlds
- Create a new world by either starting up the Nitrox Game Manager for the first time or clicking on `Duplicate Current World as New World` or `Add Empty World as New World`. The former button duplicates the current world, creating a new editable world, while the latter option generates a blank world for you to use.

### Switching Worlds
- Change worlds by using the Selection Box at the top of the Nitrox Game Manager. Select the world you want to switch to, and the Nitrox Game Manager will save your current world and switch to the selected one.

### Deleting Worlds
- To delete a world, ensure that you have selected the desired world using the Nitrox Game Manager. Then, click `Delete World`, and your world's backups will be deleted. You will be prompted to decide whether you want to remove this world from Nitrox as well.

## Backups
### Creating Backups
- Ensure that you have selected the desired world using the Nitrox Game Manager. Then, click `Backup`, and the Nitrox Game Manager will create a backup for you.

### Retrieving Backups
- Ensure that you have selected the desired world using the Nitrox Game Manager. Then, click `Rollback`, select the backup to rollback to, and the Nitrox Game Manager will take care of the rest.

## Special Features
- You can adjust the total number of backups by navigating to `Files → data.json → max_backups` and changing the number.
- If you need to change Nitrox's path, go to `Files → data.json → nitrox_path` and update the path accordingly.

## Credits
- Cypress4382
