PRAGMA user_version = 1;
/*TODO: join date and time in one single field*/
CREATE TABLE IF NOT EXISTS commands (
    id TEXT PRIMARY KEY,
    creation_date DATE NOT NULL,
    creation_time TIME NOT NULL,
    last_modif_date DATE NOT NULL,
    last_modif_time TIME NOT NULL,
    note TEXT NOT NULL,
    color TEXT
);

/*TODO: join date and time in one single field*/
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    creation_date DATE NOT NULL,
    creation_time TIME NOT NULL,
    last_modif_date DATE NOT NULL,
    last_modif_time TIME NOT NULL,
    tag TEXT NOT NULL,
    color TEXT NOT NULL
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
