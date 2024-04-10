#Peter Alonzo- CSE 4701: Project 2

import mysql.connector
con = mysql.connector.connect(host="localhost", user="sqluser", password="password", database="company_database")
#This username/password is specific to my database, feel free to change it for grading purposes
mr_curse = con.cursor() #Creates cursor object to allow for SQL statement execution
mr_curse.execute("USE COMPANY_DATABASE") #Uses the company database I created in Project P1 (I named it COMPANY_DATABASE)

#Helper Functions
def return_count(name):
    mr_curse.execute('SELECT COUNT(*) FROM ' + name) #Returns count of records of the table "name"
    print("Record Count: ", (mr_curse.fetchone())[0]) #Prints count of records

def update_emp_record(ssn, column, element):
    query = 'UPDATE EMPLOYEE SET ' + column + ' = \'' + element + ' \' WHERE Ssn = ' + ssn
    #Updates employee table based on column passed in and changes it to the value of element
    mr_curse.execute(query) #Executes the query above
    con.commit() #Commits changes to database
    print("")

def unpack(data, multiple = False): #This takes query results and formats them nicely
    result = ''
    if data == None or len(data) == 0:
        return result
    for i in range(len(data) - 1):
        if multiple:
            result += (data[i])[0] + ', '
        else:
            result += data[i] + ' '
    if multiple:
        return result + (data[len(data) - 1])[0]
    return result + data[len(data) - 1]

