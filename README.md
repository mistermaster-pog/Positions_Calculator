## Positions Calculator Summary 

The Positions Calculator is a tool designed for creating custom levels in **Colobot**. It offers a combination of manual and automated features that simplify the process of designing and organizing objects within various environments.  

---

### Key Features  

#### **Map Editor**  
The Map Editor is the central component, offering a rich set of features for detailed level design:  
- **Relief Loading**: Import any terrain relief as the base for your map.  
- **Water Level Loading**: Define water levels to enhance environmental realism.  
- **Zoom and Pan**: Easily navigate maps of any size with intuitive zooming and panning.  
- **'Insect Mode'**: Quickly place pre-defined alien creatures, such as ants and spiders, for instant integration into the scene.  
- **Full Object List**: Browse a detailed list of objects, each with preview images for easier identification.  
- **Search Functionality**: Locate specific objects swiftly using the search bar.  
- **Manual Mode**: Define custom object names and parameters manually, including attributes like `power=100`. This mode also supports setting or randomizing the `dir` (orientation) parameter for each object.  

#### **Random Object Generation**  
This feature allows users to populate a specific area with random objects by defining:  
- **Object Names**: Specify which objects to generate.  
- **Radius**: Set the area within which objects can spawn.  
- **No-Spawn Radius**: Define areas where objects should not spawn.  
- **Object Count**: Choose how many objects to generate.  

The tool includes multiple randomization algorithms to provide diverse and natural-looking arrangements, tailored to your level design needs.  

#### **Spaceship Object Placement Tool**  
This specialized program is designed for positioning objects within spaceships:  
- **Input**: Provide the spaceship's position and orientation (`dir`).  
- **Customizable Loadout**: Select which robots and items will be placed inside the spaceship.  
- **Output**: The tool calculates and generates precise positions for all objects, ensuring logical and consistent placement.  

#### **Export Functionality**  
All placements can be exported into a `scene.txt` file, ready for seamless integration into your **Colobot** levels.  

The Positions Calculator streamlines the creation of custom levels, offering precision, efficiency, and flexibility for Colobot enthusiasts and level designers alike.

---

### How to Export to .exe:
If you've made changes to the code and now want to export your project to a standalone `.exe` file, you can use the provided `build.bat` script:
1. Place the `build.bat` file in the **Positions Calculator** root folder.
2. Run `build.bat` to generate the `.exe` file. The export will create the executable in the `Positions Calculator/release/dist` folder.
3. Copy the `.exe` file from the `release/dist` folder and place it in the root folder of **Positions Calculator**.
4. Once the `.exe` is in the root folder, you can run it directly from there.

---

### How to Resolve Antivirus Blocking Issues with `build.bat` or `pyinstaller`

If your antivirus software flags the `build.bat` script or `pyinstaller` as a potential threat, follow these steps to fix the issue:

#### **Step 1: Add the `Positions Calculator` Folder to Antivirus Exceptions**
1. Open your antivirus software's settings.  
2. Look for a section called *Exclusions*, *Exceptions*, or *Whitelist*.  
3. Add the full path to the `Positions Calculator` folder as an exception.  
   - Example path: `C:\Users\YourUsername\Documents\Positions Calculator`  
4. Save the changes and try running `build.bat` again.  

#### **Step 2: Run the Script as Administrator**
1. Right-click on the `build.bat` file.  
2. Select **Run as Administrator**.  
3. Confirm any prompts for elevated permissions.  

This ensures the script has the required privileges to execute properly. 
