CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE map_channels (
    my_channels_id TEXT NOT NULL,
    channels_id TEXT NOT NULL,
    PRIMARY KEY (my_channels_id, channels_id),
    FOREIGN KEY (my_channels_id) REFERENCES my_channels(id),
    FOREIGN KEY (channels_id) REFERENCES channels(id)
);
CREATE TABLE channels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, information TEXT, language TEXT NOT NULL, video_description TEXT);
CREATE TABLE google_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, account_email TEXT NOT NULL, account_password TEXT NOT NULL, country TEXT NOT NULL, profile TEXT NOT NULL);
CREATE TABLE my_channels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, subscriber INTEGER, creation_date DATE DEFAULT (date('now')), language TEXT NOT NULL, action TEXT NOT NULL, google_account_id INTEGER REFERENCES google_accounts (id) NOT NULL, translate_tags INTEGER);
CREATE TABLE videos (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT NOT NULL, video_title TEXT NOT NULL, video_url TEXT NOT NULL, upload_date DATE DEFAULT (date('now')), my_channels_id INTEGER NOT NULL, my_video_url TEXT, FOREIGN KEY (my_channels_id) REFERENCES my_channels (id));
