from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import util
import argparse
from tqdm import tqdm
from typing import TypedDict


class Arguments(TypedDict):
    client_id:str
    client_secret:str
    redirect_uri:str
    scope:str
    username:str

def divide_array(array:list, step:int) -> list:
    """
    Simple function that divides an array into smaller arrays of a given size
    """
    result:list = []
    for i in range(0,len(array),step):
        x=i
        result.append(array[x:x+step])
    return result

def getArgs() -> dict:
    """
    Function that parses the arguments provided in the command line when invoquing the script.
    Supported arguments:
        -n, --number    ->  the number of tracks of each artist to include (capped at 10)
        -m, --mode      ->  wether you want your generated playlist to be based solely on songs by the 
                            artists you selected, you want it solely based on recommendations or you 
                            want a mixture of both
    """
    n:int = 10
    m:str = "songs"

    parser = argparse.ArgumentParser(description="A tool to generate playlists containing the 'n' most popular tracks of several artists (default = 10)")
    parser.add_argument("-n","--number",nargs=1, default=[10],
                        help="the number of tracks of each artist to include (capped at 10).")
    parser.add_argument("-m","--mode",nargs=1, choices=["songs","recommendations", "both"], default=["songs"], 
                        help="wether you want your generated playlist to be based solely on songs by the artists you selected, you want it solely based on recommendations or you want a mixture of both.")
    
    if(vars(parser.parse_args())["number"] != None):
        n = int(vars(parser.parse_args())["number"][0])
    if(vars(parser.parse_args())["number"] != None):
        m = vars(parser.parse_args())["mode"][0]

    return {"n":n, "m":m}

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
        #print("artist found\t: "+artist[0]['name'])
        if m == "songs" or m=="both":
            search_result_1 = sp.artist_top_tracks(artist[0]["uri"])
            for track in search_result_1['tracks'][:n]:
                #print('track\t: %-30.30s\tid: %s' % (track['name'], track["id"]))
                track_list.append(track["id"])
        
        if m == "recommendations" or m == "both":
            search_result_2 = sp.recommendations(seed_artists=[artist[0]['id']], limit=n)  
            for track in search_result_2['tracks'][:n]:
                #print('track\t: %-30.30s\tid: %s' % (track['name'], track["id"]))
                track_list.append(track["id"])              
        
        
        #print()
    else:
        print(f"artist not found '{artist_name}' :(\n")
    return (track_list)

def add_tracks(args:Arguments, track_list:list) -> None:
    """
    Function that adds tracks to a given playlist. It's used to bypass the limit of 100 tracks added at a time.
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=args["client_id"], client_secret=args["client_secret"],redirect_uri=args["redirect_uri"],scope=args["scope"]))
    util.prompt_for_user_token(username=args["username"], scope=args["scope"], client_id=args["client_id"], client_secret=args["client_secret"], redirect_uri=args["redirect_uri"])
    found:bool = False
    for playlist in sp.current_user_playlists()["items"]:
        if playlist["name"]=="Generated playlist" and not found:

            sp.user_playlist_add_tracks(user=args["username"], tracks=track_list, playlist_id=playlist["id"])
            found = True
        elif playlist["name"]=="Generated playlist" and found:
            break

def playlist_generate(args:Arguments, track_list:list) -> None:
    """
    Function that generates a playlist with a given track list
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=args["client_id"], client_secret=args["client_secret"],redirect_uri=args["redirect_uri"],scope=args["scope"]))
    util.prompt_for_user_token(username=args["username"], scope=args["scope"], client_id=args["client_id"], client_secret=args["client_secret"], redirect_uri=args["redirect_uri"])
    
    description = f"""An automatically generated 🤖 playlist. ⚙️ Generated using Zempui's playlist generator"""
    
    sp.user_playlist_create(user=args["username"], name="Generated playlist", public=True, description=description)


    found:bool = False
    for playlist in sp.current_user_playlists()["items"]:
        if playlist["name"]=="Generated playlist" and not found:
            for tl in tqdm(divide_array(track_list, 80), desc="Adding tracks to playlist"): # To surpass the limitation of 100 tracks per request
                add_tracks(args=args,track_list=tl)
            found = True
        elif playlist["name"]=="Generated playlist" and found:
            # In case of there being more than one playlist with the name "Generated playlist, the tracks will only be added to the latest."
            break


def main(n:int, m:str) -> None:
    """
    Main function of the project
    """
    config:dict = {}
    with (open("./config.yml", "r")) as config_file:
        config = load(config_file, Loader=Loader)

    missing_args:dict[bool] = {"client_id":True, "client_secret":True, "user_id":True, "artists":True}
    for arg in missing_args:
        if arg in config and config[arg]!=None:
            missing_args[arg]=False
        else:
            print(f"ERROR in config.yml: missing argument '{arg}'")

    if not (missing_args["client_id"] or missing_args["client_secret"] or missing_args["user_id"] or missing_args["artists"]):
        args:Arguments = {"scope"           :   "user-library-read, user-library-modify, playlist-modify-public",
                          "client_id"       :   config["client_id"],
                          "client_secret"   :   config["client_secret"],
                          "redirect_uri"    :   "http://localhost:8080",
                          "username"        :   config["user_id"]}
        track_list:list = []

        
        for artist in tqdm(config["artists"], desc="Searching for artists"):
            (tl_aux)=track_search(args=args, artist_name=artist, n=n, m=m)
            for i in tl_aux:
                track_list.append(i)

        #[...]
        playlist_generate(args=args, track_list=track_list)
        print("Done!")

        


        
        
        

if __name__=="__main__":
    n:int = getArgs()["n"]
    m:str = getArgs()["m"]
    main(n, m)