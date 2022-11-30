from flask import Flask, render_template, request, abort
import psycopg2
from datetime import date

today = date.today()

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost", database="CentralizedBloodBank", user="postgres", password="password"
)
conn.autocommit = True
cur = conn.cursor()



@app.route("/")
def base():
    cur.execute("SELECT sum(apos), sum(aneg), sum(bpos), sum(bneg), sum(abpos), sum(abneg), sum(opos), sum(oneg)  FROM blood_bank;")
    blood_units = cur.fetchall()
    return render_template("base.html", value = blood_units)


@app.route("/donate", methods = ["POST", "GET"])
def donate():
    if request.method == "POST":
        requested_data = request.form.to_dict()
        did = requested_data["did"]
        bbid = requested_data["bbid"]
        # update user last_given
        # fetch donor blood group
        # update bbid corresponding blood group of ID
        cur.execute("update donor set last_given =%s where did=%s", (today.strftime("%m/%d/%y"), str(did)))
        cur.execute("select blood_type from donor where did="+str(did)+";")
        bloodbankMap = {"A+":"apos", "A-":"aneg", "B+":"bpos", "B-":"bneg", "AB+":"abpos", "AB-":"abneg", "O+":"opos", "O-":"oneg"}
        value = cur.fetchall()
        cur.execute("select "+bloodbankMap[value[0][0]]+" from blood_bank where bbid="+str(bbid)+";")
        blood_type_units = cur.fetchall()[0][0]
        cur.execute("update blood_bank set "+str(bloodbankMap[value[0][0]])+"="+str(blood_type_units+1)+" where bbid="+str(bbid)+";")
        value = {}
        return render_template("donateForm.html", value = value)
    else:
        value = {}
        return render_template("donateForm.html", value= value)


@app.route("/address")
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
    return render_template("recordView.html", value=queryResponseObj)


# return new patient form
@app.route("/new_blood_bank")
def new_blood_bank():
    # queryResponseObj = {}
    # request_data = request.form
    # user_query = request_data.to_dict()
    # # print(user_query["user_query"] + ' LIMIT 300')
    # cur.execute(user_query["user_query"] + " LIMIT 300")
    # columsNames = cur.description
    # query_response = cur.fetchall()
    # queryResponseObj["table_cols"] = columsNames
    # queryResponseObj["table_rows"] = query_response
    return render_template("newBloodBank.html")


# TO-DO : get new hospital form data and insert into table


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
    form_fn = form_data["first_name"]
    form_ln = form_data["last_name"]
    form_age = form_data["age"]
    form_bloodGroup = form_data["blood_group"]
    form_phone = form_data["phone"]
    form_buildingNo = form_data["building_no"]
    form_streetName = form_data["street_name"]
    form_city = form_data["city"]
    form_zipcode = form_data["zipcode"]
    form_state = form_data["state_id"]
    # get state_id from state table
    get_stateid_query = "select state_id from state where state_id='{}'".format(
        form_state
    )
    cur.execute(get_stateid_query)
    form_state_id = cur.fetchall()[0][0]

    insert_into_address_query = "INSERT INTO address (building_no, street_name, city, zipcode, state_id) VALUES ({},'{}','{}',{},'{}');".format(
        form_buildingNo, form_streetName, form_city, form_zipcode, form_state_id
    )
    cur.execute(insert_into_address_query)

   # get aid from addr
    get_aid = "select aid from address where building_no='{}' and street_name='{}' and zipcode='{}'".format(form_buildingNo,form_streetName,form_zipcode)
    cur.execute(get_aid)
    new_aid = cur.fetchall()[0][0]
    print(new_aid)

    insert_new_patient = "INSERT into patient (first_name,last_name,age,blood_group,phone,aid) VALUES('{}','{}',{},'{}','{}',{})".format(form_fn,form_ln,form_age,form_bloodGroup,form_phone,new_aid)
    cur.execute(insert_new_patient)
    # cur.fetchall()

    newData = {}
    get_new_donor = "select * from patient where phone='{}' and aid={}".format(form_phone,new_aid)
    cur.execute(get_new_donor)
    columsNames = cur.description
    newData["table_cols"] = columsNames
    newData["table_rows"] = cur.fetchall()
    # print(newData)
    return render_template('recordView.html',value=newData)


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


### UPDATE functions ###
@app.route("/show_patient_ids_update")
def show_patient_ids_update():
    patientIDsOBJ = {}
    # print('RA---',request.args.to_dict())
    # print("bbid--", bbid)
    query = "select pid,first_name from patient ORDER BY pid LIMIT 100"
    cur.execute(query)
    columsNames = cur.description
    patientIDsOBJ["table_cols"] = columsNames
    patientIDsOBJ["table_rows"] = cur.fetchall()
    return render_template("showPatientIDS.html", value=patientIDsOBJ)


