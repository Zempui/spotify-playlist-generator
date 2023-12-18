import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import util
from typing import TypedDict
import typing, customtkinter

#   GLOBAL VARIABLES

_artists:list[str]   =   []

#   TYPED DICTS

class Arguments(TypedDict):
    client_id:str
    client_secret:str
    redirect_uri:str
    scope:str
    username:str

class Entry(typing.TypedDict):
    id:str
    text:str
    placeholder:str
    entry:customtkinter.CTkEntry

#   CLASSES

class ScrollableArtistFrame(customtkinter.CTkScrollableFrame):
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
        """
        Method that will refresh the values displayed in the artist list.\n
        The values of the new elements of the list are taken from the "_artists" global variable
        """
        for i in self.artist_entries:
            i.grid_remove()
        
        for i in range(len(_artists)):
            artist_entry = ArtistEntry(self, position=i, frame=self)
            artist_entry.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.artist_entries.append(artist_entry)
        
        self._scrollbar.set(0,0)

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
    
    def edit_artist_popup(self) -> typing.Union[str,None]:
        dialog = customtkinter.CTkInputDialog(text="Artist name:", title="Edit an entry")
        return dialog.get_input()

    def edit(self) -> None:
        try:
            new_artist:str = self.edit_artist_popup()
            if new_artist is not None:
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
            self.entry.insert(0, int(value))

