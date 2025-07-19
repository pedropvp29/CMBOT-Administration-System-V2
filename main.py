from flask import Flask , render_template , request
from os import chdir , path
from sqlite3 import connect
from random import shuffle

chdir(path.dirname(__file__))

#database 
connection = connect("data/students.db",check_same_thread=True)
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS students (number INTEGER PRIMARY KEY,student varchar(100),name varchar(100),class varchar(20),codename varchar(100),cpf varchar(30),born varchar(30),email varchar(100),phone varchar(100),possition varchar(50))")
cursor.execute("CREATE TABLE IF NOT EXISTS groups (name varchar(100),member varchar(100))")

connection.commit()

connection.close()

#app
app = Flask("CMBOT ADMISTRATION SYSTEM")

@app.template_filter()
def safe_split(value, sep, index):
    try:
        return value.split(sep)[index]
    except (IndexError, AttributeError):
        return ''

@app.route("/")
def mainPage():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    
    connection.close()
    return render_template("mainPage.html",data=data)

@app.route("/edit")
def editData():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()

    number = request.args.get("number")
    possition = int(request.args.get("possition"))
    value = request.args.get("value")
    
    match possition:
        case 1:#nome de guerra
            cursor.execute(f"UPDATE students SET student = '{value}' where number = {number}")
            connection.commit()
        case 2:#nome completo
            cursor.execute(f"UPDATE students SET name = '{value.strip()}' where number = {number}")
            connection.commit()
        case 3:#turma
            cursor.execute(f"UPDATE students SET class = '{value.strip()}' where number = {number}")
            connection.commit()
        case 4:#codinome
            cursor.execute(f"UPDATE students SET codename = '{value.strip()}' where number = {number}")
            connection.commit()
        case 5:#cpf
            cursor.execute(f"UPDATE students SET cpf = '{value.strip()}' where number = {number}")
            connection.commit()
        case 6:#data de nascimento
            cursor.execute(f"UPDATE students SET born = '{value.strip()}' where number = {number}")
            connection.commit()
        case 7:#email
            cursor.execute(f"UPDATE students SET email = '{value.strip()}' where number = {number}")
            connection.commit()
        case 8:#telefone
            cursor.execute(f"UPDATE students SET phone = '{value.strip()}' where number = {number}")
            connection.commit()
        case 9:#cargo/posição
            cursor.execute(f"UPDATE students SET possition = '{value.strip()}' where number = {number}")
            connection.commit()
            
    connection.close()
    return "sucess"

@app.route("/remove")
def removeData():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    number = request.args.get("number")

    cursor.execute(f"DELETE FROM students WHERE number = {number}")
    connection.commit()
    
    connection.close()
    return "sucess"

@app.route("/add")
def addData():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    number = request.args.get("number")
    student = request.args.get("student")
    name = request.args.get("name")
    clas = request.args.get("class")
    codename = request.args.get("codename")
    cpf = request.args.get("cpf")
    born = request.args.get("born")
    studentEmail = request.args.get("studentEmail")
    fatherEmail = request.args.get("fatherEmail")
    motherEmail = request.args.get("motherEmail")
    studentPhone = request.args.get("studentPhone")
    fatherPhone = request.args.get("fatherPhone")
    motherPhone = request.args.get("motherPhone")
    possition = request.args.get("possition")

    cursor.execute(f"INSERT INTO students (number,student,name,class,codename,cpf,born,email,phone,possition) VALUES ('{number}','{student}','{name}','{clas}','{codename}','{cpf}','{born}','{studentEmail + '(Aluno)' + fatherEmail + '(Pai)' + motherEmail + '(Mãe)'}','{studentPhone + '(Aluno)' + fatherPhone + '(Pai)' + motherPhone + '(Mãe)'}','{possition}')")
    connection.commit()
    
    connection.close()
    return "sucess"

@app.route("/makeGroup",methods=["POST"])
def makeGroup():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()

    data = request.get_json()
    name = data[0]
    members = data[1:]
    
    if name != "null": #sem aleatorizador
        for member in members:
            cursor.execute(f"INSERT INTO groups (name,member) values ('{name.strip()}','{member.strip()}')")
 
    else: #com aleatorizador
        groupMemberNumber = members[len(members) - 1]
        members = members[:len(members)-1]
        names = []
        
        cursor.execute("SELECT name FROM groups")
        data = cursor.fetchall()
        
        for name in data:
            if not name[0] in names:
                names.append(name[0])
         
        shuffle(members)
        
        if int(groupMemberNumber) > len(members): #sistema de segurança
            groupMemberNumber = len(members)
        
        group = 0
        number = 0
        
        for member in members:
            
            while f"grupo {group}" in names:
                group += 1
            
            if number == int(groupMemberNumber):
                number = 0
                group += 1
            
                cursor.execute("SELECT name FROM groups")
                data = cursor.fetchall()
        
                for name in data:
                    if not name[0] in names:
                        names.append(name[0])
            
            cursor.execute(f"INSERT INTO groups (name,member) values ('grupo {group}','{member.strip()}')")
            number +=1 
        
    connection.commit()
    connection.close()
    return "sucess"

@app.route("/groups")
def groupPage():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM groups ORDER BY name")
    data = cursor.fetchall()
    
    groups = {}
    for name , member in data:
        try:
            cursor.execute(f"SELECT * FROM students where number = {member} ORDER BY number")
            groups[name] += [cursor.fetchall()][0]
        except KeyError:
            try:
                cursor.execute(f"SELECT * FROM students where number = {member} ORDER BY number")
                groups[name] = [cursor.fetchall()[0]]
            except IndexError:
                continue
    
    connection.close()
    return render_template("groupsPage.html",groups=groups)

@app.route("/groupRemove")
def groupRemove():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    name = request.args.get("name")
    member = request.args.get("number")
    
    cursor.execute(f"DELETE FROM groups WHERE member = '{member}' AND name = '{name}'")
    connection.commit()
    
    connection.close()
    return "sucess"

@app.route("/groupDelete")
def groupDelete():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    name = request.args.get("name")
    
    cursor.execute(f"DELETE FROM groups WHERE name = '{name.strip()}'")
    connection.commit()
    
    connection.close()
    return "sucess"

@app.route("/groupAdd")
def grupAdd():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    name = request.args.get("name")
    number = request.args.get("number")
    
    cursor.execute(f"INSERT INTO groups (name,member) VALUES ('{name.strip()}','{number.strip()}')")
    connection.commit()
    
    connection.close()
    return "sucess"

@app.route("/groupNameChange")
def groupNameChange():
    connection = connect("data/students.db",check_same_thread=True)
    cursor = connection.cursor()
    
    name = request.args.get("name")
    new = request.args.get("new")
    
    cursor.execute(f"UPDATE groups SET name = '{new}' WHERE name = '{name}'")
    connection.commit()
    
    connection.close()
    return "sucess"

app.run(debug=True)