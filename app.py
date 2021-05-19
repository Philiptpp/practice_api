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
@api.route("/users", methods=["GET"])
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


@api.route("/users", methods=["POST"])
def api_create_user():
    print("Create request received")
    try:
        data = request.get_json()
    except:
        data = {}
    if len(data) == 0:
        return json.dumps({"message": "No data provided"}), 400

    name = data.get('name')
    if name is None:
        return json.dumps({"message": "Request is missing a 'name' value"}), 400

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO USERS (NAME) VALUES ('{name}')")
        con.commit()

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM USERS WHERE NAME='{name}'")
        data = json.dumps(cursor_to_dict(cur))
    return data


if __name__ == '__main__':
    api.run(debug=False, port=80)
    
