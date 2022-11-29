from flask import Flask, render_template, request, abort
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost", database="CentralizedBloodBank", user="postgres", password="pksc"
)
conn.autocommit = True
cur = conn.cursor()


@app.route("/")
def main():
    dataObj = {}
    cur.execute("SELECT * FROM address LIMIT 100")
    # print(cur.description)
    data = cur.fetchall()
    data1 = cur.description
    dataObj["table_cols"] = data1
    dataObj["table_rows"] = data
    return render_template("index.html", value=dataObj)

# return hospital view
@app.route("/hospital")
def hospital():
    dataObj = {}
    cur.execute("SELECT * FROM hospital LIMIT 100")
    # print(cur.description)
    data = cur.fetchall()
    data1 = cur.description
    dataObj["table_cols"] = data1
    dataObj["table_rows"] = data
    return render_template("hospitalView.html", value=dataObj)

# return patient view
@app.route("/patient")
def patient():
    dataObj = {}
    cur.execute("SELECT * FROM patient LIMIT 100")
    # print(cur.description)
    data = cur.fetchall()
    data1 = cur.description
    dataObj["table_cols"] = data1
    dataObj["table_rows"] = data
    return render_template("patientView.html", value=dataObj)

# return donor view
@app.route("/donor")
def donor():
    dataObj = {}
    cur.execute("SELECT * FROM donor LIMIT 100")
    # print(cur.description)
    data = cur.fetchall()
    data1 = cur.description
    dataObj["table_cols"] = data1
    dataObj["table_rows"] = data
    return render_template("donorView.html", value=dataObj)

# return bloodbank view
@app.route("/bloodbank")
def bloodbank():
    dataObj = {}
    cur.execute("SELECT * FROM blood_bank LIMIT 100")
    # print(cur.description)
    data = cur.fetchall()
    data1 = cur.description
    dataObj["table_cols"] = data1
    dataObj["table_rows"] = data
    return render_template("bloodbankView.html", value=dataObj)


@app.route("/submitForm", methods=["POST"])
def handle_query():
    queryResponseObj = {}
    request_data = request.form
    user_query = request_data.to_dict()
    # print(user_query["user_query"] + ' LIMIT 300')
    cur.execute(user_query["user_query"] + " LIMIT 300")
    columsNames = cur.description
    query_response = cur.fetchall()
    queryResponseObj["table_cols"] = columsNames
    queryResponseObj["table_rows"] = query_response
    return render_template("index.html", value=queryResponseObj)


# get nearest bloodbank to a hospital
@app.route("/get_nearest_bb", methods=["POST"])
def get_nearest_bb():
    nearestBloodBankObj = {}
    search_data = request.form.to_dict()
    # print(search_data["hospital_name"])
    query = "select bbid,distance from get_nearest_bloodbanks({}, {})".format(
        search_data["hospital_name"], search_data["bb_distance"]
    )
    cur.execute(query)
    queryResponse = cur.fetchall()
    columsNames = cur.description
    nearestBloodBankObj["table_cols"] = columsNames
    nearestBloodBankObj["table_rows"] = queryResponse
    return render_template("hospitalSearch.html", value=nearestBloodBankObj)


# get all hospitals a patient admitted to
@app.route("/get_patient_hospitals", methods=["POST"])
def get_patient_hospitals():
    patientHospitalObj = {}
    search_data = request.form.to_dict()
    # print(search_data["patient_name"])
    query = "select * from hospital where hid in(select hid from patient p join patient_hospital_blood_bank phb USING(pid) WHERE pid=1034)".format(
        search_data["patient_name"]
    )
    cur.execute(query)
    queryResponse = cur.fetchall()
    columsNames = cur.description
    patientHospitalObj["table_cols"] = columsNames
    patientHospitalObj["table_rows"] = queryResponse
    return render_template("patientSearch.html", value=patientHospitalObj)

# get new patient insert form
@app.route("/get_new_patient_form", methods=["POST"])
def get_new_patient_form():
    # patientHospitalObj = {}
    form_data = request.form.to_dict()
    form_fn = form_data['first_name']
    form_ln = form_data['last_name']
    form_age = form_data['age']
    form_bloodGroup = form_data['blood_group']
    form_phone = form_data['phone']
    form_buildingNo = form_data['building_no']
    form_streetName = form_data['street_name']
    form_city = form_data['city']
    form_zipcode = form_data['zipcode']
    form_state = form_data['state_id']
    # get state_id from state table
    get_stateid_query = "select state_id from state where state_id='{}'".format(form_state)
    cur.execute(get_stateid_query)
    form_state_id = cur.fetchall()[0][0]

    insert_into_address_query = "INSERT INTO address (building_no, street_name, city, zipcode, state_id) VALUES ({},'{}','{}',{},'{}');".format(form_buildingNo,form_streetName,form_city,form_zipcode,form_state_id)
    cur.execute(insert_into_address_query)

    # get aid from address
    print(cur.fetchone())
    # queryResponse = cur.fetchall()
    # columsNames = cur.description
    # patientHospitalObj["table_cols"] = columsNames
    # patientHospitalObj["table_rows"] = queryResponse
    # return render_template("patientSearch.html")
    return cur.fetchone()


# insert a new patient into database
@app.route("/insert_new_patient")
def insert_new_patient():
    return render_template("newPatient.html")


# handle hospital search
@app.route("/hospital_search")
def hospital_search():
    # print(fetchHospitalData())
    return render_template("hospitalSearch.html", value=fetchHospitalData())


# handle patient search
@app.route("/patient_search")
def patient_search():
    # print(fetchHospitalData())
    return render_template("patientSearch.html", value=fetchPatientData())


# handle bloodbank details
@app.route("/bloodbankdetails/<bbid>", methods=["POST", "GET"])
def bloodbankdetails(bbid):
    bloodBankObj = {}
    # print('RA---',request.args.to_dict())
    # print("bbid--", bbid)
    query = "select * from blood_bank where bbid=({})".format(bbid)
    cur.execute(query)
    columsNames = cur.description
    bloodBankObj["table_cols"] = columsNames
    bloodBankObj["table_rows"] = cur.fetchall()
    return render_template("hospitalSearch.html", value=bloodBankObj)


### functions ###
# get all hospitals
def fetchHospitalData():
    cur.execute("select hid,name from hospital LIMIT 100")
    resource = cur.fetchall()

    if resource is None:
        abort(404, description="Resource not found")

    return resource


# get all patients
def fetchPatientData():
    cur.execute("select * from patient LIMIT 100")
    resource = cur.fetchall()

    if resource is None:
        abort(404, description="Resource not found")

    return resource


# cache control
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r


# main
if __name__ == "__main__":
    app.run(debug=True)
