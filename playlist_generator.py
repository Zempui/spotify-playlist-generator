from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import util
import argparse


def getArgs() -> dict:
    n:int = 10
    m:str = "songs"

    parser = argparse.ArgumentParser(description="A tool to generate playlists containing the 'n' most popular tracks of several artists (default = 10)")
    parser.add_argument("-n","--number",nargs=1, default=10,
                        help="the number of tracks of each artist to include (capped at 10)")
    parser.add_argument("-m","--mode",nargs=1, choices=["songs","recommendations", "both"], default=["songs"], 
                        help="wether you want your generated playlist to be based solely on songs by the artists you selected, you want it solely based on recommendations or you want a mixture of both.")
    
    if(vars(parser.parse_args())["number"] != None):
        n = int(vars(parser.parse_args())["number"])
    if(vars(parser.parse_args())["number"] != None):
        m = vars(parser.parse_args())["mode"][0]

    return {"n":n, "m":m}



def main(n:int, m:str) -> None:
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
        scope = "user-library-read, user-library-modify, playlist-modify-public"
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        redirect_uri = "http://localhost:8080"
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri,scope=scope))
        util.prompt_for_user_token(username=config["user_id"], scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
        print("Tracks found:")
        track_list:list = []
        artist_list:str = ""
        for name in config["artists"]:
            print(f"searching for artist '{name}'...\n")
            results:dict = sp.search(q='artist:' + name, type='artist')
            artist:dict = results['artists']['items']
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
                    search_result_2 = sp.recommendations(seed_artists=[artist[0]['id']], limit=10)  
                    for track in search_result_2['tracks'][:n]:
                        print('track\t: %-30.30s\tid: %s' % (track['name'], track["id"]))
                        track_list.append(track["id"])              
                
                artist_list=artist_list+artist[0]['name']+", "
                
                print()
            else:
                print("artist not found :(\n")
        
        description = f"""An automatically generated 🤖 playlist containing songs 🎶 from {artist_list[:artist_list[:-2].rfind(", ")]} and {artist_list[artist_list[:-2].rfind(", ")+2:-2]}. ⚙️ Generated using Zempui's playlist generator"""
        
        sp.user_playlist_create(user=config["user_id"], name="Generated playlist", public=True, description=description)
        util.prompt_for_user_token(username=config["user_id"], scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
        found:bool = False
        for playlist in sp.current_user_playlists()["items"]:
            id:str = ""
            if playlist["name"]=="Generated playlist" and not found:
                sp.user_playlist_add_tracks(user=config["user_id"], tracks=track_list, playlist_id=playlist["id"])
                found = True
            elif playlist["name"]=="Generated playlist" and found:
                # In case of there being more than one playlist with the name "Generated playlist, the tracks will only be added to the latest."
                break


if __name__=="__main__":
    n:int = getArgs()["n"]
    m:str = getArgs()["m"]
    main(n, m)