from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os
import json
import quart
import quart_cors
from quart import request
from dotenv import load_dotenv
load_dotenv()

#Configure the Python Driver for Cassandra
#You'll need to have moved the secure connect bundle downloaded through your Astra UI (the Connect tab) to the specified location and ensure that the name matches 
cloud_config= {
        'secure_connect_bundle': './setup/secure-connect-cassio-ml.zip'
}
#In order for the Auth_Provider to work, your .env file must match the exact names specified here (or rename them and make sure the names match). 
auth_provider = PlainTextAuthProvider(os.getenv("astra_clientID"),os.getenv("astra_clientSecret"))
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()


app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Todos written to astra will persist beyond the end of your python session.

@app.route("/todos/<string:username>", methods=["POST"])
async def add_todo(username):
    request_data = await quart.request.get_json(force=True)
    todo = request_data["todo"]
    
    # Check if the username already exists in the Cassandra table
    query = f"SELECT COUNT(*) FROM cassio_tutorials.todos WHERE username = '{username}'"
    result = session.execute(query)
    count = result.one()[0]
    
    # If the username does not exist, insert it into the Cassandra table
    if count == 0:
        insert_query = f"INSERT INTO cassio_tutorials.todos (username, todo) VALUES ('{username}','test task')"
        session.execute(insert_query)
        
    # Insert the task into the Cassandra table
    todo_insert_query = f"INSERT INTO cassio_tutorials.todos (username, todo) VALUES ('{username}', '{todo}')"
    session.execute(todo_insert_query)
    return quart.Response(response='OK', status=200)

@app.route("/todos/<string:username>", methods=["GET"])
async def get_todos(username):
    # Retrieve the tasks from the Cassandra table for the provided username
    query = f"SELECT todo FROM cassio_tutorials.todos WHERE username = '{username}'"
    result = session.execute(query)
    todos = [row.todo for row in result]
    return quart.jsonify(todos)

@app.route("/todos/<string:username>", methods=["DELETE"])
async def delete_todo(username):
    request_data = await quart.request.get_json(force=True)
    todo_idx = request_data["todo_idx"]

    # Retrieve the task at the given index for the provided username
    query = f"SELECT todo FROM cassio_tutorials.todos WHERE username = '{username}'"
    result = session.execute(query)
    todos = [row.todo for row in result]

    if 0 <= todo_idx < len(todos):
        todos_to_delete = todos[todo_idx]

        # Delete the task from the Cassandra table
        query = f"DELETE FROM cassio_tutorials.todos WHERE username = '{username}' AND todo = '{todos_to_delete}'"
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
