from flask import Flask, render_template, request, flash, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)


# do not cache responses
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# initiate database
dbvar = sqlite3.connect("main.db", check_same_thread=False)
db = dbvar.cursor()

@app.context_processor
def inject_boards():

    # get all user boards
    def getboards():
        # if not logged in
        if not session.get("user_id"):
            return 0
            
        userid = session["user_id"]
        db.execute("SELECT id, name FROM boards WHERE userid = ?", (userid,))
        boards = db.fetchall()
        
        # if no boards exist put empty board
        if boards is None:
            boards = {
                "name": "No Boards",
                "id": 0
            }

            return boards

        # populate into list of dicts
        myboards = []

        for board in boards:
            current = {
                "name": board[1],
                "id": board[0]
            }
            myboards.append(current)

        return myboards

    # return list of boards
    return dict(getboards=getboards)


def getlists(boardid):
    # get lists

    lists = []
    
    # get lists from database
    db.execute("SELECT name, id FROM lists WHERE boardid = ?", (boardid,))
    results = db.fetchall()

    for result in results:
        
        # get tasks for that list
        tasks = []

        # get tasks from database
        db.execute("SELECT * FROM tasks WHERE listid = ?", (result[1],))
        taskresults = db.fetchall()

        for taskresult in taskresults:
            currenttask = {
                "task": taskresult[2],
                "id": taskresult[0],
                "listid": taskresult[1]
            }

            tasks.append(currenttask)

        current = {
            "name": result[0],
            "id": result[1],
            "tasks": tasks
        }

        lists.append(current)
    return lists


