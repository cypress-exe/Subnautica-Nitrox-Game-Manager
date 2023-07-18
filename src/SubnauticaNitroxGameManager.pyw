from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
import json
import os
import shutil
import datetime

class Files:
    def __init__(self):
        self.dataStructure = {
            "nitrox_path": None,
            "current_world": None,
            "max_backups": 10,
            "files": ["server.cfg", "world"],
        }
        
        
        # Determine working directory and thus file paths
        if os.path.exists("./src"):
            self.filesPath = "./Files"
            self.worldsPath = "./Files/"
            self.dataPath = "./Files/data.json"
        elif os.path.exists("../src"):
            self.filesPath = "../Files"
            self.worldsPath = "../Files/"
            self.dataPath = "../Files/data.json"
        else:
            raise RuntimeError("Please run the program from the correct directory or the exe file in the dist folder.")
        
        # Ensure that the "Files" exists
        if not os.path.exists(self.filesPath):
            os.mkdir(self.filesPath)
        
        self.data = {}
        try:
            with open(self.dataPath, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            pass
        
        self.data = self.standardizeDictProperties(self.dataStructure, self.data)
        
        # Set Values
        self.nitrox_path = self.data["nitrox_path"]
        self.current_world = self.data["current_world"]
        self.max_backups = self.data["max_backups"]
        self.files = self.data["files"]
        
        # Get Worlds
        self.refreshWorlds()
        
    def saveData(self):
        data = {
            "nitrox_path": self.nitrox_path,
            "current_world": self.current_world,
            "max_backups": self.max_backups,
            "files": self.files,
        }
        
        with open(self.dataPath, "w") as file:
            json.dump(data, file)
    
    def refreshWorlds(self):
        self.worlds = self.getFolderNames(self.worldsPath)

    def addWorld(self, name):
        os.mkdir(os.path.join(self.worldsPath, name))
        self.backupWorld(name)
        self.refreshWorlds()

    def renameWorld(self, name_old, name_new):
        os.rename(os.path.join(self.worldsPath, name_old), os.path.join(self.worldsPath, name_new))
        self.refreshWorlds()
        
    def deleteWorld(self, world_name):
        shutil.rmtree(os.path.join(self.worldsPath, world_name), ignore_errors=False)
        self.refreshWorlds()
        
    def backupWorld(self, world_name):
        path = os.path.join(self.worldsPath, world_name)

        if not os.path.exists(path):
            raise FileNotFoundError()

        folderName = str(datetime.datetime.now()).replace(":", "_").split(".")[0]
        backupPath = os.path.join(path, folderName)

        # Make backup directory
        os.mkdir(backupPath)

        # Recursively copy the contents of the source folder to the destination folder
        for item in self.files:
            source_path = os.path.join(self.nitrox_path, item)

            if os.path.exists(source_path):
                if os.path.isdir(source_path):  # Handle directories
                    destination_path = os.path.join(backupPath, item)
                    shutil.copytree(source_path, destination_path)
                else:  # Handle individual files
                    destination_path = os.path.join(backupPath, os.path.basename(source_path))
                    shutil.copy(source_path, destination_path)
                        
                        
        
        # Finally, double check that we're not storing more backups than we need to.
        oldest_to_newest_backups = sorted(self.getFolderNames(path))
        if len(oldest_to_newest_backups) > self.max_backups:
            shutil.rmtree(os.path.join(path, oldest_to_newest_backups[0]), ignore_errors=False)
            
    def rollbackWorld(self, world_name, backup_name):
        path = os.path.join(self.worldsPath, world_name)

        if not os.path.exists(path):
            raise FileNotFoundError()

        backupPath = os.path.join(path, backup_name)
        
        if not os.path.exists(backupPath):
            raise FileNotFoundError()

        # Make rollback directory
        folderName = str(datetime.datetime.now()).replace(":", "_").split(".")[0] + "_rollback_from_version_" + backup_name
        rollbackPath = os.path.join(path, folderName)
        os.mkdir(rollbackPath)

        # Recursively copy the contents of the source folder to the destination folder
        for item in self.files:
            source_path = os.path.join(backupPath, item)

            if os.path.exists(source_path):
                if os.path.isdir(source_path):  # Handle directories
                    destination_path = os.path.join(rollbackPath, item)
                    shutil.copytree(source_path, destination_path)
                else:  # Handle individual files
                    destination_path = os.path.join(rollbackPath, os.path.basename(source_path))
                    shutil.copy(source_path, destination_path)
                        
                        
        
        # Finally, double check that we're not storing more backups than we need to.
        oldest_to_newest_backups = sorted(self.getFolderNames(path))
        if len(oldest_to_newest_backups) > self.max_backups:
            shutil.rmtree(os.path.join(path, oldest_to_newest_backups[0]), ignore_errors=False)
        
    def getBackups(self, world_name):
        path = os.path.join(self.worldsPath, world_name)
        return(self.getFolderNames(path))
        
    def deleteLastBackup(self, world_name, withinonesecond=False):
        path = os.path.join(self.worldsPath, world_name)
        
        pathToBackupToDelete = self.backupsPathToLatestBackupPath(path)
        
        if withinonesecond:
            wouldBeName = str(datetime.datetime.now()).replace(":", "_").split(".")[0]
            actualName = os.path.basename(pathToBackupToDelete)
            if not wouldBeName and actualName:
                # Out of safety, if it's not within the same second, we won't do this.
                return
        
        shutil.rmtree(pathToBackupToDelete, ignore_errors=False)
        
    def deleteNitroxWorld(self):
        for item in self.files:
            item_path = os.path.join(self.nitrox_path, item)
            if os.path.exists(item_path):
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        
    def changeNitroxWorld(self, world_name):
        source_directory = self.backupsPathToLatestBackupPath(os.path.join(self.worldsPath, world_name))
        
        if not os.path.exists(source_directory):
            raise FileNotFoundError()
        
        # Get a list of files in the source directory
        files = os.listdir(source_directory)

        # Delete old files
        self.deleteNitroxWorld()

        # Copy each file or directory from source to destination
        for item in os.listdir(source_directory):
            source_item = os.path.join(source_directory, item)
            destination_item = os.path.join(self.nitrox_path, item)
            
            if os.path.exists(source_item):
                if os.path.isfile(source_item):
                    shutil.copy(source_item, destination_item)
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, destination_item)
        
    def standardizeDictProperties(self, defaultDict: dict, objectDict: dict, aliases: dict = {}):
        returnDict = defaultDict.copy()
        
        objectDict = {aliases.get(k, k): v for k, v in objectDict.items()}
        
        for key in returnDict:
            if key in objectDict:
                if isinstance(objectDict[key], dict):
                    returnDict[key] = self.standardizeDictProperties(returnDict[key], objectDict[key], aliases=aliases)
                else:
                    returnDict[key] = objectDict[key]
            
        return returnDict

    def getFolderNames(self, directory):
        folders = [folder.name for folder in os.scandir(directory) if folder.is_dir()]
        return folders
    
    def getFileNames(self, directory):
        files = [file.name for file in os.scandir(directory) if file.is_file()]
        return files

    def backupsPathToLatestBackupPath(self, path):
        oldest_to_newest_backups = sorted(self.getFolderNames(path))
        if len(oldest_to_newest_backups) == 0:
            raise FileNotFoundError()
        
        return os.path.join(path, oldest_to_newest_backups[-1])
            
    def countFilesToSave(self):
        count = 0
        for item in self.files:
            item_path = os.path.join(self.nitrox_path, item)
            if os.path.isfile(item_path):
                count += 1
            elif os.path.isdir(item_path):
                for root, dirs, files in os.walk(item_path):
                    count += len(files)
        return count
    
