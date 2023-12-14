import typing, customtkinter

#   Global variables
_artists:list[str]   =   []

#   Typed dicts
class Entry(typing.TypedDict):
    id:str
    text:str
    placeholder:str
    entry:customtkinter.CTkEntry

#   Classes


class ScrollableArtistFrame(customtkinter.CTkScrollableFrame): # TODO: Change checkboxes for CTkFrames
    """
    Class that represents a Scrollable frame where the artist names are contained
    """
    def __init__(self, master:customtkinter.CTk, title:str):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        global _artists
        self.artist_entries:list = []

        for i in range(len(_artists)):
            artist_entry = ArtistEntry(self, position=i, frame=self)
            artist_entry.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.artist_entries.append(artist_entry)
    
    def refresh(self):
        pass # TODO

class ArtistEntry(customtkinter.CTkFrame):
    """
    Class that contains the name of an artist, as well as
    several options to edit or remove it
    """
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 position:int,
                 frame:ScrollableArtistFrame,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        global _artists

        self.grid_columnconfigure((0,1,2), weight=1)
        self.grid_columnconfigure((3,4), weight=0)

        self.frame=frame
        self.position=position

        self.label = customtkinter.CTkLabel(self, text=_artists[self.position], fg_color="transparent", width=width*4, anchor="w")
        self.label.grid(row=0,column=0, padx=10, pady=0, sticky="w", columnspan=3)
        

        self.edit_button = customtkinter.CTkButton(self, text="⛭", command=self.edit, fg_color="transparent", width=height-6, height=height-6)
        self.edit_button.grid(row=0, column=3, padx=0, pady=0, sticky="e", columnspan=1)
        self.remove_button = customtkinter.CTkButton(self, text="❌", command=self.remove, fg_color="transparent", width=height-6, height=height-6)
        self.remove_button.grid(row=0, column=4, padx=0, pady=0, sticky="e", columnspan=1)
    
    def edit(self, new_artist:str) -> None:
        try:
            _artists[self.position] = str(new_artist)
            self.frame.refresh()
        except Exception as e:
            print(f"ERROR: {e}")

    def remove(self) -> None:
        try:
            del(_artists[self.position])
            self.frame.refresh()
        except Exception as e:
            print(f"ERROR: {e}")


class IntSpinbox(customtkinter.CTkFrame):
    """
    Class that defines the custom Spinbox that will be used to select
    the amount of tracks that are to be added to the playlist.
    """
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: int = 1,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "5")

    def add_button_callback(self):
        try:
            if int(self.entry.get())<10:
                value = int(self.entry.get()) + self.step_size
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
            else:
                self.entry.delete(0, "end")
                self.entry.insert(0, 10)
        except ValueError:
            return

    def subtract_button_callback(self):
        try:
            if int(self.entry.get())>1:
                value = int(self.entry.get()) - self.step_size
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
            else:
                self.entry.delete(0, "end")
                self.entry.insert(0, 1)
        except ValueError:
            return

    def get(self) -> typing.Union[int, None]:
        try:
            result=int(self.entry.get())
            if result>10:
                result = 10
            elif result<1:
                result = 1
            return result
        except ValueError:
            return None

    def set(self, value: int):
        if value<=10 and value>=0:
            self.entry.delete(0, "end")
            self.entry.insert(0, str(int(value)))

