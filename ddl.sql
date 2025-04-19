-- Users
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
);

-- auth_credentials
CREATE TABLE auth_credentials (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) DEFERRABLE INITIALLY DEFERRED
);

-- Artists
CREATE TABLE artists (
    artist_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks
CREATE TABLE tracks (
    track_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    duration_ms INTEGER NOT NULL,
    explicit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Relation Track <-> Artist
CREATE TABLE track_artists (
    track_id BIGINT NOT NULL,
    artist_id BIGINT NOT NULL,
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE
);


-- Playlist
CREATE TABLE playlists (
    playlist_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_favourite BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT unique_favourite_per_user UNIQUE (user_id, is_favourite) 
        DEFERRABLE INITIALLY DEFERRED WHERE (is_favourite)
);

-- Relation Playlist <-> Track
CREATE TABLE playlist_tracks (
    playlist_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE CASCADE,
);

-- Relation Playlist <-> User
CREATE TABLE playlists_users (
    playlist_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (playlist_id, user_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- On register: duplicate data from auth_cred to Users + create playlist of favourites 
CREATE OR REPLACE FUNCTION handle_registration()
RETURNS TRIGGER AS $$
BEGIN
    -- 1. Создаем/обновляем запись в users
    INSERT INTO users (user_id, username, email)
    VALUES (NEW.user_id, NEW.username, NEW.email)
    ON CONFLICT (user_id) 
    DO UPDATE SET
        username = EXCLUDED.username,
        email = EXCLUDED.email,
        updated_at = NOW();
    
    -- 2. Создаем плейлист "Favourites"
    INSERT INTO playlists (user_id, name, is_favourite)
    VALUES (NEW.user_id, 'Favourites', TRUE)
    ON CONFLICT DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_handle_registration
AFTER INSERT ON auth_credentials
FOR EACH ROW
EXECUTE FUNCTION handle_registration();

-- On User's data update in Users-table
CREATE OR REPLACE FUNCTION sync_auth_from_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновляем auth_credentials только если данные изменились
    IF (OLD.username IS DISTINCT FROM NEW.username) OR 
       (OLD.email IS DISTINCT FROM NEW.email) THEN
       
        UPDATE auth_credentials 
        SET 
            username = NEW.username,
            email = NEW.email
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_sync_auth_from_user
AFTER UPDATE OF username, email ON users
FOR EACH ROW
EXECUTE FUNCTION sync_auth_from_user();

-- Настройка прав доступа
-- CREATE ROLE auth_service;
-- GRANT SELECT, UPDATE ON auth_credentials TO auth_service;
-- GRANT SELECT (user_id, username, email, is_active) ON users TO auth_service;