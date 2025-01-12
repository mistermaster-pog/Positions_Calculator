# Positions Calculator

## Overview
Positions Calculator is a versatile tool designed for level creation and object placement in the game Colobot. It consists of three main components:

### 1. **Map Editor** (Core Functionality)
The Map Editor facilitates precise object placement and level customization. It replaces the manual and time-consuming process of recording positions in the game and editing the `scene.txt` file.

### 2. **Random Positions Generator** (Support Functionality)
Generates random object positions based on simple parameters. Output can be copied and directly pasted into the Map Editor’s output field for further customization.

### 3. **Space Ship Objects** (Support Functionality)
Calculates positions of objects placed on a spaceship. The results are immediately compatible with the Map Editor for seamless integration.

For both support functionalities, any changes to the output must be confirmed using the **Refresh** button to save them in memory.

---

## Features

### **Map Editor Features**
1. **Map Loading**
   - Load the terrain relief from a level.
   - Define and load water levels manually.
   - Import existing objects directly from a `scene.txt` file.

2. **Map Navigation**
   - View the current cursor position on the map.
   - Zoom in and out using the mouse wheel.
   - Drag the map by holding the middle mouse button.

3. **Object Management**
   - Place objects by selecting them from a searchable list or manually defining parameters.
   - Each object in the list includes a preview image for easy identification.
   - Support for multi-selection in the object list using **Ctrl** (individual objects) or **Shift** (blocks of objects).
   - Randomize or set specific direction (`dir`) for objects.

4. **Insect Mode**
   - Automatically adds additional parameters when placing alien creatures, such as:
     ```
     CreateObject pos=55;65 cmdline=75;55;30 dir=0.0 type=AlienAnt script1="antict.txt" run=1
     ```

5. **Delete Mode**
   - Remove objects by enabling **Delete Mode** and clicking on objects on the map.
   - Automatically updates object lists and output after deletion.

6. **Output Management**
   - Outputs object data in the following format:
     ```
     CreateObject pos=-3.25;-3.25 dir=1.5 type=WingedGrabber power=100
     ```
   - Manually edit output to:
     - Adjust positions.
     - Add or remove multiple entries.
     - Add additional parameters, e.g., `power=100` or `script1="charge2.txt"`.
   - Confirm edits by clicking the **Refresh** button. Any unconfirmed changes will be lost when adding or removing objects.

7. **Clear Map**
   - Clear all objects from the map with a single button.

8. **Copy Output**
   - Copy the output to the clipboard for easy pasting into the `scene.txt` file.

---

## Usage Instructions

1. **Start with the Map Editor:**
   - Load a terrain map and define water levels.
   - Import existing objects from a `scene.txt` file.

2. **Place Objects:**
   - Select objects from the list or use manual mode to define parameters.
   - Use **Insect Mode** for alien creatures to auto-generate required parameters.

3. **Manage Output:**
   - Confirm changes to the output using the **Refresh** button.
   - Copy the output and paste it into `scene.txt` once satisfied with all edits.

4. **Utilize Support Functions:**
   - Use the Random Positions Generator and Space Ship Objects tools as needed.
   - Paste their output into the Map Editor for integration.

5. **Save Your Work:**
   - Ensure all changes are reflected in the output before exiting the program.

---

## Example Workflow
1. Load the map and water levels.
2. Import existing objects.
3. Place new objects or modify existing ones:
   - Select objects from the list or enter details manually.
   - Use Delete Mode to remove unnecessary objects.
4. Edit the output to fine-tune parameters.
5. Click **Refresh** to save changes.
6. Copy the final output and paste it into `scene.txt`.

---

## Additional Notes
- Always confirm edits to the output using the **Refresh** button.
- Multi-selection in the object list allows for efficient object placement with random selection.
- Utilize the Clear Map button to start fresh if needed.

With Positions Calculator, creating and customizing levels in Colobot becomes an efficient and user-friendly experience!