#1: Add New Employee to Company Database
def add_employee(): 
    #Reads in all fields for a new EMPLOYEE record
    fName = input("Enter the first name of the employee you want to add: ")
    mInit = input("Enter their middle initial: ")
    lName = input("Enter their last name: ")
    ssn = input("Enter their SSN: ")
    bDate = input("Enter their birthdate as YYYY-MM-DD: ")
    address = input("Enter their address: ")
    sex = input("Enter their sex (M/F): ")
    salary = input("Enter their salary: ")
    super_ssn = input("Enter their supervisor's SSN: ")
    dno = input("Enter their department number: ")
    try:
        mr_curse.execute('INSERT INTO EMPLOYEE VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (fName, mInit, lName, ssn, bDate, address, sex, salary, super_ssn, dno))
        #This query takes the values entered by the user and inserts them into the correct columns to make a new EMPLOYEE record
    except mysql.connector.errors.IntegrityError: #Checks for any constraint violations with the primary/foreign keys
        print("\nError: Integrity Violation!!")
        con.rollback() #rolls back any changes/accesses to the database if INSERT INTO fails
        menu() #returns to menu
    except mysql.connector.errors.DataError: #Checks if incorrect data type was entered in a particular field
        print("\nError: Incorrect Type/Length of Data Entered!!")
        con.rollback() #rolls back any changes/accesses to the database if INSERT INTO fails
        menu()
    con.commit() #Assuming the record doesn't violate any constraints, the new record is committed to the database
    print("Employee Added Successfully!")
    return_count('EMPLOYEE') #Returns number of records in EMPLOYEE database
    menu()

#2: View Employee from Company Database
def view_employee():
    emp_ssn = input("Enter the SSN of the employee you're looking for: ")
    query = 'SELECT * FROM EMPLOYEE WHERE Ssn = ' + emp_ssn
    #Returns all fields for the desired employee
    query2 = 'SELECT F.Fname, F.Minit, F.Lname FROM EMPLOYEE AS E, EMPLOYEE AS F WHERE E.Super_ssn = F.Ssn AND E.Ssn = ' + emp_ssn
    #References EMPLOYEE table twice in order to find the full name of the desired employee's supervisor
    query3 = 'SELECT Dname FROM DEPARTMENT JOIN EMPLOYEE ON Dnumber=Dno WHERE Ssn = ' + emp_ssn
    #Returns the name of the department the desired employee works for
    query4 = 'SELECT Dependent_name FROM DEPENDENT JOIN EMPLOYEE ON Essn=Ssn WHERE Ssn = ' + emp_ssn
    #Returns the names of every dependent associated with the desired employee
    mr_curse.execute(query)
    print("Employee Info: ", mr_curse.fetchone())
    mr_curse.execute(query2)
    print("Supervisor Name: ", unpack(mr_curse.fetchone()))
    mr_curse.execute(query3)
    print("Department Name: ", unpack(mr_curse.fetchone()))
    mr_curse.execute(query4)
    print("Dependents: ", unpack(mr_curse.fetchall(), True))
    #Runs all queries and prints out the results
    menu()

#3 Modify Employee in Company Database
def modify_employee():
    emp_ssn = input("Enter the SSN of the employee you want to modify: ")
    mr_curse.execute('START TRANSACTION') 
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM EMPLOYEE WHERE Ssn = ' + emp_ssn + ' FOR UPDATE'
    #Returns all fields for the desired employee. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    keepUpdating = True
    while keepUpdating:
        mr_curse.execute(query) #Executes locking query and shows current values for desired employee
        print("Employee Info: ", mr_curse.fetchone()) #Prints out employee details
        choice = input("What do you wish to change? (Address, Sex, Salary, Super_ssn, Dno, Done to Exit): ")
        if choice != "Done":
            updated = input("Enter the new value for " + choice + ": ")
            update_emp_record(emp_ssn, choice, updated) #Calls helper function above to update record and commit its changes to the database
        else:
            keepUpdating = False
    con.rollback() #Rolls back any locking done to the record after we finish modifying it
    menu()
    
#4 Remove Employee from Company Database
def delete_employee():
    emp_ssn = input("Enter the SSN of the employee you want to delete: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM EMPLOYEE WHERE Ssn = ' + emp_ssn + ' FOR UPDATE'
    #Returns all fields for the desired employee. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query) #Executes locking query and shows current values for desired employee
    print("Employee Info: ", mr_curse.fetchone()) #Prints out employee details
    confirm = input("Are you sure you wish to delete this employee? (Yes/No): ")
    if confirm == 'No':
        con.rollback() #rolls back locking if user cancels deletion
        menu()
    query2 = 'DELETE FROM EMPLOYEE WHERE Ssn = ' + emp_ssn
    #This query will delete the desired employee
    try:
        mr_curse.execute(query2)
        #The query above is then executed
    except mysql.connector.errors.IntegrityError: #Checks for referential integrity constraint violations
        print("Error: Integrity Violation! -> This employee has dependencies. Please remove these first before deleting")
        con.rollback() #rolls back any changes/locks to the database if DELETE FROM fails
        menu()
    con.commit()
    #The changes are committed to the database
    print("Employee Deleted Successfully!")
    return_count('EMPLOYEE') #Returns number of records in EMPLOYEE database
    menu()

#5 Add Dependent to Company Database
def add_dependent():
    emp_ssn = input("Enter the SSN of the employee you want to add a dependent to: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM EMPLOYEE WHERE Ssn = ' + emp_ssn + ' FOR UPDATE'
    #Returns all fields for the desired employee. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query)
    #Executes locking query
    mr_curse.fetchone()
    #Runs result, but doesn't print it (allows next query to run properly)
    query2 = 'SELECT Dependent_name FROM DEPENDENT JOIN EMPLOYEE ON Essn=Ssn WHERE Ssn = ' + emp_ssn
    #Returns all dependents for the desired employee
    mr_curse.execute(query2)
    #Executes dependent query
    print("Dependents: ", unpack(mr_curse.fetchall(), True)) #Returns formatted dependent name(s)
    dName = input("Enter the dependent's first name: ")
    sex = input("Enter their sex (M/F): ")
    bDate = input("Enter their birthdate as YYYY-MM-DD: ")
    rel = input("Enter their relationship with the employee: ")
    mr_curse.execute('INSERT INTO DEPENDENT VALUES(%s, %s, %s, %s, %s)', (emp_ssn, dName, sex, bDate, rel))
    #This query takes the values entered by the user and inserts them into the correct columns to make a new DEPENDENT record
    con.commit()
    #Commits all changes to database and unlocks record
    print("Dependent Added Successfully!")
    menu()

#6 Remove Dependent from Company Database
def remove_dependent():
    emp_ssn = input("Enter the SSN of the employee you want to delete a dependent for: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM EMPLOYEE WHERE Ssn = ' + emp_ssn + ' FOR UPDATE'
    #Returns all fields for the desired employee. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query)
    #Executes locking query
    mr_curse.fetchone()
    #Runs result, but doesn't print it (allows next queries to run properly)
    query2 = 'SELECT Dependent_name FROM DEPENDENT JOIN EMPLOYEE ON Essn=Ssn WHERE Ssn = ' + emp_ssn
    #Returns all dependents for the desired employee
    mr_curse.execute(query2)
    #Executes dependent query
    print("Dependents: ", unpack(mr_curse.fetchall(), True)) #Returns formatted dependent name(s)
    name = input("Enter the name of the dependent you want to delete: ")
    query3 = 'DELETE FROM DEPENDENT WHERE Dependent_name = \'' + name + '\' AND Essn = ' + emp_ssn
    #Deletes desired dependent given desired employee's Ssn (Essn)
    mr_curse.execute(query3)
    #Executes deletion query
    con.commit()
    #Commits all changes to database and unlocks record
    print("Dependent Deleted Successfully!")
    menu()

#7 Add Department to Company Database
def add_department():
    dName = input("Enter the name of the department you want to add: ")
    dNum = input("Enter the department number: ")
    m_ssn = input("Enter the manager's ssn: ")
    m_date = input("Enter the manager's start date as YYYY-MM-DD: ")
    try:
        mr_curse.execute('INSERT INTO DEPARTMENT VALUES(%s, %s, %s, %s)', (dName, dNum, m_ssn, m_date))
        #This query takes the values entered by the user and inserts them into the correct columns to make a new DEPARTMENT record
    except mysql.connector.errors.IntegrityError: #Checks for any constraint violations with the primary/foreign keys
        print("\nError: Integrity Violation!!")
        con.rollback() #rolls back any changes/accesses to the database if INSERT INTO fails
        menu() #returns to menu
    except mysql.connector.errors.DataError: #Checks if incorrect data type was entered in a particular field
        print("\nError: Incorrect Type/Length of Data Entered!!")
        con.rollback() #rolls back any changes/accesses to the database if INSERT INTO fails
        menu()
    con.commit() #Assuming the record doesn't violate any constraints, the new record is committed to the database
    print("Department Added Successfully!")
    menu()

#8 View Department in Company Database
def view_department():
    dNum = input("Enter the number of the department you want to view: ")
    query = 'SELECT Dname FROM DEPARTMENT WHERE Dnumber = ' + dNum
    #Returns the name associated with the desired department
    query2 = 'SELECT Fname, Minit, Lname FROM EMPLOYEE JOIN DEPARTMENT ON Ssn = Mgr_ssn WHERE Dnumber = ' + dNum
    #Returns the full name of the manager for the desired department
    query3 = 'SELECT Dlocation FROM DEPT_LOCATIONS JOIN DEPARTMENT ON DEPT_LOCATIONS.Dnumber=DEPARTMENT.Dnumber WHERE DEPARTMENT.Dnumber = ' + dNum
    #Returns every location name associated with the desired department
    mr_curse.execute(query)
    print("Department Name: ", unpack(mr_curse.fetchone()))
    mr_curse.execute(query2)
    print("Manager's Name: ", unpack(mr_curse.fetchone()))
    mr_curse.execute(query3)
    print("Department's Locations: ", unpack(mr_curse.fetchall(), True))
    #Executes every query listed above and prints out their results
    menu()

#9 Delete Department from Company Database
def delete_department():
    dNum = input("Enter the number of the department you want to delete: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = ' + dNum + ' FOR UPDATE'
    #Returns all fields for the desired department. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query)
    #Executes locking query
    print("Department Information: ", mr_curse.fetchone()) #Prints out department details
    confirm = input("Are you sure you wish to delete this department? (Yes/No): ")
    if confirm == 'No':
        con.rollback() #rolls back locking if user cancels deletion
        menu()
    query2 = 'DELETE FROM DEPARTMENT WHERE Dnumber = ' + dNum
    #This query will delete the desired department
    try:
        mr_curse.execute(query2)
        #The query above is then executed
    except mysql.connector.errors.IntegrityError: #Checks for referential integrity constraint violations
        print("Error: Integrity Violation! -> This department has dependencies. Please remove these first before deleting")
        con.rollback() #rolls back any changes/locks to the database if DELETE FROM fails
        menu()
    con.commit()
    #The changes are committed to the database
    print("Department Deleted Successfully!")
    menu()

#10 Add Department Location to Company Database
def add_dep_location():
    dNum = input("Enter the number of the department you want to add a location to: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = ' + dNum + ' FOR UPDATE'
    #Returns all fields for the desired department. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query)
    #Executes locking query
    mr_curse.fetchone()
    #Runs result, but doesn't print it (allows next query to run properly)
    query2 = 'SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = ' + dNum
    #Returns all location names associated with desired department
    mr_curse.execute(query2)
    #Executes location query
    print("Department's Locations: ", unpack(mr_curse.fetchall(), True)) #Prints out department locations
    location = input("Enter the new location you wish to add: ")
    mr_curse.execute('INSERT INTO DEPT_LOCATIONS VALUES(%s, %s)', (dNum, location))
    #This query takes the values entered by the user and inserts them into the correct columns to make a new DEPT_LOCATIONS record
    con.commit() #Commits changes to database and unlocks department record
    print("Department Location Added Successfully!")
    menu()

#11 Remove Department Location from Company Database
def remove_dep_location():
    dNum = input("Enter the number of the department you want to remove a location from: ")
    mr_curse.execute('START TRANSACTION')
    #This starts a transaction, which will allow us to lock records as needed
    query = 'SELECT * FROM DEPARTMENT WHERE Dnumber = ' + dNum + ' FOR UPDATE'
    #Returns all fields for the desired department. The FOR UPDATE is added to this query to ensure the record being accessed/changed is locked
    mr_curse.execute(query)
    #Executes locking query
    mr_curse.fetchone()
    #Runs result, but doesn't print it (allows next query to run properly)
    query2 = 'SELECT Dlocation FROM DEPT_LOCATIONS WHERE Dnumber = ' + dNum
    #Returns all location names associated with desired department
    mr_curse.execute(query2)
    #Executes location query
    print("Department's Locations: ", unpack(mr_curse.fetchall(), True)) #Prints out department locations
    location = input("Enter the location you wish to delete: ")
    query3 = 'DELETE FROM DEPT_LOCATIONS WHERE Dlocation = \'' + location + '\' AND Dnumber = ' + dNum
    #Deletes desired department location given desired department's Dnumber
    mr_curse.execute(query3)
    #Executes deletion query
    con.commit()
    #Commits all changes to database and unlocks department record
    print("Department Location Deleted Successfully!")
    menu()

#Menu for Using Database Operations
def menu():
    print("\n1 to Add Employee\t2 to View Employee\t3 to Modify Employee\t4 to Delete Employee")
    print("5 to Add Dependent\t6 to Remove Dependent\t7 to Add Department\t8 to View Department")
    print("9 to Remove Dept\t10 to Add Dept Loc\t11 to Remove Dept Loc\t0 to Exit")
    choice = int(input("Enter your choice of operation (0-11): "))
    match choice: #This takes user's input for operation and calls the corresponding method
        case 0: exit(0)
        case 1: add_employee()
        case 2: view_employee()
        case 3: modify_employee()
        case 4: delete_employee()
        case 5: add_dependent()
        case 6: remove_dependent()
        case 7: add_department()
        case 8: view_department()
        case 9: delete_department()
        case 10: add_dep_location()
        case 11: remove_dep_location()
        case _: exit(0)

if __name__ == '__main__':
    print("Welcome to Project 2: Company Database Operations!")
    menu()