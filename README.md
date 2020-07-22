# Music Streaming Service Database System


## Installation

To use this template, your computer needs:

- [Python 2 or 3](https://python.org)
- [Pip Package Manager](https://pypi.python.org/pypi)

## Running the app

```bash
python app.py
```
## Preview of the app
### Entity Type
- Users
- Songs
- Playists
- Artists
- Albums

### Relationship Types
- An user has a playlist, containing songs he or she likes
- A playlist can include many songs, and a song can belong to many playlists
- An album has many songs, and a song can belong to an album
- a song is published by an artist, and an artist can publish many songs
- an album is published by an artist, and an artist can publish many albums

## Functions of the app

### Search
- users can search by song name, artist and album name.
- users can get reccomendation according to songs he liked (in his or her playlist)
- when registering, user can't use username that already exists in database
- after registering, user can login

### Insertion
- users can add their own accounts with username, password, name and email
- user can customize their own playlist by adding songs

### Deletion
- user can remove songs from their own playlist

### Update
- users can edit their personal information including name and email.

### Other Specialty Functions
- Permission system (only people that have logged in can access song search and playlists)
- Quicksearch: search from searched list/ playlists