class GUI:
    def __init__(self, files: Files):
        self.files = files
        
        # Setup UI
        self.root = Tk()
        self.root.title("Subnautica Nitrox Game Manager")
        self.root.resizable(0, 0)
        self.root.geometry("350x300")
        self.root.update()
        
        self.mainWindow()
        
    def mainWindow(self):
        # Clear tk
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Check for incomplete variables
        self.validateData()
        
        # Create world select
        self.worldSelectFrame = Frame(self.root, pady=10)
        self.worldSelectFrame.pack()
        self.worldSelectLabel = Label(self.worldSelectFrame, text="Current World")
        self.worldSelectLabel.pack(side="left")
        self.worldSelectValue = StringVar(self.worldSelectFrame, self.files.current_world)
        self.worldSelect = OptionMenu(self.worldSelectFrame, self.worldSelectValue, *self.files.worlds, command=self.changeWorld)
        self.worldSelect.pack(side="left")
        
        self.worldOptionsFrame = Frame(self.root, padx=20)
        self.worldOptionsFrame.pack(fill="x")
        self.backupWorldBtn = Button(self.worldOptionsFrame, text="Backup World", command=self.backupWorld)
        self.backupWorldBtn.pack(fill="x", pady=5)
        self.renameWorldBtn = Button(self.worldOptionsFrame, text="Rename World", command=self.renameWorld)
        self.renameWorldBtn.pack(fill="x", pady=5)
        self.deleteWorldBtn = Button(self.worldOptionsFrame, text="Delete World", command=self.deleteWorld)
        self.deleteWorldBtn.pack(fill="x", pady=5)
        self.rollbackWorldBtn = Button(self.worldOptionsFrame, text="Rollback World", command=self.rollbackWorld)
        self.rollbackWorldBtn.pack(fill="x", pady=5)
        
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=10)
        
        self.globalOptionsFrame = Frame(self.root, padx=20)
        self.globalOptionsFrame.pack(fill="x")
        self.addWorldBtn = Button(self.globalOptionsFrame, text="Duplicate Current World as New World", command=self.addWorld)
        self.addWorldBtn.pack(fill="x", pady=5)
        self.addWorldEmptyBtn = Button(self.globalOptionsFrame, text="Add Empty World As New World", command=self.addWorldEmpty)
        self.addWorldEmptyBtn.pack(fill="x", pady=5)
        
    def validateData(self):
        if self.files.nitrox_path is None:
            response = simpledialog.askstring("Nitrox World Path", "Provide the absolute path of Nitrox's files.")
            if response and os.path.exists(response):
                self.files.nitrox_path = response
                self.files.saveData()
            else:
                self.root.quit()
                quit()
        
        if self.files.current_world is None or self.files.current_world not in self.files.worlds:
            # Make sure that there's a world to even use.
            if self.files.countFilesToSave() == 0:
                if len(self.files.worlds) == 0:
                    reset = messagebox.askyesno("World Required", "Your Nitrox path does not have any worlds in it. Would you like to reset your Nitrox path? If not, you will be exited out of this application.")
                    if reset:
                        self.files.nitrox_path = None
                        self.validateData()
                    else:
                        self.root.quit()
                        quit()
                else:
                    self.files.current_world = self.files.worlds[0]
                    self.files.saveData()
                    self.files.changeNitroxWorld(self.files.current_world)
                    self.validateData()
                    return
            
            response = simpledialog.askstring("Unknown World", "This world has an unknown name. Please specify a name for it.")
            if response:
                self.files.current_world = response
                self.files.saveData()
                
                if response not in self.files.worlds:
                    self.files.addWorld(response)
            else:
                self.root.quit()
                quit()
    
    def backupWorld(self):
        self.files.backupWorld(self.worldSelectValue.get())
        messagebox.showinfo("Backed Up!", "This save has been backed up.")
        
    def renameWorld(self):
        old_name = self.worldSelectValue.get()
        response = simpledialog.askstring("Rename World", f"Please specify a name to rename world {old_name} to.", initialvalue=old_name)
        if not response:
            return
        
        if response not in self.files.getFolderNames(self.files.worldsPath):
            self.files.renameWorld(old_name, response)
            self.files.current_world = response
            self.files.saveData()
            
            messagebox.showinfo("Renamed World", "World has been renamed. No conflicts.")
        else:
            messagebox.showerror("Failed to Rename World", f"World \"{response}\" already exists. Please choose a different name.")
            
        # Reset Main Window
        self.mainWindow()
        
    def deleteWorld(self):
        world_name = self.worldSelectValue.get()
        agree = messagebox.askyesno("Confirmation", f"Are you sure you want to delete world \"{world_name}\"? This will delete all backups, and is not reversible.")
        if not agree:
            return
        
        self.files.deleteWorld(world_name)
        self.files.current_world = None
        self.files.saveData()
            
        agree = messagebox.askyesno("Also Delete from Nitrox?", f"Would you also like to delete the world from Nitrox?")
        if agree:
            self.files.deleteNitroxWorld()
        
        messagebox.showinfo("Deleted World", "World has been deleted.")
        
        # Reset Main Window
        self.mainWindow()

    def changeWorld(self, *args):
        new_world = self.worldSelectValue.get()
        old_world = self.files.current_world
        
        try:
            self.files.backupWorld(old_world)
        except Exception as error:
            print(error)
            # There was a problem, so let's get rid of that backup.
            self.files.deleteLastBackup(old_world, withinonesecond=True)
            messagebox.showerror("Failed to Transfer World", "Failed to transfer world for an unknown reason. Returning to the last world.")
            self.worldSelectValue.set(old_world)
            return
        
        try:
            self.files.changeNitroxWorld(new_world)
        except Exception as error:
            print(error)
            # There was a problem, so let's put them back to the old world.
            self.files.changeNitroxWorld(old_world)
            messagebox.showerror("Failed to Transfer World", "Failed to transfer world for an unknown reason. Returning to the last world.")
            self.worldSelectValue.set(old_world)
            return
            
        self.files.current_world = new_world
        self.files.saveData()
        messagebox.showinfo("Successfully Transferred Worlds", f"Transferred worlds. You are now in the {new_world} world.")
        
    def addWorld(self):
        response = simpledialog.askstring("World Name", f"Please specify a name for the new current world.")
        if not response:
            return
        
        if response not in self.files.getFolderNames(self.files.worldsPath):
            self.files.backupWorld(self.files.current_world)
            self.files.addWorld(response)
            self.files.current_world = response
            self.files.saveData()
        
            messagebox.showinfo("Added World", "World has been added. No conflicts. You have been switched to the world.")
        else:
            messagebox.showerror("Failed to Add World", f"World \"{response}\" already exists. Please choose a different name.")
            
        # Reset Main Window
        self.mainWindow()
        
    def addWorldEmpty(self):
        response = simpledialog.askstring("World Name", f"Please specify a name for the new empty world.")
        if not response:
            return
        
        if response not in self.files.getFolderNames(self.files.worldsPath):
            self.files.backupWorld(self.files.current_world)
            self.files.deleteNitroxWorld()
            self.files.addWorld(response)
            self.files.current_world = response
            self.files.saveData()
        
            messagebox.showinfo("Added Empty World", "Empty world has been added. No conflicts. You have been switched to the world.")
        else:
            messagebox.showerror("Failed to Add Empty World", f"World \"{response}\" already exists. Please choose a different name.")
            
        # Reset Main Window
        self.mainWindow()
  
    def rollbackWorld(self):
        self.root_rollback = Tk()
        self.root_rollback.title("Rollback World")
        self.root_rollback.resizable(0, 0)
        self.root_rollback.geometry("350x170")
        self.root_rollback.update()
        
        # Create ui
        frame = Frame(self.root_rollback, pady=10)
        frame.pack()
        
        backupSelectLabel = Label(frame, text="Select a Backup to Rollback To.")
        backupSelectLabel.pack(pady = 10)
        
        selectOptions = self.files.getBackups(self.files.current_world)
        self.backupSelectValue = StringVar(self.root_rollback, "Select A Backup")
        backupSelect = OptionMenu(frame, self.backupSelectValue, *selectOptions, command=self.changeBackup)
        backupSelect.pack(pady = 10)
        
        cancelBtn = Button(frame, text="Cancel", command = lambda: self.root_rollback.destroy())
        cancelBtn.pack(pady = 10, fill = "x")
        
    def changeBackup(self, *args):
        # Ask them if they're sure.
        if (messagebox.askyesno(title = "Rollback World?", message = f"Are you certain you want to rollback your world to version {self.backupSelectValue.get()}? We will create a backup of the current state so you can undo this, but please refrain from proceeding if you are unsure.")):
            # They wish to proceed
            self.files.backupWorld(self.files.current_world)
            self.files.rollbackWorld(self.files.current_world, self.backupSelectValue.get())
            self.files.changeNitroxWorld(self.files.current_world)
            messagebox.showinfo(title = "World Rollback Successful", message = f"The world rollback has been successful. You are now on version {self.backupSelectValue.get()}")
            self.root_rollback.destroy()
        else:
            # Cancel
            self.backupSelectValue.set("Select A Backup")
    
if __name__ == '__main__':
    files = Files()
    gui = GUI(files)

    gui.root.mainloop()