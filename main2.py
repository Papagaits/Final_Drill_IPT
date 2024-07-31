# Need Libraries for perform the REST-API-PROGRAMMING
from flask import Flask, make_response, jsonify, request, abort
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import dicttoxml 
from xml.dom.minidom import parseString


# using flask application 
app = Flask(__name__)

# call out of auth to our client
auth = HTTPBasicAuth()

# my SQL configuration to out database connect to python
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "mydb"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# Verify password function
@auth.verify_password
def verify_password(username, password):
    return username == "gaite" and password == "1010"



# Helper function to convert data to XML

def convert_to_xml(data):
    xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
    dom = parseString(xml)
    return dom.toprettyxml()



# Using postman Helper function to format response

def format_response(data):
    response_format = request.args.get('format', 'json').lower()
    if response_format == 'xml':
        xml_data = convert_to_xml(data)
        return make_response(xml_data, 200, {'Content-Type': 'application/xml'})
    else:
        return make_response(jsonify(data), 200)
    
    

# Protected routes with authentication

@app.route("/protected")
@auth.login_required
def protected_resource():
    data = {"message": "You are authorized to access this resource."}
    return format_response(data)


#USING GET: RETRIEVE OR VIEW HISTORY

@app.route("/departments", methods=["GET"])
@auth.login_required
def get_departments():
    data = data_fetch("SELECT * FROM departments")
    return format_response(data)

@app.route("/departments/<int:id>", methods=["GET"])
@auth.login_required
def get_departments_by_id(id):
    data = data_fetch(f"SELECT * FROM departments WHERE iddepartments = {id}")
    return format_response(data)

@app.route("/departments/<int:id>/Employee System", methods=["GET"])
@auth.login_required
def get_departments_by_iddepartments(id):
    data = data_fetch(f"""
       SELECT departments.iddepartments, Employee System.idcontract_types
        FROM departments
        INNER JOIN Employee System
        ON departments.iddepartments = Employee System.idcontract_types
        WHERE departments.iddepartments = {id}""")
    response_data = {"iddepartments": id, "count": len(data), "idcontract_types": data}
    return format_response(response_data)

#USING POST: ADD USER

@app.route("/departments", methods=["POST"])
@auth.login_required
def add_departments():
    if not request.is_json:
        abort(400, description="Request must be in JSON format.")
    cur = mysql.connection.cursor()
    info = request.get_json()
    iddepartments = info["iddepartments"]
    contract_classification = info["contract_classification"]
    contract_description = info["contract_description"]
    Contact_No = info["Contact_No"]
    Email = info["Email"]
    Location = info["Location"]
    Password = info["Password"]

    if not all([iddepartments, contract_classification, contract_description, Contact_No, Email, Location, Password]):
        abort(400, description="Missing required fields in JSON data.")
        
    cur.execute(
        """ INSERT INTO departments (iddepartments, contract_classification, contract_description, Contact_No, Email, Location, Password) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (iddepartments, contract_classification, contract_description, Contact_No, Email, Location, Password))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "departments added successfully", "rows_affected": rows_affected}
    return format_response(data)

#USING PUT: UPDATE THE BEFORE POST USING POSTMAN 

@app.route("/departments/<int:id>", methods=["PUT"])
@auth.login_required
def update_departments(id):
    if not request.is_json:
        abort(400, description="Request must be in JSON format.")
    cur = mysql.connection.cursor()
    info = request.get_json()
    contract_classification = info["contract_classification"]
    contract_description = info["contract_description"]
    Contact_No = info["Contact_No"]
    Email = info["Email"]
    Location = info["Location"]
    Password = info["Password"]

    if not all([contract_classification, contract_description, Contact_No, Email, Location, Password]):
        abort(400, description="No data provided for update.")
        
    cur.execute(
        """ UPDATE departments SET contract_classification = %s, contract_description = %s, Contact_No = %s, Email = %s, Location = %s, Password = %s 
        WHERE iddepartments = %s """,
        (contract_classification, contract_description, Contact_No, Email, Location, Password, id))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "departments updated successfully", "rows_affected": rows_affected}
    return format_response(data)

#USING DELETE TO POSTMAN ALREADY DELETE THE DATA IN MYSQL WORKBENCH

@app.route("/departments/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_departments(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM departments WHERE iddepartments = %s", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    data = {"message": "departments deleted successfully", "rows_affected": rows_affected}
    return format_response(data)

def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

# Getting URI parameters in a GET request

@app.route("/departments/format", methods=["GET"])
@auth.login_required  
def get_params():
    fmt = request.args.get('id')
    foo = request.args.get('aaaa')
    return make_response(jsonify({"format": fmt, "foo": foo}), 200)



if __name__ == "__main__":
    app.run(debug=True)

