CREATE TABLE IF NOT EXISTS todos (
    username text,
    todo text,    
    PRIMARY KEY ((username), todo)
) WITH CLUSTERING ORDER BY (todo ASC);
