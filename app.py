from flask import Flask, render_template, request, redirect, flash, url_for
from flask import jsonify
import oracledb
 
app = Flask(__name__)
 
d = r"C:\oracle\instantclient_21_12"
oracledb.init_oracle_client(lib_dir=d)
print(oracledb.clientversion())
 
def get_db_connection():
    dsn_t = oracledb.makedsn('navydb.artg.arizona.edu', 1521, 'ORCL')
    connection = oracledb.connect(user="mis531groupS1H", password="A4.PRp@:r5HFA/X", dsn=dsn_t, disable_oob=True)
    return connection




@app.route('/')
def index():
    return render_template('index.html', loginStatus = False)

@app.route('/loggedIn')
def indexLoggedIn():
    return render_template('index.html', loginStatus = True)

@app.route('/signout')
def signOut():
    return render_template('index.html', loginStatus = False)

@app.route('/signup')
def signup():
    return render_template('signup.html', loginStatus = False)



@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/login')
def login():
    return render_template('login.html')

 
@app.route('/loginAuth', methods=['POST'])
def loginAuth():
    connection = get_db_connection()
    userID = request.form['userID'].strip()
    password = request.form['password'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM AUTHENTICATION where AUTHID = :userID and PASSWORD = :password", userID = userID, password = password)
        authDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    if len(authDetails) > 0:
        return render_template('index.html', loginStatus = True)

    return render_template('login.html', alert = 'Invalid Credentials')

@app.route('/stationDetails', methods=['POST'])
def stationDetails():
    connection = get_db_connection()
    city = request.form['city']

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM stations where city = :city", city = city)
        stationDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    if len(stationDetails) > 0:
        # return jsonify(stationDetails)
        return render_template('stations.html', DetailsAvailable = True, stationDetails = stationDetails)

    return render_template('stations.html', alert = 'No Stations Found')


# =================================================================================================
# CUSTOMERS
@app.route('/customers')
def customers():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM CUSTOMERS order by CustID")
        custDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(custDetails)
    return render_template('customers.html', customers = custDetails)


@app.route('/insertCustomers', methods=['POST'])
def insertCustomers():
    connection = get_db_connection()
    firstName = request.form['firstName'].strip()
    lastName = request.form['lastName'].strip()
    email = request.form['email'].strip()
    age = request.form['age'].strip()
    city = request.form['city'].strip()
    state = request.form['state'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO CUSTOMERS (FNAME, LNAME, EMAIL, AGE, CITY, STATE) VALUES (:firstName, :lastName, :email, :age, :city, :state)", firstName = firstName, lastName = lastName, email = email, age = age, city = city, state = state)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('customers'))


@app.route('/updateCustomers', methods=['POST'])
def updateCustomers():
    connection = get_db_connection()
    custID = request.form['custID'].strip()
    firstName = request.form['firstName'].strip()
    lastName = request.form['lastName'].strip()
    email = request.form['email'].strip()
    age = request.form['age'].strip()
    city = request.form['city'].strip()
    state = request.form['state'].strip()

    colNames = ["FNAME", "LNAME", "EMAIL", "AGE", "CITY", "STATE"]
    colValues = [firstName, lastName, email, age, city, state]
    try:
        cursor = connection.cursor()
        for index in range(len(colValues)):
            if colValues[index] != "":
                # cursor.execute("UPDATE CUSTOMERS SET FNAME = :colValue WHERE CUSTID = :custID", colName = colNames[index], colValue = colValues[index], custID = custID)
                sqlQuery = "UPDATE CUSTOMERS SET " + colNames[index] + " = :colValue WHERE CUSTID = :custID"
                cursor.execute(sqlQuery, colValue = colValues[index], custID = custID)

    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()
    

    return redirect(url_for('customers'))


@app.route('/deleteCustomers', methods=['POST'])
def deleteCustomers():
    connection = get_db_connection()
    custID = request.form['custID'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM  CUSTOMERS WHERE CUSTID = :custID", custID = custID)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('customers'))

# ===============================================================================================================
       
# ===================================================================================================================
# Stations
@app.route('/stations')
def stations():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM STATIONS order by STATIONID")
        stationDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(stationDetails)
    return render_template('stations.html', stationDetails=stationDetails)

@app.route('/insertStations', methods=['POST'])
def insertStations():
    connection = get_db_connection()
    sName = request.form['sName'].strip()
    city = request.form['city'].strip()
    bikeCapacity = request.form['bikeCapacity'].strip()
    AvailBikes = request.form['AvailBikes'].strip()
    mBikes = request.form['mBikes'].strip()

    # Station total Bike Capacity should be greater than or equal to the sum of available bikes and maintenance bikes
    if (bikeCapacity < AvailBikes+mBikes):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM STATIONS order by STATIONID")
            stationDetails = cursor.fetchall()
        finally:
            # Close the cursor and connection in a finally block
            cursor.close()
            connection.close()
        return render_template('stations.html', stationDetails=stationDetails, alert = 'Invalid Bike Capacity')

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO STATIONS (SNAME, CITY, BIKECAPACITY, AVAILABLEBIKES, MAINTENANCEBIKES) VALUES (:sName, :city, :bikeCapacity, :AvailBikes, :mBikes)", sName = sName, city = city, bikeCapacity = bikeCapacity, AvailBikes = AvailBikes, mBikes = mBikes)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('stations'))


@app.route('/updateStations', methods=['POST'])
def updateStations():
    connection = get_db_connection()
    sID = request.form['sID'].strip()
    sName = request.form['sName'].strip()
    city = request.form['city'].strip()
    bikeCapacity = request.form['bikeCapacity'].strip()
    AvailBikes = request.form['AvailBikes'].strip()
    mBikes = request.form['mBikes'].strip()

    colNames = ["STATIONID", "SNAME", "CITY", "BIKECAPACITY", "AVAILABLEBIKES", "MAINTENANCEBIKES"]
    colValues = [sID, sName, city, bikeCapacity, AvailBikes, mBikes]
    try:
        cursor = connection.cursor()
        if (bikeCapacity < AvailBikes+mBikes):
            
            cursor.execute("SELECT * FROM STATIONS order by STATIONID")
            stationDetails = cursor.fetchall()
            return render_template('stations.html', stationDetails=stationDetails, alert = 'Invalid Bike Capacity')
    
        for index in range(len(colValues)):
            if colValues[index] != "":
                sqlQuery = "UPDATE STATIONS SET " + colNames[index] + " = :colValue WHERE STATIONID = :sID"
                cursor.execute(sqlQuery, colValue = colValues[index], sID = sID)

    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()
    

    return redirect(url_for('stations'))


@app.route('/deleteStations', methods=['POST'])
def deleteStations():
    connection = get_db_connection()
    sID = request.form['sID'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM STATIONS WHERE STATIONID = :sID", sID = sID)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('stations'))

# =========================================================================================================================
# Vendors

@app.route('/vendors')
def vendors():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM VENDORS order by VENDORID")
        vendorDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(vendorDetails)
    return render_template('vendors.html', vendorDetails=vendorDetails)

@app.route('/insertVendors', methods=['POST'])
def insertVendors():
    connection = get_db_connection()
    vName = request.form['vName'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip()
    city = request.form['city'].strip()
    state = request.form['state'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO VENDORS (VNAME, VPHONE, VEMAIL, CITY, STATE) VALUES (:vName, :phone, :email, :city, :state)", vName = vName, phone = phone, email = email, city = city, state = state)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('vendors'))



@app.route('/updateVendors', methods=['POST'])
def updateVendors():
    connection = get_db_connection()
    vID = request.form['vID'].strip()
    vName = request.form['vName'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip()
    city = request.form['city'].strip()
    state = request.form['state'].strip()

    colNames = ["VENDORID", "VNAME", "VPHONE", "VEMAIL", "CITY", "STATE"]
    colValues = [vID, vName, phone, email, city, state]
    try:
        cursor = connection.cursor()
        for index in range(len(colValues)):
            if colValues[index] != "":
                # cursor.execute("UPDATE CUSTOMERS SET FNAME = :colValue WHERE CUSTID = :custID", colName = colNames[index], colValue = colValues[index], custID = custID)
                sqlQuery = "UPDATE VENDORS SET " + colNames[index] + " = :colValue WHERE VENDORID = :vID"
                cursor.execute(sqlQuery, colValue = colValues[index], vID = vID)

    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('vendors'))


@app.route('/deleteVendors', methods=['POST'])
def deleteVendors():
    connection = get_db_connection()
    vID = request.form['vID'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM VENDORS WHERE VENDORID = :vID", vID = vID)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('vendors'))

# ==================================================================================================================================================
# Employees

def check_deptid(deptid):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM DEPARTMENTS")
        deptDetails = cursor.fetchall()
        deptIDs = [record[0] for record in deptDetails]

        # DeptID that is not in departments table should not be accepted
        if deptid not in deptIDs:
            return False
        else:
            return True
        
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

@app.route('/employees')
def employees():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM EMPLOYEES order by EMPID")
        empDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(empDetails)
    return render_template('employees.html', empDetails=empDetails) 

@app.route('/insertEmployees', methods=['POST'])
def insertEmployees():
    connection = get_db_connection()
    firstName = request.form['firstName'].strip()
    lastName = request.form['lastName'].strip()
    email = request.form['email'].strip()
    gender = request.form['gender'].strip()
    age = request.form['age'].strip()
    deptID = request.form['deptID'].strip()

    try:
        cursor = connection.cursor()
        deptIDCheck = check_deptid(deptID)

        # DeptID that is not in departments table should not be accepted
        if not deptIDCheck:
            cursor.execute("SELECT * FROM EMPLOYEES order by EMPID")
            empDetails = cursor.fetchall()
            return render_template('employees.html', alert = 'Invalid Department ID', empDetails=empDetails)
        
        cursor.execute("INSERT INTO EMPLOYEES (FNAME, LNAME, EMAIL, GENDER, AGE, DEPARTMENTID) VALUES (:firstName, :lastName, :email, :gender, :age, :deptID)", 
                       firstName = firstName, lastName = lastName, email = email, gender = gender, age = age, deptID = deptID)
        
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('employees'))

@app.route('/updateEmployees', methods=['POST'])
def updateEmployees():
    connection = get_db_connection()
    empID = request.form['empID'].strip()
    firstName = request.form['firstName'].strip()
    lastName = request.form['lastName'].strip()
    email = request.form['email'].strip()
    age = request.form['age'].strip()
    deptID = request.form['deptID'].strip()

    colNames = ["EMPID", "FName", "LNAME", "EMAIL", "AGE", "DEPARTMENTID"]
    colValues = [empID, firstName, lastName, email, age, deptID]
    try:
        cursor = connection.cursor()
        deptIDCheck = True if deptID=="" else check_deptid(deptID)

        # DeptID that is not in departments table should not be accepted
        if not deptIDCheck:
            cursor.execute("SELECT * FROM EMPLOYEES order by EMPID")
            empDetails = cursor.fetchall()
            return render_template('employees.html', alert = 'Invalid Department ID', empDetails=empDetails)

        for index in range(len(colValues)):
            if colValues[index] != "":
                # cursor.execute("UPDATE CUSTOMERS SET FNAME = :colValue WHERE CUSTID = :custID", colName = colNames[index], colValue = colValues[index], custID = custID)
                sqlQuery = "UPDATE EMPLOYEES SET " + colNames[index] + " = :colValue WHERE EMPID = :empID"
                cursor.execute(sqlQuery, colValue = colValues[index], empID = empID)

    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('employees'))


@app.route('/deleteEmployees', methods=['POST'])
def deleteEmployees():
    connection = get_db_connection()
    empID = request.form['empID'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM EMPLOYEES WHERE EMPID = :empID", empID = empID)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('employees'))

# ===========================================================================================================================

# Bike Models
# 1. check for vendor ID referential integrity before inserting.
# 2. Referential integrity while updating vendor ID

def check_vendorid(vendorid):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM VENDORS")
        vendorDetails = cursor.fetchall()
        vendorIDs = [record[0] for record in vendorDetails]

        # VendorID that is not in vendors table should not be accepted
        if vendorid not in vendorIDs:
            return False
        else:
            return True
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

@app.route('/bikeModels')
def bikeModels():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM BIKE_MODELS order by MODELID")
        bikeDetails = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(bikeDetails)
    return render_template('bikeModels.html', bikeDetails=bikeDetails) 


@app.route('/insertModel', methods=['POST'])
def insertModel():
    connection = get_db_connection()
    modelName = request.form['modelName'].strip()
    type = request.form['type'].strip()
    cost = request.form['cost'].strip()
    vendorID = request.form['vendorID'].strip()

    try:
        cursor = connection.cursor()
        vendorIDCheck = check_vendorid(vendorID)

        # vendorID that is not in vendors table should not be accepted
        if not vendorIDCheck:
            cursor.execute("SELECT * FROM BIKE_MODELS order by MODELID")
            bikeDetails = cursor.fetchall()
            return render_template('bikeModels.html', alert = 'Invalid Vendor ID', bikeDetails=bikeDetails)

        cursor.execute("INSERT INTO BIKE_MODELS (MODELNAME, TYPE, MODELCOST, VENDORID) VALUES (:modelName, :type, :cost, :vendorID)", modelName = modelName, type = type, cost = cost, vendorID = vendorID) 
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('bikeModels'))


@app.route('/updateModels', methods=['POST'])
def updateModels():
    connection = get_db_connection()
    modelID = request.form['modelID'].strip()
    modelName = request.form['modelName'].strip()
    type = request.form['type'].strip()
    cost = request.form['cost'].strip()
    vendorID = request.form['vendorID'].strip()

    colNames = ["MODELID", "MODELNAME", "TYPE", "MODELCOST", "VENDORID"]
    colValues = [modelID, modelName, type, cost, vendorID]
    try:
        cursor = connection.cursor()
        vendorIDCheck = True if vendorID=="" else check_vendorid(vendorID)

        # vendorID that is not in vendors table should not be accepted
        if not vendorIDCheck:
            cursor.execute("SELECT * FROM BIKE_MODELS order by MODELID")
            bikeDetails = cursor.fetchall()
            return render_template('bikeModels.html', alert = 'Invalid Vendor ID', bikeDetails=bikeDetails)

        for index in range(len(colValues)):
            if colValues[index] != "":
                # cursor.execute("UPDATE CUSTOMERS SET FNAME = :colValue WHERE CUSTID = :custID", colName = colNames[index], colValue = colValues[index], custID = custID)
                sqlQuery = "UPDATE BIKE_MODELS SET " + colNames[index] + " = :colValue WHERE MODELID = :modelID"
                cursor.execute(sqlQuery, colValue = colValues[index], modelID = modelID)

    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('bikeModels'))

@app.route('/deleteModels', methods=['POST'])
def deleteModels():
    connection = get_db_connection()
    modelID = request.form['modelID'].strip()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM BIKE_MODELS WHERE MODELID = :modelID", modelID = modelID)
    finally:
        # Close the cursor and connection in a finally block
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('bikeModels'))

# =================================================================================================================================================

# Scenarios
@app.route('/scenarios')
def scenarios():
    return render_template('scenario.html')


#1. Top customers based on maximum rental time
@app.route('/scenario1')
def scenario1():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
                with rideTime as (select tripid, (extract(HOUR FROM ((endtime)-(starttime))) * 3600 + extract(MINUTE FROM ((endtime)-(starttime))
                    ) * 60 + extract(SECOND FROM ((endtime)-(starttime)))) as time1, age, c.custid, c.fname,c.lname from customers c 
                inner join trips t on c.custid = t.custid)
                select custid, fname, lname, sum(time1) as SumTime 
                from rideTime
                group by custid,fname,lname
                order by SumTime desc
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario1.html', queryOutput=queryOutput) 


#2. Calculate difference between the revenue for quarters based on the standalone table
@app.route('/scenario2')
def scenario2():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
                WITH Quarters AS (         
                            SELECT
                                    YEAR,
                                    CEIL(MONTH / 3) AS QUARTER,
                                    sum(MONTHTOTAL) as monthtotal
                                FROM
                                    monthly_revenue
                                    group by year, ceil(month/3)
                                    )
                            SELECT
                                YEAR,
                                LAG(QUARTER) OVER (ORDER BY YEAR, QUARTER) AS PREVIOUS_QUARTER,
                                QUARTER AS CURRENT_QUARTER,
                                MONTHTOTAL - LAG(MONTHTOTAL) OVER (ORDER BY YEAR, QUARTER) AS REVENUE_DIFFERENCE
                            FROM
                                Quarters
                            ORDER BY
                                YEAR, QUARTER
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario2.html', queryOutput=queryOutput) 

#3. Hotspot locations based on zipcodes/stations from where most of the trips are made
@app.route('/scenario3')
def scenario3():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
                with hotspotsPick as (select * from trips t
                    left join bikes b using(Bikeid)
                    left join stations s using(stationid))
                select h.pickupstationid, count(h.pickupstationid) as NoOfSt, ss.city
                    from hotspotsPick h	
                    left join stations ss on h.pickupstationid = ss.stationid
                group by h.pickupstationid, ss.city
                order by NoOfSt desc
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario3.html', queryOutput=queryOutput)


#4. Calculate the time between consecutive bike rentals for each bike trips
@app.route('/scenario4')
def scenario4():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
                WITH TripDetails AS (
                            SELECT
                                tripID,
                                bikeID,
                                startTime,
                                endTime,
                                LEAD(startTime) OVER (PARTITION BY bikeID ORDER BY startTime) AS nextStartTime
                            FROM
                                TRIPS
                        )
                        SELECT
                            tripID,
                            bikeID,
                            startTime,
                            endTime,
                            nextStartTime,
                            nextStartTime - endTime AS timeBetweenRentals
                        FROM
                            TripDetails
                        ORDER BY
                            bikeID, startTime
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario4.html', queryOutput=queryOutput)

#5. Analyzing the frequency of the most common type of service done on bike and/or station maintenance
@app.route('/scenario5')
def scenario5():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQueryBike = """
               WITH ServiceCounts AS (
                    SELECT
                        EXTRACT(YEAR FROM m_Start_Time) AS maintenanceYear,
                        typeOfService,
                        COUNT(*) AS serviceCount
                    FROM
                        BIKE_MAINTENANCE
                    GROUP BY
                        EXTRACT(YEAR FROM m_Start_Time),
                        typeOfService
                )
                SELECT
                    maintenanceYear,
                    typeOfService,
                    serviceCount
                FROM
                    ServiceCounts
                ORDER BY
                    maintenanceYear, typeOfService
                """
        cursor.execute(sqlQueryBike)
        queryOutputBike = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario5.html', queryOutput=queryOutputBike)

#6. Top customers with most overdue/defaulted payment
@app.route('/scenario6')
def scenario6():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               WITH CustomerPayments AS (
                        SELECT
                            c.custID,
                            c.fName || ' ' || c.lName AS name,
                            SUM(p.amount) AS totalAmount,
                            RANK() OVER (ORDER BY SUM(p.amount) DESC) AS paymentRank
                        FROM
                            CUSTOMERS c
                        JOIN
                            PAYMENT p ON c.custID = p.custid
                        WHERE
                            p.typeOfPayment = 'D'
                        GROUP BY
                            c.custID, c.fName, c.lName
                    )
                    SELECT
                        paymentRank,name,
                        totalAmount
                        
                    FROM
                        CustomerPayments
                    WHERE
                        paymentRank <= 5
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario6.html', queryOutput=queryOutput)


#7. Top customers with most overdue/defaulted payment
@app.route('/scenario7')
def scenario7():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               WITH CustomerCategories AS (
                    SELECT
                        c.custID,
                        c.fName || ' ' || c.lName AS name,
                        COUNT(p.paymentID) AS numberOfPayments,
                        CASE
                            WHEN COUNT(p.paymentID) >= 20 THEN 'Platinum'
                            WHEN COUNT(p.paymentID) >= 15 THEN 'Gold'
                            WHEN COUNT(p.paymentID) >= 10 THEN 'Silver'
                            ELSE 'Regular'
                        END AS category
                    FROM
                        CUSTOMERS c
                    LEFT JOIN
                        PAYMENT p ON c.custID = p.custid
                    GROUP BY
                        c.custID, c.fName, c.lName
                )
                SELECT
                    name,
                    numberOfPayments,
                    category
                FROM
                    CustomerCategories
                order by numberofpayments desc
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario7.html', queryOutput=queryOutput)


#8. Calculate the total revenue generated from active subscribers in the last month
@app.route('/scenario8')
def scenario8():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               SELECT c.custID, c.fName || ' ' || c.lName AS CustomerName, COUNT(co.complaintID) AS UnresolvedComplaints
                FROM CUSTOMERS c
                inner JOIN COMPLAINTS co ON c.custID = co.custID AND co.status = 'P'
                GROUP BY c.custID, c.fName, c.lName
                ORDER BY UnresolvedComplaints DESC
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario8.html', queryOutput=queryOutput)

#9. Calculate the percentage of customers with an active subscription
@app.route('/scenario9')
def scenario9():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               with activeCust as (select custid, fname, lname, age, city, planid
                from customers 
                inner join subscription_status using(custid)
                where activestatus = 'Y' and haspayed='Y' and enddate > sysdate 
                order by custid),

                totalCust as (select count(custid) as total from customers)

                select (count(a.custid)/total * 100) as "Percent of Active Subscribers"
                from activeCust a ,totalCust t
                group by total
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario9.html', queryOutput=queryOutput)

#10. Subscription model distribution
@app.route('/scenario10')
def scenario10():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               select planid, count(custid) as CtCust
                from subscription_status
                group by planid
                order by CtCust desc
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario10.html', queryOutput=queryOutput)

#11. Most popular bike models derived from trips
@app.route('/scenario11')
def scenario11():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               WITH BikeTripsCount AS (
                        SELECT
                            b.modelID,
                            bm.modelName,
                            COUNT(t.tripID) AS tripCount
                        FROM
                            BIKES b
                        JOIN
                            TRIPS t ON b.bikeID = t.bikeID
                        JOIN
                            BIKE_MODELS bm ON b.modelID = bm.modelID
                        GROUP BY
                            b.modelID, bm.modelName
                    )
                    SELECT
                        modelID,
                        modelName,
                        tripCount
                    FROM
                        (
                            SELECT
                                modelID,
                                modelName,
                                tripCount,
                                RANK() OVER (ORDER BY tripCount DESC) AS rnk
                            FROM
                                BikeTripsCount
                        )
                    WHERE
                        rnk <= 3
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario11.html', queryOutput=queryOutput)


#12. Most popular bike models derived from trips
@app.route('/scenario12')
def scenario12():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sqlQuery = """
               WITH OnCallEmployeeComplaints AS (
                        SELECT
                            e.empID,
                            e.fName || ' ' || e.lName AS employeeName,
                            COUNT(c.complaintID) AS numberOfComplaints
                        FROM
                            EMPLOYEES e
                        JOIN
                            COMPLAINTS c ON e.empID = c.empID
                        WHERE
                            e.isOnCallSupport = 'Y'
                        GROUP BY
                            e.empID, e.fName, e.lName
                        order by numberOfComplaints desc
                    )
                    SELECT
                        employeeName,
                        numberOfComplaints
                    FROM
                        OnCallEmployeeComplaints
                    where rownum = 1
                    ORDER BY
                        numberOfComplaints DESC
                """
        cursor.execute(sqlQuery)
        queryOutput = cursor.fetchall()
    finally:
        # Close the cursor and connection in a finally block
        cursor.close()
        connection.close()

    # return jsonify(queryOutput)
    return render_template('scenario12.html', queryOutput=queryOutput)


if __name__ == '__main__':
    app.run(debug=True)