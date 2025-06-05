## Audio Service ##

### Launch ###

- ```docker compose up -d``` from source directory
- install dependencies with ```poetry install``` then use ```make generate``` and ```make run``` from each service folder
- to use valid version of database you should reset sequences, use following script
  ```sql
  SELECT setval('playlist.playlists_playlist_id_seq', (SELECT MAX(playlist_id) FROM playlist.playlists));
  SELECT setval('user_profile.users_user_id_seq', (SELECT MAX(user_id) FROM user_profile.users));
  SELECT setval('music_catalog.tracks_track_id_seq', (SELECT MAX(track_id) FROM music_catalog.tracks));
  SELECT setval('music_catalog.genres_genre_id_seq', (SELECT MAX(genre_id) FROM music_catalog.genres));
  SELECT setval('music_catalog.bitrates_bitrate_id_seq', (SELECT MAX(bitrate_id) FROM music_catalog.bitrates));
  SELECT setval('music_catalog.artists_artist_id_seq', (SELECT MAX(artist_id) FROM music_catalog.artists));
  ```
-   open kafka-ui and (re)create manually ```etl-topic```
-   ```make generate; make run``` from analytics folder and follow its readme file
-   for streaming test make folder in minio with name ```{track_id}``` and upload various bitrate files, name them like ```128.mp3```
-   in order to see metrics open ```localhost:3000```, import ```dashbord.json``` and create data source (important: name it ```prometheus``` in lowercase) with ```prometheus:9090```
