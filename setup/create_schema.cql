CREATE TABLE IF NOT EXISTS todos (
    username text,
    todo text    
    PRIMARY KEY (city, todo)
) WITH CLUSTERING ORDER BY (username ASC);
