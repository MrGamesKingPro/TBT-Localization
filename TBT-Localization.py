import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
# To use the drag and drop feature, this library must be installed:
# pip install tkinterdnd2
import tkinterdnd2
import re

# We inherit from tkinterdnd2.TkinterDnD.Tk to get the best drag and drop functionality.
class TBTLocalizationEditor(tkinterdnd2.TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        # --- Main Window Settings ---
        self.title("TBT Localization Editor (By MrGamesKingPro)")
        self.geometry("1100x700")

        # --- Application State Variables ---
        self.data = None  # Holds the entire loaded JSON data structure.
        self.current_filepath = None  # Stores the path of the currently open file.
        self.id_to_tree_item = {}  # Dictionary to quickly find an item in the Treeview by m_Id key.
        self.id_to_original_index = {} # Links the m_Id key to its original order in the JSON array.
        self.terms_list_ref = None  # Direct reference to the list of terms in the loaded JSON.
        
        # Variable to store the key of the term currently being edited in the text widget.
        self.currently_editing_id = None
        
        # --- Build the User Interface ---
        self._create_widgets()
        
        # Register the main window as a drop target for files.
        self.drop_target_register('DND_FILES')
        self.dnd_bind('<<Drop>>', self.on_drop)

    def _create_widgets(self):
        # --- Top Menu Bar ---
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file_dialog, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export to TXT...", command=self.export_to_txt)
        file_menu.add_command(label="Import from TXT...", command=self.import_from_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # --- Top Toolbar Frame (for Search and Replace) ---
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)
        
        # --- Search and Replace Frame (aligned to the right) ---
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Find:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(search_frame, text="Find Next", command=self.find_next).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(search_frame, text="Replace:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.replace_entry = ttk.Entry(search_frame, width=25)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(search_frame, text="Replace", command=self.replace_selected).grid(row=1, column=2, padx=5, pady=2)
        ttk.Button(search_frame, text="Replace All", command=self.replace_all).grid(row=1, column=3, padx=5, pady=2)

        # Use PanedWindow to create a resizable divider between the table and the editor.
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 10))

        # --- Top Frame for Treeview (list of terms) ---
        tree_frame = ttk.Frame(main_pane, padding=(0, 10, 0, 0))
        main_pane.add(tree_frame, weight=3) # Give the table more space by default.
        
        columns = ("#", "id", "text")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("#", text="No.")
        self.tree.heading("id", text="ID")
        self.tree.heading("text", text="Localized Text (Preview)")
        
        self.tree.column("#", width=50, anchor='center')
        self.tree.column("id", width=250)
        self.tree.column("text", width=700)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Bind the selection event to update the text editor below.
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Bottom Frame for the Full Text Editor ---
        editor_frame = ttk.LabelFrame(main_pane, text="Full Text Editor", padding="10")
        main_pane.add(editor_frame, weight=1) # Give the editor less space by default.

        self.editor_text = tk.Text(editor_frame, wrap="word", height=10, width=80, undo=True)
        self.editor_text.pack(expand=True, fill="both", side="left", padx=(0, 10))
        self.editor_text.config(state="disabled") # Disable until an item is selected.

        editor_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.editor_text.yview)
        self.editor_text.configure(yscrollcommand=editor_scrollbar.set)
        editor_scrollbar.pack(side="left", fill="y")
        
        self.save_button = ttk.Button(editor_frame, text="Save Changes", command=self.save_from_editor, state="disabled")
        self.save_button.pack(pady=10, anchor="n")

        # --- Bottom Status Bar ---
        self.status_bar = ttk.Label(self, text="Open a TBT Localization JSON file to begin, or drag & drop a file here.", relief=tk.SUNKEN, anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- Bind Keyboard Shortcuts ---
        self.bind("<Control-o>", lambda event: self.open_file_dialog())
        self.bind("<Control-s>", lambda event: self.save_file())
        self.bind("<Control-S>", lambda event: self.save_file_as())

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            self.editor_text.config(state="normal")
            self.editor_text.delete("1.0", "end")
            self.editor_text.config(state="disabled")
            self.save_button.config(state="disabled")
            self.currently_editing_id = None
            return

        item_id = selected_items[0]
        item_values = self.tree.item(item_id, "values")
        term_id = item_values[1]
        
        original_index = self.id_to_original_index.get(term_id)
        if original_index is None: return

        try:
            full_text = self.terms_list_ref[original_index]['m_Localized']
        except (KeyError, IndexError):
            full_text = ""

        self.editor_text.config(state="normal")
        self.editor_text.delete("1.0", "end")
        self.editor_text.insert("1.0", full_text)
        self.save_button.config(state="normal")
        self.currently_editing_id = term_id

    def save_from_editor(self):
        if not self.currently_editing_id: return
        
        new_text = self.editor_text.get("1.0", "end-1c")
        self.update_data_and_tree(self.currently_editing_id, new_text)
        self.status_bar.config(text=f"Saved changes for ID: {self.currently_editing_id}")

    def on_drop(self, event):
        try:
            filepath = self.tk.splitlist(event.data)[0]
            if filepath.startswith('{') and filepath.endswith('}'):
                filepath = filepath[1:-1]
            
            self.load_file_logic(filepath)
        except Exception as e:
            messagebox.showerror("Drag & Drop Error", f"Could not open the dropped file.\n\nError: {e}")
            self.status_bar.config(text="Drag & drop failed.")

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Open TBT Localization JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath: return
        self.load_file_logic(filepath)

    def load_file_logic(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Search for the main data array.
            if 'm_TableData' in self.data and isinstance(self.data.get('m_TableData'), dict):
                self.terms_list_ref = self.data['m_TableData'].get('Array')
            else:
                self.terms_list_ref = None

            if self.terms_list_ref is None:
                raise ValueError("Invalid file structure. Could not find 'm_TableData' -> 'Array'.")

            self.current_filepath = filepath
            
            self.populate_treeview()
            self.title(f"TBT Localization Editor (By MrGamesKingPro) - {filepath.split('/')[-1]}")
            self.status_bar.config(text=f"File loaded: {filepath}")

        except (json.JSONDecodeError, ValueError, KeyError, FileNotFoundError) as e:
            messagebox.showerror("Error", f"Failed to open or parse file: {e}\n\nPlease make sure it's a valid TBT Localization JSON file.")
            self.data = None
            self.current_filepath = None
            self.terms_list_ref = None
            self.tree.delete(*self.tree.get_children())

    def populate_treeview(self):
        if not self.data or not self.terms_list_ref: return
        self.tree.delete(*self.tree.get_children())
        self.id_to_tree_item.clear()
        self.id_to_original_index.clear()
        
        self.on_tree_select(None) # Clear and disable the editor

        for i, term_data in enumerate(self.terms_list_ref):
            # Use m_Id as a unique key
            term_id = str(term_data.get('m_Id', '[NO ID]'))
            full_translation = term_data.get('m_Localized', '[NO TEXT]')
            
            display_translation = full_translation.replace('\n', ' ').replace('\r', ' ').strip()
            
            item_id = self.tree.insert("", "end", values=(i + 1, term_id, display_translation))
            self.id_to_tree_item[term_id] = item_id
            self.id_to_original_index[term_id] = i

    def update_data_and_tree(self, term_id, new_text):
        if not self.data or not self.terms_list_ref: return
        
        original_index = self.id_to_original_index.get(term_id)
        if original_index is None: return

        # Update the data in memory (the main JSON dictionary).
        self.terms_list_ref[original_index]['m_Localized'] = new_text

        # Also update the preview value in the Treeview.
        item_id = self.id_to_tree_item[term_id]
        current_values = list(self.tree.item(item_id, "values"))
        current_values[2] = new_text.replace('\n', ' ').replace('\r', ' ').strip()
        self.tree.item(item_id, values=tuple(current_values))
        
        self.status_bar.config(text=f"Updated ID: {term_id}")

    def save_file(self):
        if not self.current_filepath:
            self.save_file_as()
        else:
            self._write_to_file(self.current_filepath)

    def save_file_as(self):
        initial_filename = "Localization_en.json"
        if self.current_filepath:
            initial_filename = self.current_filepath.split('/')[-1]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=initial_filename
        )
        if not filepath: return
        self.current_filepath = filepath
        self._write_to_file(filepath)
        self.title(f"TBT Localization Editor - {filepath.split('/')[-1]}")

    def _write_to_file(self, filepath):
        if not self.data:
            messagebox.showwarning("No Data", "There is no data to save.")
            return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Preserve the original file format as much as possible
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            self.status_bar.config(text=f"File saved successfully: {filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")
            self.status_bar.config(text=f"Error saving file: {e}")

    def export_to_txt(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please open a file first before exporting.")
            return
        filepath = filedialog.asksaveasfilename(
            title="Export translations to TXT", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for item_id in self.tree.get_children():
                    term_id = self.tree.item(item_id, "values")[1]
                    original_index = self.id_to_original_index[term_id]
                    full_text = self.terms_list_ref[original_index]['m_Localized']
                    
                    # *** Start of modification ***
                    # 1. Replace \n with \\n to keep it as text.
                    # 2. Replace " with "" to escape quotes.
                    processed_text = full_text.replace('\n', '\\n').replace('"', '""')
                    # *** End of modification ***

                    # Wrap the entire string in quotes.
                    quoted_text = f'"{processed_text}"'
                    f.write(quoted_text + '\n')

            self.status_bar.config(text=f"Successfully exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export file: {e}")
    
    def import_from_txt(self):
        if not self.data:
            messagebox.showwarning("No Data", "Please open a file first before importing.")
            return
        filepath = filedialog.askopenfilename(
            title="Import translations from TXT", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            tree_items = self.tree.get_children()
            
            if len(lines) != len(tree_items):
                msg = (f"The number of lines in the text file ({len(lines)}) does not match "
                       f"the number of terms in the table ({len(tree_items)}).\n\n"
                       "Do you want to proceed and import matching lines only?")
                if not messagebox.askyesno("Line Count Mismatch", msg): return
            
            count = 0
            for item_id, new_line in zip(tree_items, lines):
                term_id = self.tree.item(item_id, "values")[1]
                
                processed_line = new_line.rstrip('\n\r')
                if processed_line.startswith('"') and processed_line.endswith('"'):
                    new_text = processed_line[1:-1].replace('""', '"')
                else:
                    new_text = processed_line
                
                self.update_data_and_tree(term_id, new_text)
                count += 1
            
            selected = self.tree.selection()
            if selected:
                self.on_tree_select(None)
                self.tree.selection_set(selected)

            self.status_bar.config(text=f"Successfully imported {count} lines from {filepath}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import file: {e}")

    def find_next(self):
        query = self.search_entry.get()
        if not query: return
        
        all_items = self.tree.get_children()
        if not all_items: return

        selected_item = self.tree.focus()
        start_index = 0
        if selected_item:
            start_index = self.tree.index(selected_item) + 1

        items_to_search = all_items[start_index:] + all_items[:start_index]

        for item in items_to_search:
            term_id = self.tree.item(item, "values")[1]
            original_index = self.id_to_original_index[term_id]
            full_text = self.terms_list_ref[original_index]['m_Localized']

            if query.lower() in full_text.lower():
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                self.status_bar.config(text=f"Found '{query}'")
                return
        
        self.status_bar.config(text=f"No more occurrences of '{query}' found.")
        messagebox.showinfo("Search Finished", f"No more occurrences of '{query}' were found.")

    def replace_selected(self):
        if not self.tree.focus():
            messagebox.showinfo("Info", "Please select a row to replace.")
            return

        query = self.search_entry.get()
        replace_with = self.replace_entry.get()
        
        if not query or self.editor_text.cget("state") == "disabled": return

        current_text = self.editor_text.get("1.0", "end-1c")
        new_text, count = re.subn(re.escape(query), replace_with, current_text, count=1, flags=re.IGNORECASE)
        
        if count > 0:
            self.editor_text.delete("1.0", "end")
            self.editor_text.insert("1.0", new_text)
            self.status_bar.config(text="Replaced text in editor. Click 'Save Changes' to commit.")
        else:
            self.status_bar.config(text="Search text not found in the editor for the selected row.")

    def replace_all(self):
        query = self.search_entry.get()
        replace_with = self.replace_entry.get()
        if not query:
            messagebox.showinfo("Info", "Please enter a search term in the 'Find' box.")
            return
            
        if not messagebox.askyesno("Confirm Replace All", f"Are you sure you want to replace all occurrences of '{query}' with '{replace_with}'? This cannot be undone."):
            return

        count = 0
        for item_id in self.tree.get_children():
            term_id = self.tree.item(item_id, "values")[1]
            
            original_index = self.id_to_original_index[term_id]
            old_text = self.terms_list_ref[original_index]['m_Localized']

            new_text, num_replacements = re.subn(re.escape(query), replace_with, old_text, flags=re.IGNORECASE)

            if num_replacements > 0:
                self.update_data_and_tree(term_id, new_text)
                count += num_replacements
        
        if self.currently_editing_id:
            selected = self.tree.selection()
            if selected:
                self.on_tree_select(None)
                self.tree.selection_set(selected)

        self.status_bar.config(text=f"Replaced {count} occurrence(s) in total.")
        messagebox.showinfo("Replace All", f"Finished. Replaced {count} occurrence(s).")


if __name__ == "__main__":
    app = TBTLocalizationEditor()
    app.mainloop()
