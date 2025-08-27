# Based on Requirements

[UABEA](https://github.com/nesrak1/UABEA)

### **About the Tool: TBT Localization Editor**

The **TBT Localization Editor** is a specialized desktop application designed for editing localization files used in games, specifically those in a particular JSON format.this tool provides a user-friendly graphical interface (GUI) to view, edit, search, and manage translation texts without needing to directly manipulate the complex JSON file structure.

## Download tool

.

<img width="1113" height="765" alt="Screenshot_2025-08-21_00-38-07" src="https://github.com/user-attachments/assets/fe254bc2-bc3a-47d1-8556-b3122b9a0ceb" />

### **Python Requirements**

To run this tool, you will need:

1. *   **Python 3.x+**

2. *   *install the required library using pip:**
```sh
pip install tkinterdnd2
```
3.  **Valid JSON File:** The tool is designed to work with a specific JSON file structure. The file must contain a main object with a key named `m_TableData`, which in turn contains an `Array` of localization entries. Each entry in the array should be an object with keys like `m_Id` (the unique identifier) and `m_Localized` (the text to be translated).

### **How to Use the Tool**

1.  **Installation & Running:**
    *   Make sure you have Python installed.
    *   Install the required library using the `pip install tkinterdnd2` command.
    *   Run the script from your terminal: `python TBT-Localization.py`.

2.  **Opening a File:**
    *   **Method 1 (Menu):** Go to `File > Open...` (or press `Ctrl+O`) and select your TBT localization `.json` file.

3.  **Viewing and Editing Text:**
    *   Once a file is loaded, the main table will be populated with all the text entries.
    *   Click on any row in the table to select it.
    *   The full text of the selected entry will appear in the **"Full Text Editor"** box at the bottom.
    *   You can now edit the text in this box.
    *   After making your changes, click the **"Save Changes"** button next to the editor. This updates the text in the application's memory but does **not** save the file to your disk yet.

4.  **Searching and Replacing:**
    *   Use the **"Find"** and **"Replace"** fields in the top-right corner.
    *   **Find Next:** Enter text in the "Find" field and click "Find Next" to jump to the next entry containing that text. The search is case-insensitive.
    *   **Replace (in selected entry):** Select a row, then enter text in the "Find" and "Replace" fields. Clicking **"Replace"** will replace the *first* occurrence of the "Find" text with the "Replace" text *only within the text editor below*. You must still click "Save Changes" to apply it.
    *   **Replace All:** Enter text in both fields and click **"Replace All"**. This will find and replace *every* occurrence of the "Find" text in *all entries* throughout the entire file. A confirmation prompt will appear, as this action cannot be undone.

5.  **Saving Your Work:**
    *   **Save:** Go to `File > Save` (or press `Ctrl+S`) to overwrite the currently opened file with your changes.
    *   **Save As:** Go to `File > Save As...` (or press `Ctrl+Shift+S`) to save your changes to a new `.json` file.

6.  **Using the TXT Workflow (for Translators):**
    *   **Export:** Open your JSON file, then go to `File > Export to TXT...`. This will create a `.txt` file where each line corresponds to a translation entry. The text is enclosed in double quotes (`"`) to preserve formatting, and any internal quotes are escaped as `""`.
    *   **Translate:** Edit the exported `.txt` file using any plain text editor.
    *   **Import:** After the translation is done, open the original JSON file again in the tool. Go to `File > Import from TXT...` and select your edited `.txt` file. The tool will read each line and update the corresponding entry in the JSON data. If the number of lines doesn't match, the tool will warn you.
