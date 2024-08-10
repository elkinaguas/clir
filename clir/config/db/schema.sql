PRAGMA user_version = 1;
CREATE TABLE IF NOT EXISTS commands (
    id TEXT PRIMARY KEY,
    creation_date TEXT NOT NULL,
    last_modif_date TEST NOT NULL,
    command TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    creation_date TEXT NOT NULL,
    last_modif_date TEXT NOT NULL,
    tag TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commands_tags (
    command_id TEXT,
    tag_id TEXT,
    PRIMARY KEY (command_id, tag_id),
    FOREIGN KEY (command_id) REFERENCES commands(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
