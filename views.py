import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from controller import Controller


# This is our menu
class NavBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)

        # File
        menu_file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(label="How to use WordSmith", command=parent.OpenHelpPage)
        menu_file.add_command(label="Disclaimer", command=parent.OpenDisclaimerPage)
        menu_file.add_separator()
        menu_file.add_command(label="Exit",
                              command=parent.quit_application)


class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        MAIN_FONT = ("Yu Gothic UI", 9, "bold")

        frame_styles = {"relief": "groove",
                        "bd": 3,
                        "fg": "#073bb3", "font": MAIN_FONT}
        self.controller = Controller(view=self)

        label_header = tk.Label(parent, text="WordSmith", font=("Verdana Pro Cond Black", 25))
        label_header.place(rely=0.03, relx=0.02)
        label_author = tk.Label(parent, text="by Ramon Williams", font=MAIN_FONT)
        label_author.place(rely=0.07, relx=0.20)

        label_dict_title = tk.Label(parent, text="Select your dictionary list", font=MAIN_FONT)
        label_dict_title.place(rely=0.12, relx=0.02)
        self.label_dict_file = tk.Label(parent, relief="ridge", anchor="w")
        self.label_dict_file.place(rely=0.15, relx=0.02, height=23, width=375)
        btn_dict_file = ttk.Button(parent, text="Browse...", command=self._set_dictionary_list)
        btn_dict_file.place(rely=0.15, relx=0.40)

        label_extract_title = tk.Label(parent, text="Select a path where cracked files will be extracted to", font=MAIN_FONT)
        label_extract_title.place(rely=0.22, relx=0.02)
        self.label_extract_dest = tk.Label(parent, relief="ridge", anchor="w")
        self.label_extract_dest.place(rely=0.25, relx=0.02, height=23, width=375)
        btn_extract_dest = ttk.Button(parent, text="Browse...", command=self._set_extract_path)
        btn_extract_dest.place(rely=0.25, relx=0.40)

        frame_targets = tk.LabelFrame(parent, frame_styles, text="Targets")
        frame_targets.place(rely=0.32, relx=0.02, height=300, width=470)
        btn_add_file = ttk.Button(parent, text="Add a File...", command=self._add_target_file_tv)
        btn_add_file.place(rely=0.84, relx=0.02)
        btn_add_folder = ttk.Button(parent, text="Add a Folder...", command=self._add_target_folder_tv)
        btn_add_folder.place(rely=0.84, relx=0.10)
        self.include_subfolders = tk.BooleanVar(parent)
        ckbtn_subfolders = tk.Checkbutton(parent, variable=self.include_subfolders)
        ckbtn_subfolders.place(rely=0.84, relx=0.20)
        label_subfolders = tk.Label(parent, text="Include Subfolders?", font=MAIN_FONT)

        label_subfolders.place(rely=0.84, relx=0.23)

        hash_types = ("Plain", "MD5")
        self.hash = tk.StringVar(parent)
        opt_menu_hash = ttk.OptionMenu(parent, self.hash, hash_types[0],
                                       *hash_types)
        opt_menu_hash.place(rely=0.90, relx=0.27)

        btn_launch_attack = ttk.Button(parent, text="Launch Dictionary Attack!", command=self._launch_dictionary_attack)
        btn_launch_attack.place(rely=0.90, relx=0.12)

        frame_current_target = tk.LabelFrame(parent, frame_styles, text="Current Target")
        frame_current_target.place(rely=0.05, relx=0.50, height=50, width=500)
        self.label_current_target = tk.Label(frame_current_target, text="---------")
        self.label_current_target.pack(side="left")

        # TEXT BOX WIDGET
        frame_output = tk.LabelFrame(parent, frame_styles, text="Attack Output")
        frame_output.place(rely=0.15, relx=0.50, height=475, width=500)

        self.text_output = tk.Text(frame_output,wrap=tk.NONE)
        self.text_output.place(relheight=1, relwidth=1)
        text_scrolly = tk.Scrollbar(frame_output, orient="vertical", command=self.text_output.yview)
        text_scrollx = tk.Scrollbar(frame_output, orient="horizontal", command=self.text_output.xview)
        self.text_output.configure(yscrollcommand=text_scrolly.set, xscrollcommand=text_scrollx.set)
        text_scrolly.pack(side="right", fill="y")
        text_scrollx.pack(side="bottom", fill="x")

        # TREEVIEW WIDGET
        self.tv_target = ttk.Treeview(frame_targets)
        self.tv_target.place(relheight=1, relwidth=1)
        tv_scrolly = tk.Scrollbar(frame_targets, orient="vertical", command=self.tv_target.yview)
        tv_scrollx = tk.Scrollbar(frame_targets, orient="horizontal", command=self.tv_target.xview)
        self.tv_target.configure(yscrollcommand=tv_scrolly.set, xscrollcommand=tv_scrollx.set)
        tv_scrolly.pack(side="right", fill="y")
        tv_scrollx.pack(side="bottom", fill="x")
        self.tv_target["columns"] = ["Type", "Include SubFolders", "Target Path"]
        self.tv_target["show"] = "headings"  # removes empty column
        for col in self.tv_target["columns"]:
            self.tv_target.heading(col, text=col)
            col_width = 110
            if col == "Target Path":
                col_width = 300
            self.tv_target.column(col, width=col_width)
        # when you double click the treeview item it will delete the row
        self.tv_target.bind("<Double-1>", self._delete_tv_row)

    def _windows_dialog(self, is_folder=False, only_text=False):
        selection = None
        if is_folder:
            selection = filedialog.askdirectory()
        else:
            type1 = ("All Files", "*.*") if not only_text else ("Text Files", "*.txt")
            selection = filedialog.askopenfilename(initialdir="/",
                                                   title="Select a File",
                                                   filetype=[type1])
        return selection

    def _set_dictionary_list(self):
        selection = self._windows_dialog(only_text=True)
        self.label_dict_file["text"] = selection

    def _set_extract_path(self):
        selection = self._windows_dialog(is_folder=True)
        self.label_extract_dest["text"] = selection

    def _add_target_file_tv(self):
        path = self._windows_dialog()
        if not path:
            return None
        row = ["File", "False", path]
        self.tv_target.insert("", "end", values=row)

    def _add_target_folder_tv(self):
        path = self._windows_dialog(is_folder=True)
        if not path:
            return None
        seek_subfolders = self.include_subfolders.get()
        row = ["Folder", str(seek_subfolders), path]
        self.tv_target.insert("", "end", values=row)

    def _delete_tv_row(self, event):
        row = self.tv_target.selection()
        if row:
            self.tv_target.delete(row[0])

    def insert_text_message(self, message, update_idle=False):
        self.text_output.insert("end", f"{message}\n")
        self.text_output.see("end")
        if update_idle:
            self.text_output.update_idletasks()  # prevents gui freezing

    def display_messagebox(self, message, type="showinfo"):
        if type == "showerror":
            messagebox.showerror(title="Error", message=message)
        else:
            messagebox.showinfo(title="Information", message=message)

    def clear_text_output(self):
        self.text_output.delete('1.0', "end")

    def set_current_target(self, current_target):
        self.label_current_target["text"] = current_target

    def _launch_dictionary_attack(self):
        password_hash_type = "Plain Text"  # self.hash.get()
        password_file = self.label_dict_file["text"]
        save_dest = self.label_extract_dest["text"]

        if not password_file or not save_dest:
            msg = "You need to provide a password file and save destination"
            self.display_messagebox(msg, type="showinfo")
            return None

        all_targets = []
        for row_id in self.tv_target.get_children():
            target_info = self.tv_target.item(row_id, "values")
            all_targets.append(target_info)
        # raise message box if there are no targets
        if not all_targets:
            self.display_messagebox("There are no targets", type="showinfo")
        else:
            self.controller.launch_attack(password_file=password_file,
                                          save_destination=save_dest,
                                          hash_type=password_hash_type,
                                          targets=all_targets)


class BaseWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.base_frame = tk.Frame(self)
        self.base_frame.pack_propagate(0)
        self.base_frame.pack(fill="both", expand="true")
        self.fonts = ("Trebuchet MS", 9)
        self.geometry("600x200")
        self.resizable(0, 0)


class HelpPage(BaseWindow):
    def __init__(self):
        super().__init__()

        self.title("How to Use WordSmith")
        bio = (
            "Step 1: Select a file containing a list of passwords.\n"
            "Step 2: Select a Folder where you would like to extracted files "
            "to be saved.\n"
            "Step 3: Add File and/or Folders to the Targets list.\n"
            "Step 4: Choose whether you want to launch a plain text attack or "
            "MD5 attack.\n"
            "Step 5: Launch Attack >:)\n\n"
            "Note: Once finished passwords and file paths will be saved to "
            "the destination you originally chose.\n"
            "Remember to have fun and don't use this for malicious purposes.\n"
            "Created by Ramon Williams.   "
            "Github Account: https://github.com/RamonWill"
        )
        frame_about = tk.LabelFrame(self.base_frame, text="About WordSmith")
        frame_about.pack(expand=True, fill="both")
        label_about = tk.Label(frame_about, text=bio, font=self.fonts)
        label_about.pack(expand=True)


class DisclaimerPage(BaseWindow):
    def __init__(self):
        super().__init__()
        self.title("Disclaimer")
        summary = (
            "DO NOT USE THIS FOR MALICIOUS PURPOSES\n"
            "i.e. Stealing the password belonging to a person, animal, alien, "
            "flora or business/corporation is illegal\n"
            "This is a toy project for educational purposes"
        )
        frame_disc = tk.LabelFrame(self.base_frame, text="WordSmith Disclaimer")
        frame_disc.pack(expand=True, fill="both")
        label_disc = tk.Label(frame_disc, text=summary, font=self.fonts)
        label_disc.pack(expand=True)