# return patient details to update
@app.route("/show_patient_details_form", methods=["POST"])
def show_patient_details_form():
    patientData = {}
    pid = request.form.to_dict()["pid"]
    query1 = "select * from patient where pid={}".format(pid)
    cur.execute(query1)
    patientData["details"] = cur.fetchall()
    patient_aid = patientData["details"][0][6]
    query2 = "select * from address where aid={}".format(patient_aid)
    cur.execute(query2)
    patientData["addr"] = cur.fetchall()
    print(patientData)
    return render_template("updatePatientDetails.html", value=patientData)


# return updated patient details
@app.route("/get_updated_patient_details", methods=["POST"])
def get_updated_patient_details():
    patientIDsOBJ = {}
    patientData = request.form.to_dict()
    # print(patientData)
    pid = patientData["pid"]
    fn = patientData["first_name"]
    ln = patientData["last_name"]
    age = patientData["age"]
    bg = patientData["blood_group"]
    phone = patientData["phone"]
    insert_into_patient_query = "UPDATE patient SET first_name = '{}', last_name = '{}', age = {}, blood_group = '{}', phone='{}' WHERE pid = {};".format(
        fn, ln, age, bg, phone, pid
    )
    cur.execute(insert_into_patient_query)
    query = "select * from patient where pid={}".format(pid)
    cur.execute(query)
    columsNames = cur.description
    patientIDsOBJ["table_cols"] = columsNames
    patientIDsOBJ["table_rows"] = cur.fetchall()
    return render_template("patientView.html", value=patientIDsOBJ)


# return BloodBank details to delete
@app.route("/show_bloodbank_ids_delete")
def show_bloodbank_ids_delete():
    bloodBank = {}
    query = "select bbid,name from blood_bank LIMIT 100"
    cur.execute(query)
    columsNames = cur.description
    bloodBank["table_cols"] = columsNames
    bloodBank["table_rows"] = cur.fetchall()
    return render_template("showBloodBankIDS.html", value=bloodBank)


# return bloodbank details form
@app.route("/show_bloodbank_details_form", methods=["POST"])
def show_bloodbank_details_form():
    bloodbankData = {}
    bbid = request.form.to_dict()["bbid"]
    query1 = "select * from blood_bank where bbid={}".format(bbid)
    cur.execute(query1)
    bloodbankData["details"] = cur.fetchall()
    bloodbank_aid = bloodbankData["details"][0][6]
    query2 = "select * from address where aid={}".format(bloodbank_aid)
    cur.execute(query2)
    bloodbankData["addr"] = cur.fetchall()
    print(bloodbankData)
    return render_template("updateBloodBankdetails.html", value=bloodbankData)


# delete a bloodbank
@app.route("/delete_blood_bank", methods=["POST"])
def delete_blood_bank():
    bloodbankOBJ = {}
    bloodBankData = request.form.to_dict()
    # print(patientData)
    bbid = bloodBankData["bbid"]
    name = bloodBankData["name"]
    apos = bloodBankData["apos"]
    aneg = bloodBankData["aneg"]
    bpos = bloodBankData["bpos"]
    bneg = bloodBankData["bneg"]
    opos = bloodBankData["opos"]
    oneg = bloodBankData["oneg"]
    abpos = bloodBankData["abpos"]
    abneg = bloodBankData["abneg"]
    phone = bloodBankData["phone"]
    mail = bloodBankData["mail"]
    print(bloodBankData)
    delete_from_bloodbank_query = "delete from blood_bank where bbid={}".format(bbid)
    cur.execute(delete_from_bloodbank_query)
    # query = "select * from patient where pid={}".format(pid)
    # cur.execute(query)
    # columsNames = cur.description
    # bloodbankOBJ["table_cols"] = columsNames
    # bloodbankOBJ["table_rows"] = cur.fetchall()
    return "<h2>bbid={} delete sucess.</h2>".format(bbid)


# join new patient form
@app.route("/join_new_patient")
def join_new_patient():
    patientIDsOBJ = {}
    # print('RA---',request.args.to_dict())
    # print("bbid--", bbid)
    query = "select pid,first_name from patient ORDER BY pid LIMIT 100"
    cur.execute(query)
    columsNames = cur.description
    patientIDsOBJ["table_cols"] = columsNames
    patientIDsOBJ["table_rows"] = cur.fetchall()
    hospital_query = "select hid,name from hospital ORDER BY hid LIMIT 100"
    cur.execute(hospital_query)
    patientIDsOBJ["htable_rows"] = cur.fetchall()
    return render_template("joinNewPatient.html", value=patientIDsOBJ)


