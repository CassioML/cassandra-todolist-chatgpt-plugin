CREATE TABLE IF NOT EXISTS todo_list (
    username text,
    task text,    
    PRIMARY KEY ((task), username)
) WITH CLUSTERING ORDER BY (username ASC);
