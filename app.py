from flask import Flask, json, request
import sqlite3


api = Flask(__name__)

## Initialize database
with sqlite3.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS USERS (ID integer primary key, NAME text not null)")
    if len(cur.execute("SELECT * FROM USERS").fetchall()) == 0:
        cur.execute("INSERT INTO USERS (NAME) VALUES ('John'), ('Peter'), ('Edward'), ('Robert'), ('Mary'), ('Andrew')")
        print("Added initial data to User Table")
    con.commit()
    cur.close()


## Helper functions
def cursor_to_dict(cursor):
    data = cursor.fetchall()
    return [{col[0].lower(): row[i] for i, col in enumerate(cur.description)} for row in data]


## API routes
@api.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return api.send_static_file('index.html')


@api.route("/api/v1/users", methods=["GET"])
def api_get_users():
    data = []
    args = {k.lower(): request.args[k] for k in request.args}
    if 'id' in args:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM USERS WHERE ID={args['id']}")
            data = json.dumps(cursor_to_dict(cur))
    else:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM USERS")
            data = json.dumps(cursor_to_dict(cur))
    return data


@api.route("/api/v1/users", methods=["POST"])
def api_create_user():
    data = None
    try:
        data = request.get_json()
    except:
        pass
    if data is None:
        return "No data provided", 400

    name = data.get('name')
    if name is None:
        return "Request is missing a 'name' value", 400

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO USERS (NAME) VALUES ('{name}')")
        con.commit()

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM USERS WHERE NAME='{name}'")
        data = json.dumps(cursor_to_dict(cur))
    return data


@api.route("/api/v1/users", methods=["DELETE"])
def api_delete_user():
    args = {k.lower(): request.args[k] for k in request.args}
    if 'id' in args:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM USERS WHERE ID={args['id']}")
            data = cursor_to_dict(cur)
            if len(data) > 0:
                cur.execute(f"DELETE FROM USERS WHERE ID={args['id']}")
                return json.dumps(data)
            else:
                return f"No user with id '{args['id']}' found", 400
    else:
        return "Request is missing a 'id' parameter", 400


@api.route("/api/v1/users", methods=["PATCH"])
def api_update_user():
    args = {k.lower(): request.args[k] for k in request.args}
    if 'id' in args:
        data = None
        try:
            data = request.get_json()
        except:
            pass
        if data is None:
            return "No data provided to patch", 400
        name = data.get('name')
        if name is None:
            return "Request is missing a 'name' value", 400
        
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM USERS WHERE ID={args['id']}")
            data = cursor_to_dict(cur)
            if len(data) > 0:
                cur.execute(f"UPDATE USERS SET NAME='{name}' WHERE ID={args['id']}")
                return json.dumps(data)
            else:
                return f"No user with id '{args['id']}' found", 400
    else:
        return "Request is missing a 'id' parameter", 400


if __name__ == '__main__':
    api.run(debug=False, port=80)
    
