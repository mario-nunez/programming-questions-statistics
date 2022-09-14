import tkinter as tk

class Gui(tk.Tk):
    """
    A class to represent a GUI app.
    """

    LANG_OPTIONS_MAP = { 
        "English": "",
        "Spanish": "es",
        "Portuguese": "pt"
    }
    PROG_LANG_OPTIONS = [
        "Python", "SQL", "Javascript", "C", "Java", "R", "Scala"
    ]

    def __init__(self):
        """
        Constructs all the necessary attributes for the GUI app object.

        Attributes
        ----------
        search_lang : str
            language selected by the user
        search_prog_lang : str
            programming language selected by the user
        """
        super().__init__()
        self.lang_options = list(self.LANG_OPTIONS_MAP.keys())

        # GUI properties
        self.title("Search GUI")
        self.geometry("300x300")
        self.resizable(False, False)
        self.iconbitmap('./images/search_icon.ico')

        # Options properties
        self.clicked_lang = tk.StringVar()
        self.clicked_prog_lang = tk.StringVar()

        # Store options selected
        self.search_lang = None
        self.search_prog_lang = None
        
        # Labels
        label_title = tk.Label(self, text="Stack Overflow statistics.", font="bold")
        label_general = tk.Label(self, text="Select search options", font="bold")
        label_lang = tk.Label(self, text="Select language:")
        label_prog_lang = tk.Label(self, text="Select programming language:")
        label_new_line = tk.Label(self, text="\n")

        # Drop down boxes
        self.clicked_lang.set(self.lang_options[0])
        drop_lang = tk.OptionMenu(
            self,
            self.clicked_lang,
            *self.lang_options)

        self.clicked_prog_lang.set(self.PROG_LANG_OPTIONS[0])
        drop_prog_lang = tk.OptionMenu(
            self,
            self.clicked_prog_lang,
            *self.PROG_LANG_OPTIONS)
        
        # Submit button
        submit_button = tk.Button(self, text="Submit", command=self.submit)
        
        # Display elements
        label_general.pack()
        label_lang.pack()
        drop_lang.pack()
        label_prog_lang.pack()
        drop_prog_lang.pack()
        label_new_line.pack()
        submit_button.pack()

    def submit(self):
        """
        Get the value of the selected options and close the GUI window
        automatically.
        """
        self.search_lang = self.LANG_OPTIONS_MAP[self.clicked_lang.get()]
        self.search_prog_lang = self.clicked_prog_lang.get()

        # Close automatically the gui after storing the selected options
        self.destroy()
        