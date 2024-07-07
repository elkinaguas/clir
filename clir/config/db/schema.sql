PRAGMA user_version = 1;
/*TODO: join date and time in one single field*/
CREATE TABLE IF NOT EXISTS commands (
    id TEXT PRIMARY KEY,
    creation_date TEXT NOT NULL,
    last_modif_date TEST NOT NULL,
    command TEXT NOT NULL,
    description TEXT NOT NULL
);

/*TODO: join date and time in one single field*/
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    creation_date TEXT NOT NULL,
    last_modif_date TEXT NOT NULL,
    tag TEXT NOT NULL
);

/*TODO: change schema so that one command can have multiple tags*/
/*TODO: join date and time in one single field*/
CREATE TABLE IF NOT EXISTS commands_tags (
    command_id TEXT,
    tag_id TEXT,
    PRIMARY KEY (command_id, tag_id),
    FOREIGN KEY (command_id) REFERENCES notes(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
