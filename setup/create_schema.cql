CREATE TABLE IF NOT EXISTS todo_list (
    username text,
    task text,    
    PRIMARY KEY ((username), task)
) WITH CLUSTERING ORDER BY (task ASC);
