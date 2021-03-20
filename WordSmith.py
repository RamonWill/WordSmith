import tkinter as tk
from tkinter import messagebox
from views import DisclaimerPage, HelpPage, MainPage, NavBar

APP_HEIGHT = 600
APP_WIDTH = 1024


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WordSmith")
        main_frame = tk.Frame(self, height=APP_HEIGHT, width=APP_WIDTH)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        self.resizable(0, 0)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        # Add menu to the application
        menubar = NavBar(self)
        tk.Tk.config(self, menu=menubar)

        # add the frames to the application
        page = MainPage(parent=main_frame)
        page.place(rely=0, relx=0)
        page.tkraise()
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

    def OpenHelpPage(self):
        help = HelpPage()
        help.focus_set()
        help.grab_set()

    def OpenDisclaimerPage(self):
        disclaimer = DisclaimerPage()
        disclaimer.focus_set()
        disclaimer.grab_set()

    def quit_application(self):
        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
            self.destroy()
# parent is the parent frame that the object is tied to i.e. Frame(root)
# MainPage(main_frame) means MainPage is tied to the main_frame in application)


if __name__ == "__main__":
    root = Application()
    root.mainloop()
