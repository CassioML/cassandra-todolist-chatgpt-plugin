from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

import json

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.route("/todos/<string:username>", methods=["POST"])
async def add_todo(username):
    request_data = await quart.request.get_json(force=True)
    task = request_data["todo"]
    
    # Check if the username already exists in the Cassandra table
    query = f"SELECT COUNT(*) FROM cassio_tutorials.todo_list WHERE username = '{username}'"
    result = session.execute(query)
    count = result.one()[0]
    
    # If the username does not exist, insert it into the Cassandra table
    if count == 0:
        insert_query = f"INSERT INTO cassio_tutorials.todo_list (username) VALUES ('{username}')"
        session.execute(insert_query)
        
    # Insert the task into the Cassandra table
    task_insert_query = f"INSERT INTO cassio_tutorials.todo_list (username, task) VALUES ('{username}', '{task}')"
    session.execute(task_insert_query)
    return quart.Response(response='OK', status=200)

@app.route("/todos/<string:username>", methods=["GET"])
async def get_todos(username):
    # Retrieve the tasks from the Cassandra table for the provided username
    query = f"SELECT task FROM cassio_tutorials.todo_list WHERE username = '{username}'"
    result = session.execute(query)
    tasks = [row.task for row in result]
    return quart.jsonify(tasks)

@app.route("/todos/<string:username>", methods=["DELETE"])
async def delete_todo(username):
    request_data = await quart.request.get_json(force=True)
    todo_idx = request_data["todo_idx"]

    # Retrieve the task at the given index for the provided username
    query = f"SELECT task FROM cassio_tutorials.todo_list WHERE username = '{username}'"
    result = session.execute(query)
    tasks = [row.task for row in result]

    if 0 <= todo_idx < len(tasks):
        task_to_delete = tasks[todo_idx]

        # Delete the task from the Cassandra table
        query = f"DELETE FROM cassio_tutorials.todo_list WHERE username = '{username}' AND task = '{task_to_delete}'"
        session.execute(query)

    return quart.Response(response='OK', status=200)

@app.route("/logo.png", methods=["GET"])
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, content_type="text/json")

@app.route("/openapi.yaml", methods=["GET"])
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, content_type="text/json")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
