# Spotify Playlist Generator
A tool to generate playlists containing the 'n' most popular tracks of several artists (up to 10 tracks each).
## Usage
In order to use this tool, you will have to download the current repository and install the latest version of Python. After that, just execute the followind command while located at the parent folder of the repository ([...]/spotify-playlist-generator/)
```bash
python3 -m pip install -r requirements.txt
```
Once dependencies have been taken care of, you should be good to go! Just create a YAML file with the same structure as the provided file `config_template.yml` and rename it `config.yml`. You will have to fill out its fields with your custom information:
- In order to get the value of your `client_id` and `client_secret` fields, just go to [https://developer.spotify.com/](https://developer.spotify.com/), access your dashboard and register a new app (the app's redirect URI must be `http://localhost:8080`). Once that is done, go to your app's settings and copy your `client_id` and `client_secret` tokens, then paste them at their corresponding fields in `config.yml`.
- Note that your `user_id` may not be the same as your username, it is usually the original username with which the account was created.
- In the artist list you should specify the name of the artists you wish to see in your playlist. Note that the script uses whatever you input as an "artist name" in order to perform a normal spotify search, and will only add songs of the first artist that it finds, so be carefull with your spelling!

Besides the paremeters specified in the `config.yml` file, when executing the script, a list of optional arguments may be passed to make it have a certain behaviour:
- `-n`, `--number`: the number of tracks of each artist to include (capped at 10).
- `-m`, `--mode`: wether you want your generated playlist to be based solely on songs by the artists you selected, you want it solely based on recommendations or you want a mixture of both.