class AddArtistButton(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 button_callback:typing.Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        
        self.grid_columnconfigure((0,1,2),weight=1) # Lable expands
        self.grid_columnconfigure(3,weight=0) # Button does not expand

        self.label=customtkinter.CTkLabel(self, text="Add new artist:", fg_color="transparent")
        self.label.grid(row=0,column=0, padx=10, pady=0, sticky="wsn")
        self.entry=customtkinter.CTkEntry(self, placeholder_text="artist name")
        self.entry.grid(row=0, column=1,padx=10, pady=0, sticky="ew", columnspan=2)
        self.button=customtkinter.CTkButton(self, text="+", command=button_callback, width=height-6, height=height-6)
        self.button.grid(row=0,column=3, padx=10, pady=0, sticky="wesn")
    
    def get(self) -> typing.Union[str, None]:
        return str(self.entry.get())

class HelpWindow(customtkinter.CTkToplevel):
    """
    Pop-up window where extra information about the usage of the program can be consulted.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("420x520")
        self.maxsize(width=420, height=520)
        self.minsize(width=420, height=520)

        self.title("Information")

        self.header = customtkinter.CTkLabel(self, text="🛈 Information")
        self.header.pack(padx=20, pady=20)
        self.header.cget("font").configure(size=16, underline=True)

        self.description = customtkinter.CTkLabel(self, text=
"""1)\tIn order to get the value of your client_id and client_secret 
fields, just go to https://developer.spotify.com/, access your 
dashboard and register a new app (the app's redirect URI must be 
http://localhost:8080). Once that is done, go to your app's settings 
and copy your client_id and client_secret tokens

2)\tNote that your user_id may not be the same as your 
username, it is usually the original username under which 
the account was created.

3)\tIn the artist list you should specify the name of 
the artists you wish to see in your playlist. Note that the script 
uses whatever you input as an "artist name" in order to perform a 
normal spotify search, and will only add songs of the first artist 
that it finds, so be carefull with your spelling!

4)\tMode: Wether you want your generated playlist to 
be based solely on songs by the artists you selected, you want it 
solely based on recommendations or you want a mixture of both

5)\tNumber of tracks: the number of tracks of each 
artist to include (capped at 10). If you select the "recommendations"
or "both" mode, it also represents the number of recommended tracks
to be added into the playlist