@app.route("/", methods=["GET", "POST"])
def index():

    # redirect to login if user is not logged in
    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":

        # check for operation
        if request.form.get("op"):

            # check which operation

            if request.form.get("op") == "switch":
                # switch active board
                boardid = request.form.get("id")
                boardname = request.form.get("name")

                session["board_id"] = boardid
                session["board_name"] = boardname

            if request.form.get("op") == "cb":
                # cb is create board
                name = request.form.get("name")

                # check validity
                if name is None:
                    return redirect("/")
                elif name == "":
                    setname = "New board"
                else:
                    setname = name

                # create board
                cboard(setname)
            
            if request.form.get("op") == "rb":
                # rb is rename board

                name = request.form.get("name")

                # check validity
                if name is None:
                    return redirect("/")
                elif name == "":
                    setname = "Unnamed"
                else:
                    setname = name

                id = request.form.get("id")
                
                if id is None:
                    return redirect("/")
                
                # rename board
                rboard(id, setname)

            if request.form.get("op") == "db":
                # db is delete board

                id = request.form.get("id")

                if id is None:
                    return redirect("/")
                
                # delete board
                dboard(id)

            if request.form.get("op") == "cl":
                # cl is create list

                boardid = request.form.get("id")
                listname = request.form.get("name")

                if listname == "":
                    listname = "New list"

                # add list into db
                clist(listname, boardid)

            if request.form.get("op") == "rl":
                # rl is rename list

                listid = request.form.get("id")
                name = request.form.get("name")

                if name == "":
                    name = "Unnamed"

                # add list into db
                rlist(listid, name)

            if request.form.get("op") == "dl":
                # dl is delete list

                listid = request.form.get("id")

                # delete list
                dlist(listid)

            if request.form.get("op") == "ct":
                # ct is create task

                listid = request.form.get("id")
                taskname = request.form.get("name")

                if taskname == "":
                    taskname = "New task"

                # add list into db
                ctask(taskname, listid)

            if request.form.get("op") == "mt":
                # mt is move task

                id = request.form.get("id")
                listid = request.form.get("listid")

                if listid == "":
                    return redirect("/")
                
                # move task into new list
                mtask(id, listid)

            if request.form.get("op") == "rt":
                # rt is rename task

                id = request.form.get("id")
                name = request.form.get("name")

                if name == "":
                    name = "Unnamed"
                    return redirect("/")
                
                # rename task
                rtask(id, name)

            if request.form.get("op") == "dt":
                # dt is delete task

                id = request.form.get("id")
                
                # delete task
                dtask(id)

        return redirect("/")

    else:
        lists = getlists(session["board_id"])
        return render_template("index.html", lists=lists)


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        # login function

        # username check
        username = request.form.get("username")
        db.execute("SELECT * FROM users WHERE username = ?", [username])
        user = db.fetchone()

        if user is None:
            # if no results found, error
            feedback = "Invalid username or password"
            return render_template("login.html", feedback=feedback)

        # password check
        password = request.form.get("password")
        userhash = user[3]

        if check_password_hash(userhash, password):
            # login
            session["user_id"] = user[0]
            session["display_name"] = user[1]

            # get user boards
            userid = session["user_id"]
            db.execute("SELECT id, name FROM boards WHERE userid = ?", (userid,))
            boards = db.fetchone()

            # return to the first board
            session["board_id"] = boards[0]
            session["board_name"] = boards[1]

            return redirect("/")
        else:
            # if password is incorrect, error
            feedback = "Invalid username or password"
            return render_template("login.html", feedback=feedback)
    else:
        # show login page
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # register function

        # check display name
        displayname = request.form.get("displayname")

        if displayname == "":
            feedback = "Display name cannot be empty"
            return render_template("register.html", feedback=feedback)
        elif len(displayname) < 3:
            feedback = "Display name cannot be shorter than 3 characters"
            return render_template("register.html", feedback=feedback)

        # check username
        username = request.form.get("username")

        if username == "":
            feedback = "Username cannot be empty"
            return render_template("register.html", feedback=feedback)
        elif len(username) < 3:
            feedback = "Username cannot be shorter than 3 characters"
            return render_template("register.html", feedback=feedback)
        
        # check if username already exists in db
        db.execute("SELECT * FROM users WHERE username = ?", [username])
        reggeduser = db.fetchone()

        if reggeduser is not None:
            # if username is already registered
            feedback = "Username already exists"
            return render_template("register.html", feedback=feedback)
        
        # check password
        password = request.form.get("password")
        if password == "":
            feedback = "Password cannot be empty"
            return render_template("register.html", feedback=feedback)
        elif len(password) < 3:
            feedback = "Password cannot be shorter than 3 characters"
            return render_template("register.html", feedback=feedback)

        # check password confirmation
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            feedback = "Passwords do not match"
            return render_template("register.html", feedback=feedback)
        
        # if passed all these checks, register
        passhash = generate_password_hash(password)

        db.execute("INSERT INTO users (displayname, username, passhash) VALUES (?1, ?2, ?3)",( displayname, username, passhash))
        dbvar.commit()

        # auto log in
        db.execute("SELECT * FROM users WHERE username = ?", [username])
        user = db.fetchone()

        session["user_id"] = user[0]
        session["display_name"] = user[1]

        # create base board "My Board"
        newboardname = "My Board"
        cboard(newboardname)

        return redirect("/")

    else:
        # show registration page
        return render_template("register.html")


@app.route("/logout")
def logout():

    # forget logged in user
    session.clear()

    # redirect user to login
    return redirect("/login")


@app.route("/account", methods=["GET", "POST"])
def account():

    # redirect to login if user is not logged in
    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":
        # get operation index
        op = request.form.get("op")

        id = session["user_id"]

        # op 0 = change display name
        if op == "0":
            displayname = request.form.get("displayname")

            # check display name
            if displayname == "":
                feedback = "Display name cannot be empty"
                return render_template("account.html", feedback=feedback)
            elif len(displayname) < 3:
                feedback = "Display name cannot be empty"
                return render_template("account.html", feedback=feedback)

            # update database
            db.execute("UPDATE users SET displayname = ?1 WHERE id = ?2", (displayname, id))
            dbvar.commit()

            # update login session
            session["display_name"] = displayname

            # redirect with feedback
            feedback = "Display name changed successfully"
            return render_template("account.html", feedback=feedback)
        
        if op == "1":
            oldpw = request.form.get("oldpw")
            
            # check oldpw
            db.execute("SELECT passhash FROM users WHERE id = ?", (id,))
            passhash = db.fetchone()

            # give feedback and redirect if old password is incorrect
            if not check_password_hash(passhash[0], oldpw):
                feedback = "Old password is incorrect"
                return render_template("account.html", feedback=feedback)

            # validate new password
            newpw = request.form.get("newpw")
            
            if newpw == "":
                feedback = "New password cannot be empty"
                return render_template("account.html", feedback=feedback)
            elif len(newpw) < 3:
                feedback = "New password cannot be shorter than 3 characters"
                return render_template("account.html", feedback=feedback)

            # check if new password is the same as old
            if check_password_hash(passhash[0], newpw):
                feedback = "New password cannot be the same as old password"
                return render_template("account.html", feedback=feedback)
            
            # check if new passwords match
            confirmation = request.form.get("confirmation")

            if newpw != confirmation:
                feedback = "New passwords do not match"
                return render_template("account.html", feedback=feedback)

            # update database
            newpasshash = generate_password_hash(newpw)
            db.execute("UPDATE users SET passhash = ?1 WHERE id = ?2", (newpasshash, id))
            dbvar.commit()

            # redirect with feedback
            feedback = "Password changed successfully"
            return render_template("account.html", feedback=feedback)
        else:
            feedback = "Unknown operation"
            return render_template("account.html", feedback=feedback)

    else:
        return render_template("account.html")


