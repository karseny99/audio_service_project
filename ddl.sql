
CREATE TABLE artists (
	artist_id bigserial NOT NULL,
	"name" varchar(255) NOT NULL,
	bio text NULL,
	verified bool DEFAULT false NULL,
	created_at timestamptz DEFAULT now() NULL,
	CONSTRAINT artists_pkey PRIMARY KEY (artist_id)
);

CREATE TABLE playlists (
	playlist_id bigserial NOT NULL,
	"name" varchar(255) NOT NULL,
	is_favourite bool DEFAULT false NULL,
	is_public bool DEFAULT false NULL,
	created_at timestamptz DEFAULT now() NULL,
	CONSTRAINT playlists_pkey PRIMARY KEY (playlist_id)
);

CREATE TABLE tracks (
	track_id bigserial NOT NULL,
	title varchar(255) NOT NULL,
	duration_ms int4 NOT NULL,
	explicit bool DEFAULT false NULL,
	created_at timestamptz DEFAULT now() NULL,
	CONSTRAINT tracks_pkey PRIMARY KEY (track_id)
);

CREATE TABLE users (
	user_id bigserial NOT NULL,
	username varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	password_hash text NOT NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (user_id),
	CONSTRAINT users_username_key UNIQUE (username)
);

CREATE TABLE playlist_tracks (
	playlist_id bigserial NOT NULL,
	track_id bigserial NOT NULL,
	"position" int4 NOT NULL,
	CONSTRAINT playlist_tracks_pkey PRIMARY KEY (playlist_id, track_id),
	CONSTRAINT playlist_tracks_playlist_id_fkey FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
	CONSTRAINT playlist_tracks_track_id_fkey FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
);


CREATE TABLE playlists_users (
	playlist_id bigserial NOT NULL,
	user_id bigserial NOT NULL,
	is_creator bool DEFAULT false NULL,
	CONSTRAINT playlists_users_pkey PRIMARY KEY (playlist_id, user_id),
	CONSTRAINT playlists_users_playlist_id_fkey FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
	CONSTRAINT playlists_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


CREATE TABLE track_artists (
	track_id bigserial NOT NULL,
	artist_id bigserial NOT NULL,
	CONSTRAINT track_artists_pkey PRIMARY KEY (track_id, artist_id),
	CONSTRAINT track_artists_artist_id_fkey FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE,
	CONSTRAINT track_artists_track_id_fkey FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
);