# get patient-hospital form
@app.route("/get_patient_hospital_form", methods=["POST"])
def get_patient_hospital_form():
    pid = request.form.to_dict()["pid"]
    hid = request.form.to_dict()["hid"]
    get_bb_from_hid = "select bbid from hospital_blood_bank where hid={}".format(hid)
    cur.execute(get_bb_from_hid)
    bbid = cur.fetchall()[0][0]

    insert_into_pbb = "INSERT into patient_hospital_blood_bank (pid, hid, bbid) VALUES({},{},{})".format(pid,hid,bbid)
    cur.execute(insert_into_pbb)
    newData = {}
    get_new_record = (
        "select pid,hid from patient_hospital_blood_bank where pid={} and bbid={}".format(
            pid, bbid
        )
    )
    cur.execute(get_new_record)
    columsNames = cur.description
    newData["table_cols"] = columsNames
    newData["table_rows"] = cur.fetchall()
    # print(newData)
    return render_template("recordView.html", value=newData)


# show new donor form
@app.route("/show_new_donor_form")
def show_new_donor_form():
    return render_template('newDonorForm.html')



# get new donor form data
@app.route("/get_new_donor_form_data", methods=["POST"])
def get_new_donor_form_data():
    new_donor_data = request.form.to_dict()
    fn = new_donor_data['first_name']
    ln = new_donor_data['last_name']
    phone = new_donor_data['phone']
    blood_type = new_donor_data['blood_type']
    age = new_donor_data['age']
    units = new_donor_data['units']
    last_given = new_donor_data['last_given']

    b_no = new_donor_data['building_no']
    street_name = new_donor_data['street_name']
    city = new_donor_data['city']
    state = new_donor_data['state_id']
    zipcode = new_donor_data['zipcode']

 # get state_id from state table
    get_stateid_query = "select state_id from state where state_id='{}'".format(
        state
    )
    cur.execute(get_stateid_query)
    form_state_id = cur.fetchall()[0][0]

    insert_into_address_query = "INSERT INTO address (building_no, street_name, city, zipcode, state_id) VALUES ({},'{}','{}','{}','{}');".format(
        b_no, street_name, city, zipcode, form_state_id
    )
    cur.execute(insert_into_address_query)

    # get aid from addr
    get_aid = "select aid from address where building_no='{}' and street_name='{}' and zipcode='{}'".format(b_no,street_name,zipcode)
    cur.execute(get_aid)
    new_aid = cur.fetchall()[0][0]
    print(new_aid)

    insert_new_donor = "INSERT into donor (first_name,last_name,phone,blood_type,age,units,last_given,aid) VALUES('{}','{}',{},'{}',{},{},'{}',{})".format(fn,ln,phone,blood_type,age,units,last_given,new_aid)
    cur.execute(insert_new_donor)
    # cur.fetchall()

    newData = {}
    get_new_donor = "select * from donor where phone='{}' and aid={}".format(phone,new_aid)
    cur.execute(get_new_donor)
    columsNames = cur.description
    newData["table_cols"] = columsNames
    newData["table_rows"] = cur.fetchall()
    # print(newData)
    return render_template('recordView.html',value=newData)


# show_donate_blood_form
@app.route("/show_donate_blood_form")
def show_donate_blood_form():
    patientIDsOBJ = {}
    # print('RA---',request.args.to_dict())
    # print("bbid--", bbid)
    query = "select did,first_name from donor ORDER BY did LIMIT 100"
    cur.execute(query)
    columsNames = cur.description
    patientIDsOBJ["table_cols"] = columsNames
    patientIDsOBJ["table_rows"] = cur.fetchall()
    hospital_query = "select bbid,name from blood_bank ORDER BY bbid LIMIT 100"
    cur.execute(hospital_query)
    patientIDsOBJ["htable_rows"] = cur.fetchall()
    return render_template("newDonorForm.html",value=patientIDsOBJ)

# donate blood
@app.route("/donate_blood", methods=["POST"])
def donate_blood():
    form_data = request.form.to_dict()
    did = form_data['did']
    bbid = form_data['bbid']
    u1 = form_data['units']

    get_blood_type = "select did,units from donor where did={} LIMIT 1".format(did)
    cur.execute(get_blood_type)
    # print(cur.fetchall())
    d = cur.fetchall()
    did = d[0][0]
    u2 = d[0][1]
    new_units = int(u1)+int(u2)
    
    increase_units = "UPDATE donor SET units={} where did={}".format(new_units,did)
    cur.execute(increase_units)
    newData = {}
    get_new_donor = "select * from donor where did={}".format(did)
    cur.execute(get_new_donor)
    columsNames = cur.description
    newData["table_cols"] = columsNames
    newData["table_rows"] = cur.fetchall()
    # print(newData)
    return render_template('recordView.html',value=newData)








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