def cboard(name):
    # create board

    # insert board into database
    boardname = name[:26]
    userid = session["user_id"]
    db.execute("INSERT INTO boards (userid, name) VALUES (?1, ?2)", (userid, boardname))
    dbvar.commit()

    # get id for the newly created board
    boardid = db.lastrowid

    # create default lists for new board
    clist("To do", boardid)
    clist("Done", boardid)

    # set newly made board as current
    session["board_id"] = boardid
    session["board_name"] = name


def clist(name, boardid):
    # create list

    # insert list into database
    listname = name[:26]
    db.execute("INSERT INTO lists (boardid, name) VALUES (?1, ?2)", (boardid, listname))
    dbvar.commit()


def ctask(name, listid):
    # create task

    # insert task into database
    taskname = name[:100]
    db.execute("INSERT INTO tasks (listid, task) VALUES (?1, ?2)", (listid, taskname))
    dbvar.commit()


def rboard(id, name):
    # rename board

    # update new name into database
    newname = name[:26]
    db.execute("UPDATE boards SET name = ?1 WHERE id = ?2", (newname, id))
    dbvar.commit()


def rlist(id, name):
    # rename list

    # update new name into database
    newname = name[:26]
    db.execute("UPDATE lists SET name = ?1 WHERE id = ?2", (newname, id))
    dbvar.commit()


def rtask(id, name):
    # rename task

    # update new name into database
    newname = name[:100]
    db.execute("UPDATE tasks SET task = ?1 WHERE id = ?2", (newname, id))
    dbvar.commit()


def dboard(id):
    # delete board

    # delete all lists inside board
    db.execute("SELECT id FROM lists WHERE boardid = ?1", (id,))
    listids = db.fetchall()
    for listid in listids:
        dlist(listid[0])
    
    # remove row from database
    db.execute("DELETE FROM boards WHERE id = ?1", (id,))
    dbvar.commit()

    # get user boards
    userid = session["user_id"]
    db.execute("SELECT id, name FROM boards WHERE userid = ?", (userid,))
    boards = db.fetchone()

    # if last board deleted create new basic one
    if boards is None:
        cboard("New board")
        return

    # return to the first board
    session["board_id"] = boards[0]
    session["board_name"] = boards[1]


def dlist(id):
    # delete list

    # delete all tasks inside list
    db.execute("DELETE FROM tasks WHERE listid = ?1", (id,))
    dbvar.commit()

    # remove row from database
    db.execute("DELETE FROM lists WHERE id = ?1", (id,))
    dbvar.commit()


def dtask(id):
    # delete task

    # remove row from database
    db.execute("DELETE FROM tasks WHERE id = ?1", (id,))
    dbvar.commit()


def mtask(taskid, listid):
    # move task to another list

    # update list where task exists
    db.execute("SELECT task FROM tasks WHERE id = ?1", (taskid,))
    task = db.fetchone()
    db.execute("INSERT INTO tasks (listid, task) VALUES (?1, ?2)", (listid, task[0]))
    db.execute("DELETE FROM tasks WHERE id = ?1", (taskid,))
    dbvar.commit()