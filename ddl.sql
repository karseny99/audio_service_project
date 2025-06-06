drop schema if exists public;
CREATE SCHEMA user_profile;
CREATE SCHEMA playlist;
CREATE SCHEMA listening_history;
CREATE SCHEMA music_catalog;

CREATE TABLE user_profile.users (
	user_id bigserial NOT NULL,
	username varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	password_hash text NOT NULL,
    role varchar(255) DEFAULT 'listener',
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (user_id),
	CONSTRAINT users_username_key UNIQUE (username)
);

-- 2. Playlist Context
CREATE TABLE playlist.playlists (
    playlist_id BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE playlist.playlist_tracks (
    playlist_id BIGINT NOT NULL REFERENCES playlist.playlists(playlist_id) ON DELETE CASCADE,
    track_id BIGINT NOT NULL, -- Без FK (трек в Music Catalog Context)
    position INT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (playlist_id, track_id)
);

CREATE TABLE playlist.playlist_users (
    playlist_id BIGINT NOT NULL REFERENCES playlist.playlists(playlist_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL, 
    is_creator BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (playlist_id, user_id)
);


-- 3. Listening History Context
CREATE TABLE listening_history.user_likes (
    user_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, track_id)
);

CREATE TABLE listening_history.user_history (
    user_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, track_id)
);

-- 4. Music Catalog Context
CREATE TABLE music_catalog.artists (
    artist_id BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE music_catalog.tracks (
    track_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    duration_ms INT NOT NULL,
    explicit BOOLEAN DEFAULT FALSE,
    release_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE music_catalog.track_artists (
    track_id BIGINT NOT NULL REFERENCES music_catalog.tracks(track_id) ON DELETE CASCADE,
    artist_id BIGINT NOT NULL REFERENCES music_catalog.artists(artist_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, artist_id)
);

CREATE TABLE music_catalog.genres (
    genre_id SERIAL PRIMARY KEY,
    "name" VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE music_catalog.track_genres (
    track_id BIGINT NOT NULL REFERENCES music_catalog.tracks(track_id) ON DELETE CASCADE,
    genre_id INT NOT NULL REFERENCES music_catalog.genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, genre_id)
);

CREATE TABLE music_catalog.bitrates (
    bitrate_id SERIAL PRIMARY KEY,
    name VARCHAR(20),  -- Например, "128kbps", "320kbps", "Lossless"
);

CREATE TABLE music_catalog.track_bitrates (
    track_id BIGINT REFERENCES music_catalog.tracks(track_id) ON DELETE CASCADE,
    bitrate_id INT REFERENCES music_catalog.bitrates(bitrate_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, bitrate_id)
)