© Álvaro de Castro (@Zempui), 2023""")
        self.description.pack(padx=0, pady=0)

class ProgressBar(customtkinter.CTkFrame):
    """
    Progress bar that reflects the status of the generation of the playlist
    """
    

    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 progress: float = 0.0,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.status:str = "Ready"
        self.progress:float = 0.0
        self.help_window = None

        self.grid_columnconfigure((1,2,3), weight=1)
        self.grid_columnconfigure((0,4), weight=0)

        self.label=customtkinter.CTkLabel(self, text=self.status, fg_color="transparent")
        self.label.grid(row=0,column=0, padx=10, pady=0, sticky="w")
        self.progressbar = customtkinter.CTkProgressBar(self, orientation="horizontal")
        self.progressbar.grid(row=0,column=1, padx=10, pady=0, sticky="we", columnspan=3)
        self.button=customtkinter.CTkButton(self, text="?", command=self.help_button_callback, width=height-6, height=height-6, corner_radius=100)
        self.button.grid(row=0,column=4, padx=10, pady=0, sticky="we")

        self.set_progress(progress)
        

    def help_button_callback(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self) 
        else:
            self.help_window.focus()

    def set_progress(self, progress: float):
        if float(progress)<=1.0 and float(progress)>=0.0:
            self.progress = float(progress)
            if self.progress==0.0:
                self.status="Ready"
            elif self.progress>0.0 and self.progress<1.0:
                self.status=f"{self.progress*100:3.2f} %"
            elif self.progress==1.0:
                self.status="Finished!"
        else:
            self.progress = 0.0
            self.status = "Error: Invalid Value"
        self.progressbar.set(self.progress)





class App(customtkinter.CTk):
    """
    Backbone class of the GUI
    """
    global _artists 
    _artists        = ["Lorem","ipsum","dolor","sit","amet","consectetur", "adipiscing","elit","Nullam","vitae","velit ac nisl","tempus fermentum"]
    _width:int      = 520
    _height:int     = 620

    def __init__(self) -> None :
        super().__init__()

        self.title("Spotify Playlist Generator")
        self.geometry(f"{self._width}x{self._height}")
        self.maxsize(width=self._width, height=self._height)
        self.minsize(width=self._width, height=self._height)

        self.grid_columnconfigure((0,2),weight=0)
        self.grid_columnconfigure((1,3), weight=2)
        self.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9), weight=2)

        self.label_title = customtkinter.CTkLabel(self, text="Spotify Playlist Generator", fg_color="transparent")
        self.label_title.grid(row=0,column=0, padx=10, pady=0, sticky="ew", columnspan=4)
        self.label_title.cget("font").configure(size=16, underline=True)

        self.progressbar = ProgressBar(self,progress=0.0)
        self.progressbar.grid(row=1,column=0, padx=10, pady=0, sticky="ew", columnspan=4)

        # Labels:Entries
        self.entries:list(Entry) = [
            {"id":"playlist_name", "text":"Playlist Name:", "placeholder":"name of the playlist"},
            {"id":"client_id", "text":"Client Id:", "placeholder":"client id"},
            {"id":"client_secret", "text":"Client Secret:", "placeholder":"client secret"},
            {"id":"user_id", "text":"User Id:", "placeholder":"user id"}]
        for i in range(len(self.entries)):
            customtkinter.CTkLabel(self, text=self.entries[i]["text"], 
                                   fg_color="transparent").grid(
                                       row=(i+2),column=0, padx=10, pady=0, sticky="w")
            self.entries[i]["entry"]=customtkinter.CTkEntry(self, placeholder_text=self.entries[i]["placeholder"])
            self.entries[i]["entry"].grid(row=(i+2), column=1,padx=10, pady=0, sticky="ew", columnspan=3)

        self.label_mode = customtkinter.CTkLabel(self, text="Mode:", fg_color="transparent")
        self.label_mode.grid(row=6,column=0, padx=10, pady=0, sticky="w")
        self.combobox_mode = customtkinter.CTkComboBox(self, values=["Tracks only", "Recommendations only", "Both"])
        self.combobox_mode.grid(row=6,column=1, padx=10, pady=0, sticky="we")
        self.label_n = customtkinter.CTkLabel(self, text="Number of Tracks:", fg_color="transparent")
        self.label_n.grid(row=6,column=2, padx=10, pady=0, sticky="w")
        self.spinbox_n=IntSpinbox(self)
        self.spinbox_n.grid(row=6,column=3, padx=10, pady=0, sticky="we")

        self.scrollable_checkbox_frame = ScrollableArtistFrame(self, title="Artists")
        self.scrollable_checkbox_frame.grid(row=7, column=0, padx=10, pady=(10, 0), sticky="nsew", columnspan=4)

        self.add_artist = AddArtistButton(self, button_callback=self.add_button_callback, fg_color="transparent")
        self.add_artist.grid(row=8, column=0, padx=10, pady=(10, 0), sticky="nsew", columnspan=3)

        self.generate_button = customtkinter.CTkButton(self, text="Generate", command=self.generate_button_callback)
        self.generate_button.grid(row=9, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        self.clear_button = customtkinter.CTkButton(self, text="Clear", command=self.clear_button_callback)
        self.clear_button.grid(row=9, column=2, padx=10, pady=10, sticky="ew", columnspan=2)

        

    def generate_button_callback(self) -> None :
        """
        Callback function that is executed when the 'generate' button is pressed.
        """
        playlist_name, client_id, client_secret, user_id = (
            str(self.entries[i]["entry"].get()) for i in range(4))
        mode:str = self.combobox_mode.get()
        n:int = self.spinbox_n.get()
        print(f"Playlist name:\t{playlist_name}\nClient Id:\t{client_id}\nClient Secret:\t{client_secret}\nUser Id:\t{user_id}\nMode:\t\t{mode}\nn:\t\t{n}\nArtistas:\t{_artists}")
        pass # TODO

    def clear_button_callback(self) -> None:
        """
        Callback function that clears the data that has been introduced
        """
        global _artists
        for i in range(4):
            self.entries[i]["entry"].delete(0,customtkinter.END)
        self.spinbox_n.set(5)
        _artists=[]
        pass # TODO

    def add_button_callback(self) -> None:
        """
        Callback function that adds a new artist to the list
        """
        pass # TODO

if __name__=="__main__":
    App().mainloop()