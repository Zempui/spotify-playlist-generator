# Spotify Playlist Generator
A tool to generate playlists containing the 'n' most popular tracks of several artists (up to 10 tracks each).
## Usage
Once you have downloaded the executable file, you should be good to go! You will have to fill out its fields with your custom information:
- In order to get the value of your `client_id` and `client_secret` fields, just go to [https://developer.spotify.com/](https://developer.spotify.com/), access your dashboard and register a new app (the app's redirect URI must be `http://localhost:8080`). Once that is done, go to your app's settings and copy your `client_id` and `client_secret` tokens, then paste them in their correspoding boxes.
- Note that your `user_id` may not be the same as your username, it is usually the original username with which the account was created.
- In the artist list you should specify the name of the artists you wish to see in your playlist. Note that the script uses whatever you input as an "artist name" in order to perform a normal spotify search, and will only add songs of the first artist that it finds, so be carefull with your spelling!

For more information, press the `?` button in the top-right of the window when executing the program.
