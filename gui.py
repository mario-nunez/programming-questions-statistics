import tkinter as tk
from PIL import ImageTk, Image

class Gui(tk.Tk):
    """
    A class to represent a GUI app.
    """
    # Menu option constants
    LANG_OPTIONS_MAPPING = {"English": "", "Spanish": "es.",
                            "Portuguese": "pt."}
    PROG_LANG_OPTIONS = ["Python", "SQL", "Javascript", "C", "Java", "R",
                         "Scala"]
    # Design constants
    SO_IMG_SIZE = (200, 40)
    SUBMIT_IMG_SIZE = (25, 25)
    SUBMIT_COLOR = "#93EA75"
    FAMILY_FONT = "Helvetica"

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
        self.lang_options = list(self.LANG_OPTIONS_MAPPING.keys())

        # GUI properties
        self.title("Search GUI")
        self.geometry("350x350")
        self.resizable(False, False)
        self.iconbitmap("./images/search-icon.ico")

        # Options properties
        self.clicked_lang = tk.StringVar()
        self.clicked_prog_lang = tk.StringVar()

        # Store options selected
        self.search_lang = None
        self.search_prog_lang = None
        
        # Labels
        label_title1 = tk.Label(self, text="Get statistics of",
                                font=f"{self.FAMILY_FONT} 15")
        label_title2 = tk.Label(self, text="questions",
                                font=f"{self.FAMILY_FONT} 15")
        label_general = tk.Label(self, text="Select search options",
                                 font=f"{self.FAMILY_FONT} 13 underline")
        label_lang = tk.Label(self, text="- Select language:")
        label_prog_lang = tk.Label(self, text="- Select programming language:")
        label_new_line = lambda: tk.Label(self, text="\n") # allows label reuse

        # Add image
        img = ImageTk.PhotoImage(Image
            .open("./images/stackoverflow.png")
            .resize(self.SO_IMG_SIZE))
        img_label = tk.Label(self, image=img)
        img_label.image = img
        # Add button image
        submit_btn = ImageTk.PhotoImage(Image
            .open("./images/submit-icon.png")
            .resize(self.SUBMIT_IMG_SIZE))
        submit_btn.image = submit_btn

        # Drop down boxes
        self.clicked_lang.set(self.lang_options[0])
        drop_lang = tk.OptionMenu(self, self.clicked_lang, *self.lang_options)

        self.clicked_prog_lang.set(self.PROG_LANG_OPTIONS[0])
        drop_prog_lang = tk.OptionMenu(self, self.clicked_prog_lang,
                                       *self.PROG_LANG_OPTIONS)
        
        # Submit button
        submit_button = tk.Button(self, text="Submit", command=self.submit,
                                  bg=self.SUBMIT_COLOR, image=submit_btn,
                                  compound="left")
        
        # Display elements
        label_title1.pack()
        img_label.pack()
        label_title2.pack()
        label_new_line().pack()
        label_general.pack()
        label_lang.pack()
        drop_lang.pack()
        label_prog_lang.pack()
        drop_prog_lang.pack()
        label_new_line().pack()
        submit_button.pack()

    def submit(self):
        """
        Get the value of the selected options and close the GUI window
        automatically.
        """
        self.search_lang = self.LANG_OPTIONS_MAPPING[self.clicked_lang.get()]
        self.search_prog_lang = self.clicked_prog_lang.get()

        self.destroy()
        