class AddArtistButton(customtkinter.CTkFrame):
    def __init__(self, *args,
                 master:customtkinter.CTk,
                 width: int = 100,
                 height: int = 32,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        
        self.master:App=master
        self.grid_columnconfigure((0,1,2),weight=1) # Lable expands
        self.grid_columnconfigure(3,weight=0) # Button does not expand

        self.label=customtkinter.CTkLabel(self, text="Add new artist:", fg_color="transparent")
        self.label.grid(row=0,column=0, padx=10, pady=0, sticky="wsn")
        self.entry=customtkinter.CTkEntry(self, placeholder_text="artist name")
        self.entry.grid(row=0, column=1,padx=10, pady=0, sticky="ew", columnspan=2)
        self.button=customtkinter.CTkButton(self, text="+", command=self.add_button_callback, width=height-6, height=height-6)
        self.button.grid(row=0,column=3, padx=10, pady=0, sticky="wesn")
    
    def clear(self) -> None:
        """
        Function that clears the value in the Add Artist Entrybox
        """
        self.entry.delete(0, "end")

    def get(self) -> typing.Union[str, None]:
        result = str(self.entry.get())
        if result == "":
            result = None
        return result
    
    def add_button_callback(self) -> None:
        """
        Callback function that adds a new artist to the list
        """
        global _artists
        new_artist:typing.Union[str, None] = self.get()
        if new_artist is not None: #OK!
            self.clear()
            _artists.append(str(new_artist))
            self.master.scrollable_artist_frame.refresh()

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

class ErrorWindow(customtkinter.CTkToplevel):
    """
    Pop-up window where information about an error is presented.
    """
    def __init__(self, text:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width, self.height = 420, 125
        self.geometry(f"{self.width}x{self.height}")
        #self.maxsize(width=self.width, height=self.height)
        self.minsize(width=self.width, height=self.height)

        self.title("ERROR")

        self.header = customtkinter.CTkLabel(self, text="⚠ ERROR")
        self.header.pack(padx=20, pady=20)
        self.header.cget("font").configure(size=16)

        self.description = customtkinter.CTkLabel(self, text=text)
        self.description.pack(padx=0, pady=0)
    
    def edit_msg(self,text:str):
        try:
            if text is not None:
                self.description.configure(text=text)
        except Exception as e:
            print(f"ERROR: {e}")

class ProgressBar(customtkinter.CTkFrame):
    """
    Progress bar that reflects the status of the generation of the playlist
    """
    

    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 progress: float = 0.0,
                 master:customtkinter.CTk,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.status:str = "Ready"
        self.progress:float = 0.0
        self.help_window = None
        self.master=master

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
            elif self.progress>0.0 and self.progress<=1.0:
                self.status=f"{self.progress*100:3.2f} %"
        elif float(progress)==2.0:
            self.progress = float(progress)
            self.status="Finished!"
        else:
            self.progress = 0.0
            self.status = "Error: Invalid Value"
        self.progressbar.set(self.progress)
        self.label.configure(text=self.status)
        self.master.update_idletasks()

class App(customtkinter.CTk):
    """
    Backbone class of the GUI
    """
    global _artists 
    _artists        = []
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

        self.error_window:ErrorWindow = None

        self.label_title = customtkinter.CTkLabel(self, text="Spotify Playlist Generator", fg_color="transparent")
        self.label_title.grid(row=0,column=0, padx=10, pady=0, sticky="ew", columnspan=4)
        self.label_title.cget("font").configure(size=16, underline=True)

        self.progressbar = ProgressBar(self,progress=0.0, master=self)
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

        self.scrollable_artist_frame = ScrollableArtistFrame(self, title="Artists")
        self.scrollable_artist_frame.grid(row=7, column=0, padx=10, pady=(10, 0), sticky="nsew", columnspan=4)

        self.add_artist = AddArtistButton(self, master=self, fg_color="transparent")
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
        conversion_table:dict[str,str] = {"Tracks only":"songs","Recommendations only":"recommendations", "Both":"both"}
        mode:str = conversion_table[self.combobox_mode.get()]
        
        n:int = self.spinbox_n.get()
        print(f"Playlist name:\t{playlist_name}\nClient Id:\t{client_id}\nClient Secret:\t{client_secret}\nUser Id:\t{user_id}\nMode:\t\t{mode}\nn:\t\t{n}\nArtistas:\t{_artists}")
        
        args:Arguments = {"scope"           :   "user-library-read, user-library-modify, playlist-modify-public",
                          "client_id"       :   str(client_id),
                          "client_secret"   :   str(client_secret),
                          "redirect_uri"    :   "http://localhost:8080",
                          "username"        :   str(user_id)}
        
        error:set[bool, str] = (False,"")
        if(playlist_name!="" and 
            client_id!="" and 
            client_secret!="" and 
            user_id!="" and 
            mode!="" and 
            n!="" and
            _artists != [] and
            None not in [playlist_name,client_id,client_secret,user_id,mode,n]):

            track_list:list = []
            try:
                for artist in range(len(_artists)):
                    (tl_aux)=track_search(args=args, artist_name=_artists[artist], n=n, m=mode)
                    for i in tl_aux:
                        track_list.append(i)
                    self.progressbar.set_progress(float((artist+1)/len(_artists)))

                playlist_generate(args=args, track_list=track_list, name=playlist_name)
                self.progressbar.set_progress(float(2.0))
                print("Done!")
            except Exception as e:
                error = (True, f"An exception occurred: {e}\n")
        elif _artists==[]:
            error=(True,"The artist list is empty.\n")
        else:
            error=(True,"")
        

        if error[0]: #TODO: Adapt for incorrect parameters
            error_list:dict = {"missing":False, "Nan":False}
            # ERROR TYPES:
            #   missing: one or more parameters are missing
            #   NaN: the value introduced in "number of songs" is not a number
            error_msg:str=error[1]

            missing:set = set()
            for i,j in {"Playlist name":playlist_name,"Client ID":client_id,
                        "Client Secret":client_secret,"User ID":user_id,
                        "Mode":mode,"Number of songs (n)":n}.items():
                if j=="":
                    missing.add(i)
                    error_list["missing"] = True

            if n == None:
                error_list["Nan"]=True

            if error_list["missing"]:
                error_msg += "Missing parameters: "
                for param in missing:
                    error_msg += f"{param}, "
                error_msg = error_msg[:-2] + "\n"
            if error_list["Nan"]:
                error_msg += "Invalid value detected in 'Number of tracks'"
                

            if self.error_window is None or not self.error_window.winfo_exists():
                self.error_window = ErrorWindow(text=error_msg) 
            else:
                self.error_window.edit_msg(error_msg)
                self.error_window.focus()

    def clear_button_callback(self) -> None:
        """
        Callback function that clears the data that has been introduced
        """
        global _artists
        for i in range(4):
            self.entries[i]["entry"].delete(0,customtkinter.END)
        self.spinbox_n.set(5)
        _artists=[]
        self.scrollable_artist_frame.refresh()

#   FUNCTIONS

def divide_array(array:list, step:int) -> list:
    """
    Simple function that divides an array into smaller arrays of a given size
    """
    result:list = []
    for i in range(0,len(array),step):
        x=i
        result.append(array[x:x+step])
    return result

def track_search(args:Arguments, artist_name:str, n:int, m:str) -> tuple:
    """
    Function that searched for tracks by a certain artist, recommended based on a certain artist or both.
    It returns a tuple with a list of the tracks and a string containing all the songs that have been found,
    as well as the name of the artist that has been found.
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=args["client_id"], client_secret=args["client_secret"],redirect_uri=args["redirect_uri"],scope=args["scope"]))
    util.prompt_for_user_token(username=args["username"], scope=args["scope"], client_id=args["client_id"], client_secret=args["client_secret"], redirect_uri=args["redirect_uri"])
    
    track_list:list = []

    #print(f"searching for artist '{artist_name}'...\n")
    #print("Tracks found:")
    artist:dict = sp.search(q='artist:' + artist_name, type='artist')['artists']['items']
    search_result_1:dict={}
    search_result_2:dict={}

    if len(artist)>0:
        print("artist found\t: "+artist[0]['name'])
        if m == "songs" or m=="both":
            search_result_1 = sp.artist_top_tracks(artist[0]["uri"])
            for track in search_result_1['tracks'][:n]:
                print('track\t: %-30.30s\tid: %s' % (track['name'], track["id"]))
                track_list.append(track["id"])
        
        if m == "recommendations" or m == "both":
            search_result_2 = sp.recommendations(seed_artists=[artist[0]['id']], limit=n)  
            for track in search_result_2['tracks'][:n]:
                print('track\t: %-30.30s\tid: %s' % (track['name'], track["id"]))
                track_list.append(track["id"])              
        
        
        print()
    else:
        print(f"artist not found '{artist_name}' :(\n")
    return (track_list)

def add_tracks(args:Arguments, track_list:list, name:str) -> None:
    """
    Function that adds tracks to a given playlist with the selected name. It's used to bypass the limit of 100 tracks added at a time.
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=args["client_id"], client_secret=args["client_secret"],redirect_uri=args["redirect_uri"],scope=args["scope"]))
    util.prompt_for_user_token(username=args["username"], scope=args["scope"], client_id=args["client_id"], client_secret=args["client_secret"], redirect_uri=args["redirect_uri"])
    found:bool = False
    for playlist in sp.current_user_playlists()["items"]:
        if playlist["name"]==name and not found:

            sp.user_playlist_add_tracks(user=args["username"], tracks=track_list, playlist_id=playlist["id"])
            found = True
        elif playlist["name"]==name and found:
            break

def playlist_generate(args:Arguments, track_list:list, name:str) -> None:
    """
    Function that generates a playlist with a given track list
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=args["client_id"], client_secret=args["client_secret"],redirect_uri=args["redirect_uri"],scope=args["scope"]))
    util.prompt_for_user_token(username=args["username"], scope=args["scope"], client_id=args["client_id"], client_secret=args["client_secret"], redirect_uri=args["redirect_uri"])
    
    description = f"""An automatically generated 🤖 playlist. ⚙️ Generated using Zempui's playlist generator"""
    
    sp.user_playlist_create(user=args["username"], name=name, public=True, description=description)


    found:bool = False
    for playlist in sp.current_user_playlists()["items"]:
        if playlist["name"]==name and not found:
            for tl in divide_array(track_list, 80): # To surpass the limitation of 100 tracks per request
                add_tracks(args=args,track_list=tl, name=name)
            found = True
        elif playlist["name"]==name and found:
            # In case of there being more than one playlist with the same name, the tracks will only be added to the latest."
            break


        
        
        

if __name__=="__main__":
    App().mainloop()