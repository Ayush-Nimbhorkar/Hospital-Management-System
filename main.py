import re
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3

def show_frame(frame):
    frame.tkraise()

# Initializing database and creating tables if they don't exist
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Database~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def initialize_db():
    try:
        with sqlite3.connect("Hospital.db") as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id VARCHAR(8),
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    address TEXT,
                    phone TEXT,
                    blood_group TEXT,
                    room_type TEXT,
                    disease VARCHAR (20),
                    doctor_visits INTEGER DEFAULT 0,
                    check_in_date TEXT,
                    dob TEXT
                )
            """)
    
            # Create Room Types table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_types (
                    room_type TEXT PRIMARY KEY,
                    total_beds INTEGER,
                    occupied_beds INTEGER
                )
            """)
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
            
    conn.commit()
    conn.close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CLEARING ENTRIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def clear_entries():
    for entry in [patient_id_entry, name_entry, age_entry, address_entry, phone_entry, disease_entry, date_entry, dob_entry, no_of_doctor_visits_entry]:
        entry.delete(0, tk.END)
    blood_group_combo.set('')
    room_type_combo.set('')
    search_name_entry.delete(0, tk.END)
    billing_patient_name_entry.delete(0, tk.END)
    gender_var.set("none")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CHECK IN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_in_patient():
    pid = patient_id_entry.get()
    name = name_entry.get()
    age = age_entry.get()
    gender = gender_var.get()
    address = address_entry.get()
    phone = phone_entry.get()
    blood_group = blood_group_combo.get()
    room_type = room_type_combo.get()
    disease = disease_entry.get()
    no_of_doctor_visits = no_of_doctor_visits_entry.get()
    check_date = date_entry.get()
    dob = dob_entry.get()
    
    # Validate PID (assuming alphanumeric):
    if not re.match(r'^[a-zA-Z0-9]+$', pid):
        messagebox.showerror("Error", "Invalid PID format.")
        return
    # Validate Name:
    if not re.match(r'^[a-zA-Z\s]+$', name):
        messagebox.showerror("Error", "Invalid name format.")
        return
    # Validate Age:
    if not age.isdigit() or int(age) <= 0:
        messagebox.showerror("Error", "Age should be a positive number.")
        return
    # Validate Gender:
    if gender not in ['Male', 'Female', 'Other']:
        messagebox.showerror("Error", "Invalid gender selection.")
        return
    # Validate Address:
    if not address.strip():
        messagebox.showerror("Error", "Address is required.")
        return
    # Validate Phone Number:
    if not re.match(r'^[0-9]{10}$', phone):
        messagebox.showerror("Error", "Invalid phone number format. Must be 10 digits.")
        return
    # Validate Blood Group (assuming standard formats):
    if not re.match(r'^(A|B|AB|O)[+-]$', blood_group):
        messagebox.showerror("Error", "Invalid blood group format.")
        return
    # Validate Room Type (assuming predefined options):
    valid_room_types = ['Single', 'Twin Sharing', 'Dormitory', 'ICU']
    if room_type not in valid_room_types:
        messagebox.showerror("Error", "Invalid room type selection.")
        return
    # Validate Number of Doctor Visits:
    if not no_of_doctor_visits.isdigit() or int(no_of_doctor_visits) < 0:
        messagebox.showerror("Error", "Number of doctor visits should be a non-negative number.")
        return
    # Validate Disease:
    if not disease.strip():
        messagebox.showerror("Error", "Disease information is required.")
        return
    # Validate Check-in Date (assuming DD-MM-YYYY format):
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', check_date):
        messagebox.showerror("Error", "Invalid check-in date format. Use YYYY-MM-DD.")
        return
    # Validate Date of Birth (assuming DD-MM-YYYY format):
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', dob):
        messagebox.showerror("Error", "Invalid date of birth format. Use YYYY-MM-DD.")
        return
    try:
        conn = sqlite3.connect("Hospital.db")
        cursor = conn.cursor()
        
        # Insert patient details into the database
        cursor.execute("""
            INSERT INTO patients (id,name, age, gender, address, phone, blood_group, room_type, disease, doctor_visits, check_in_date, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid,name, age, gender, address, phone, blood_group, room_type, disease, no_of_doctor_visits, check_date, dob))
        
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Patient {name} checked in successfully.")
        clear_entries()
        update_bed_status_and_database(room_type, +1)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SEARCH PATIENT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def search_patient():
    search_name = search_name_entry.get()
    global result_label 

    try:
        conn = sqlite3.connect("Hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + search_name + '%',))
        results = cursor.fetchall()
        conn.close()

        for widget in search_results_frame.winfo_children():
            widget.destroy()

        if results :
            
            for index, result in enumerate(results):
                patient_id, name, age, gender, address, phone_no, blood_group, room_type,disease,doctor_visits,check_in_date, dob = result
                patient_info = (f"Patient ID3: {patient_id}\n"
                                f"Patient Name: {name}\n"
                                f"Age: {age}\n"
                                f"Gender: {gender}\n"
                                f"Address: {address}\n"
                                f"Phone No: {phone_no}\n"
                                f"Blood Group: {blood_group}\n"
                                f"Room Type: {room_type}\n"
                                f"Disease: {disease}\n"
                                f"Doctor Visits: {doctor_visits}\n"
                                f"Check-in Date: {check_in_date}\n"
                                f"Date of Birth: {dob}\n"
                                )
                result_label = tk.Label(search_results_frame, text=patient_info, anchor='w',justify='left', bg='lightblue')
                result_label.pack(fill='both', expand=True, padx=10, pady=5)
        
        else:
            messagebox.showerror("Error", "Patient not found.")
        
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")

    clear_entries()
# Global declaration of variable
current_bill_message = ""
msg = "----------------------------------------"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BILL CALCULATION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calculate_bill():
    global current_bill_message
    global bill_frame 

    search_name = billing_patient_name_entry.get()  
    try:
        conn = sqlite3.connect("Hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + search_name + '%',))
        patient = cursor.fetchone()
        conn.close()

        if patient:
            room_type1 = patient[7]
            doctor_visits = patient[9]

            room_rent = {'Single': 1000, 'Twin Sharing': 750, 'Dormitory': 500, 'ICU': 2000}
            rent = room_rent.get(room_type1, 0)
            doctor_charge = {'Single': 400, 'Twin Sharing': 300, 'Dormitory': 200, 'ICU': 450}
            charge = doctor_charge.get(room_type1, 0)
            doctor_charges = doctor_visits * charge
            total_bill = rent + doctor_charges

            bill_message = (
                f"\tPatient ID:  {patient[0]}\n"
                f"\tName:  {patient[1]}\n"
                f"\tAge:  {patient[2]}\n"
                f"\tGender:  {patient[3]}\n"
                f"\tAddress:  {patient[4]}\n"
                f"\tPhone:  {patient[5]}\n"
                f"\tBlood Group:  {patient[6]}\n"
                f"\tRoom Type:  {room_type}\n"
                f"\tDisease:  {patient[8]}\n"
                f"\tDoctor Visits:  {doctor_visits}\n"
                f"\tDate of Admission:  {patient[10]}\n"
                f"\tDate of Birth:  {patient[11]}\n"
                f"\tRoom Rent:  {rent}\n"
                f"\tDoctor Charges:  {doctor_charges}\n\n"   
            )
            
            bill_frame = tk.Frame(billing_frame,bd=5, relief=tk.RIDGE, bg="#aad7f3")
            bill_frame.place(x=320,y=110,width=460, height=400)
            
            msg = (f"\tTotal Bill:  {total_bill}\n")
            
            tk.Label(bill_frame, text=bill_message,font="arial 15",bg="#aad7f3", justify='left', anchor='w').place(x=0,y=0)
            tk.Label(bill_frame, text=msg,font="arial 15", justify='center',bg="#aad7f3", anchor='w').place(x=50,y=335)

            current_bill_message = "-----------------BILL------------------\n" + bill_message+"\n"+ msg
        else:
            messagebox.showerror("Error", "Patient not found.")
    
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")
    
    clear_entries()   

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PRINTING BILL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def print_bill():
    global current_bill_message
    global msg  
    try:
        # Open a file dialog to select the location to save the bill
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", ".txt"), ("All files", ".*")])

        if file_path:
            with open(file_path, 'w') as file:
                file.write(current_bill_message) 
                file.write("\n")  
                file.write(msg)  

            messagebox.showinfo("Success", f"Bill saved successfully at {file_path}")
        else:
            messagebox.showwarning("Warning", "Save operation cancelled")

    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while saving the bill: {str(e)}")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FETCHING DATA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fetch_data():
    try:
        conn = sqlite3.connect("Hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        rows = cursor.fetchall()
        if len(rows) != 0:
            table.delete(*table.get_children())
            for items in rows:
                table.insert('', END, values=items)
            conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error occurred: {str(e)}")

initialize_db()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GUI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the main window
top = tk.Tk()
top.title("Hospital Management System")

# Set the window icon
path = r"C:\Users\HP\OneDrive\Desktop\Python\logo.ico"
top.iconbitmap(path)

# Set the window size and state
top.geometry("1000x600")
top.state('zoomed')
top.minsize(width=1400,height=650)
top.config(bg="#dcf2f1")

# Configure column to expand
top.grid_columnconfigure(0, weight=1)

# Load and set the image for the title label
image_path = r"C:\Users\HP\OneDrive\Desktop\Python\icon.png"
image = tk.PhotoImage(file=image_path)
title = tk.Label(top,text="Hospital Management System", font="arial 20 bold", bg="#0047b3", fg="white", image=image, compound=tk.LEFT, padx=10)
title.grid(row=0, column=0, sticky='ew')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BUTTON FRAME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a frame for buttons
btn_frame = tk.Frame(top,bd=5, relief=tk.RIDGE, bg="#7fc7d9")
btn_frame.place(x=0, y=54, width=250, height=740)

# Create navigation buttons
#Home Button
tk.Button(btn_frame,bd=4, text="HOME", font="arial 15", bg="#365486", fg="white", cursor="hand2", command=lambda: [show_frame(home_frame),result_label.destroy(),bill_frame.destroy(),clear_entries()
]).place(x=30, y=65, width=190, height=70)

#Bed Status Button
tk.Button(btn_frame,bd=4,  text="Bed Status", font="arial 15", bg="#365486", fg="white", cursor="hand2", command=lambda: [show_frame(bed_status_frame),update_bed_status_and_database(room_type,+0),result_label.destroy(),bill_frame.destroy(),clear_entries()]).place(x=30, y=205, width=190, height=70)

#Patient Data Button
tk.Button(btn_frame,bd=4,  text="Patient Data", font="arial 15", bg="#365486", fg="white", cursor="hand2", command=lambda: [show_frame(patient_data_frame),result_label.destroy(),bill_frame.destroy(),clear_entries()]).place(x=30, y=345, width=190, height=70)

#Billing Button
tk.Button(btn_frame, bd=4, text="Billing", font="arial 15", bg="#365486", fg="white", cursor="hand2", command=lambda: [show_frame(billing_frame),result_label.destroy(),bill_frame.destroy(),clear_entries()]).place(x=30, y=485, width=190, height=70)


# Create frames for each section
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~HOME FRAME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

home_frame = tk.Frame(top, relief=tk.RIDGE,bd=5, bg="#aad7f3")
home_frame.place(x=300, y=80, width=1200, height=680)

# Title Label
tk.Label(home_frame, text="Patient Admission Details", font="arial 15 bold", bg="#0047b3", fg="white").place(x=440, y=0, width=280, height=30)

# First column
tk.Label(home_frame, text="Patient ID:", bg="#aad7f3", font="10").place(x=80, y=70)
patient_id_entry = ttk.Entry(home_frame, width=30,font="arial 12")
patient_id_entry.place(x=250, y=75, width=250,height=25)

tk.Label(home_frame, text="Patient Name:", bg="#aad7f3", font="10").place(x=80, y=120)
name_entry = ttk.Entry(home_frame, width=30,font="arial 12")
name_entry.place(x=250, y=125, width=250,height=25)

tk.Label(home_frame, text="Age:", bg="#aad7f3", font="10").place(x=80, y=170)
age_entry = ttk.Entry(home_frame, width=10,font="arial 12")
age_entry.place(x=250, y=175, width=250,height=25)

radio = tk.Label(home_frame, text="Gender:", bg="#aad7f3", font="10").place(x=80, y=220)
gender_var = tk.StringVar(value="none")
tk.Radiobutton(home_frame, text="Male",bg="#aad7f3",variable=gender_var, value="Male").place(x=250, y=220)
tk.Radiobutton(home_frame, text="Female",bg="#aad7f3",variable=gender_var, value="Female").place(x=320, y=220)
tk.Radiobutton(home_frame, text="Others",bg="#aad7f3", variable=gender_var, value="Other").place(x=400, y=220)

tk.Label(home_frame, text="Address:", bg="#aad7f3", font="10").place(x=80, y=270)
address_entry = ttk.Entry(home_frame, width=30,font="arial 12")
address_entry.place(x=250, y=275, width=250,height=25)

tk.Label(home_frame, text="Phone No:", bg="#aad7f3", font="10").place(x=80, y=320)
phone_entry = ttk.Entry(home_frame, width=30,font="arial 12")
phone_entry.place(x=250, y=325, width=250,height=25)

# Second column
tk.Label(home_frame, text="Blood Group:", bg="#aad7f3", font="10").place(x=600, y=70)
blood_group_combo = ttk.Combobox(home_frame, values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], width=20,font="arial 12")
blood_group_combo.place(x=800, y=75, width=250,height=25)

tk.Label(home_frame, text="Room Type:", bg="#aad7f3", font="10").place(x=600, y=120)
room_type_combo = ttk.Combobox(home_frame, values=['Single', 'Twin Sharing', 'Dormitory', 'ICU'], width=20,font="arial 12")
room_type_combo.place(x=800, y=125, width=250,height=25)

tk.Label(home_frame, text="Disease:", bg="#aad7f3", font="10").place(x=600, y=170)
disease_entry = ttk.Entry(home_frame, width=30,font="arial 12")
disease_entry.place(x=800, y=175, width=250,height=25)

tk.Label(home_frame, text="No. of Doctor Visits:", bg="#aad7f3", font="10").place(x=600, y=220)
no_of_doctor_visits_entry = ttk.Entry(home_frame, width=10,font="arial 12")
no_of_doctor_visits_entry.place(x=800, y=225, width=250,height=25)

tk.Label(home_frame, text="Date:", bg="#aad7f3", font="10").place(x=600, y=270)
date_entry = ttk.Entry(home_frame, width=10,font="arial 12")
date_entry.place(x=800, y=275, width=250,height=25)

tk.Label(home_frame, text="Date of Birth:", bg="#aad7f3", font="10").place(x=600, y=320)
dob_entry = ttk.Entry(home_frame, width=10,font="arial 12")
dob_entry.place(x=800, y=325, width=250,height=25)

ttk.Style().configure("TButton", padding=6, relief="flat",background="blue")
s = ttk.Style()
s.configure('my.TButton', font=('arial', 12))

# Admit Button
ttk.Button(home_frame,style='my.TButton', text="Admit", command=lambda: [check_in_patient(), fetch_data()]).place(x=500, y=415, width=100, height=40)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BED STATUS FRAME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

conn = sqlite3.connect('Hospital.db')
cursor = conn.cursor()

# Initialize data in the table if it doesn't exist
initial_data = [
    ('Single', 24, 0),
    ('Twin Sharing', 28, 0),
    ('Dormitory', 32, 0),
    ('ICU', 20, 0)
]

cursor.executemany("INSERT OR IGNORE INTO room_types VALUES (?, ?, ?)", initial_data)


bed_status_frame = tk.Frame(top,bd=5, relief=tk.RIDGE, bg="#aad7f3")
bed_status_frame.place(x=300, y=80, width=1200, height=680)

# Fetch initial data from database
cursor.execute("SELECT * FROM room_types")
initial_data = cursor.fetchall()

bed_availability = {row[0]: {'total': row[1], 'occupied': row[2]} for row in initial_data}

# Commit changes and close connection
conn.commit()
conn.close()

#Update coloring of the bed
def update_bed_status():
    conn = sqlite3.connect('Hospital.db')
    cursor = conn.cursor()

    for room_type, data in bed_availability.items():
        cursor.execute("SELECT occupied_beds FROM room_types WHERE room_type=?", (room_type,))
        occupied_beds = cursor.fetchone()[0]

        for i in range(data['total']):
            color = '#ff9b9b' if i < occupied_beds else 'lightgreen'
            bed_labels[room_type][i].config(bg=color)

    conn.close()

def update_bed_status_and_database(room_type, delta_occupied):
    conn = sqlite3.connect('Hospital.db')
    cursor = conn.cursor()

    cursor.execute("SELECT total_beds, occupied_beds FROM room_types WHERE room_type=?", (room_type,))
    total_beds, occupied_beds = cursor.fetchone()

    new_occupied_beds = occupied_beds + delta_occupied
    new_available_beds = total_beds - new_occupied_beds

    # Update database
    cursor.execute("UPDATE room_types SET occupied_beds=? WHERE room_type=?", (new_occupied_beds, room_type))

    conn.commit()
    conn.close()

    # Update GUI
    bed_availability[room_type]['occupied'] = new_occupied_beds
    update_bed_status()
    
#Labels
tk.Label(bed_status_frame, text="Bed Occupancy Status", font="arial 15 bold", bg="#0047b3", fg="white").place(x=440, y=0, width=280, height=30)

room_types = ['Single', 'Twin Sharing', 'Dormitory', 'ICU']
colors = ['lightgreen', 'lightgrey']  # Lightgreen for available bed, pink for ocuppied bed
image_path1 = r"C:\Users\HP\OneDrive\Desktop\Python\bed.png" 
image1 = Image.open(image_path1)
image1 = image1.resize((50, 50))
photo = ImageTk.PhotoImage(image1)

image_references = [photo]

bed_labels = {}

#Creating beds
for i, room_type in enumerate(room_types):
    room_frame = tk.Frame(bed_status_frame, relief=tk.RIDGE, bg="#81c9f9")
    room_frame.place(x=50 + i * 280, y=50, width=257, height=560)
    room_label = tk.Label(room_frame, text=room_type, font="arial 15 bold", bg="#81c9f9")
    room_label.grid(row=0, column=0, columnspan=4)
    
    bed_labels[room_type] = []
    
    total_beds = bed_availability[room_type]['total']
    num_rows = (total_beds // 4) + (1 if total_beds % 4 else 0) 

    for row in range(1, num_rows + 1):  
        for col in range(4):
            if len(bed_labels[room_type]) < total_beds:
                bed_label = tk.Label(room_frame, bg='lightgreen', image=photo)
                bed_label.grid(row=row, column=col, padx=5, pady=5)
                bed_labels[room_type].append(bed_label)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PATIENT DATA FRAME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

patient_data_frame = tk.Frame(top,bd=5, relief=tk.RIDGE, bg="#aad7f3")
patient_data_frame.place(x=300, y=80, width=1200, height=680)

# Place widgets in the patient_data_frame
tk.Label(patient_data_frame, text="Search Patients", font="arial 15 bold", bg="#0047b3", fg="white").place(x=440, y=0, width=280, height=30)

tk.Label(patient_data_frame, text="Patient Name:", bg="#aad7f3", font="10").place(x=350, y=50)
search_name_entry = ttk.Entry(patient_data_frame, width=30, font="arial 12")
search_name_entry.place(x=500, y=54, width=250)

ttk.Button(patient_data_frame, text="Search", command=search_patient).place(x=480, y=95, width=100,height=35)

search_results_frame = tk.Frame(patient_data_frame,bd=15, bg="#aad7f3")
search_results_frame.place(x=260, y=135, width=600, height=200)

result_label = tk.Label(search_results_frame, text="", anchor='w',justify='left', bg='lightblue')


#~~~~~~~~~~~~~~~~~~~~~~~PATIENT TABLE FRAME~~~~~~~~~~~~~~~~~~~~~~~~~
pt_table_frame = Frame(patient_data_frame, bd= 2, relief=RIDGE)
pt_table_frame.place(x=5, y= 360, width =1180, height=300)

#~~~~~~~~~~~~~~SCROLL BAR~~~~~~~~~~~~
# scrollX = ttk.Scrollbar(pt_table_frame, orient=HORIZONTAL)
# scrollX.pack(side='bottom', fill='x')

scrollY = ttk.Scrollbar(pt_table_frame, orient=VERTICAL)
scrollY.pack(side='right', fill='y')

#~~~~~~~~~~~~TABLE CREATION~~~~~~~~~~~

table = ttk.Treeview(pt_table_frame, columns=("pid","na", "age", "gen","ad","phno","bdg","rmt","dis","dv","cdate","dob",),xscrollcommand=scrollY.set, yscrollcommand=scrollY.set)
scrollX = ttk.Scrollbar(command=table.xview)
scrollY = ttk.Scrollbar(command=table.yview)

#heading for frame
table.heading("pid", text="Patient ID")
table.heading("na", text="Name")
table.heading("age", text="Age")
table.heading("gen", text="Gender")
table.heading("ad", text="Address")
table.heading("phno", text="Phone No.")
table.heading("bdg", text="Blood Group")
table.heading("rmt", text="Room type")
table.heading("dis", text="Disease")
table.heading("dv", text="No. of doctor visits")
table.heading("cdate", text="Check in date")
table.heading("dob", text="Date of Birth")
table['show'] = 'headings'
table.pack(fill= BOTH, expand=1)

table.column("pid", width=50)
table.column("na", width=100)
table.column("age", width=40)
table.column("gen", width=50)
table.column("ad", width=100)
table.column("phno", width=100)
table.column("bdg", width=70)
table.column("rmt", width=100)
table.column("dis", width=100)
table.column("dv", width=100)
table.column("cdate", width=100)
table.column("dob", width=100)
fetch_data()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BILLING FRAME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

billing_frame = tk.Frame(top,bd=5, relief=tk.RIDGE, bg="#aad7f3")
billing_frame.place(x=300, y=80, width=1200, height=680)

bill_frame = tk.Frame(billing_frame,bd=5, relief=tk.RIDGE, bg="#aad7f3")


tk.Label(billing_frame, text="Billing Details", font="arial 15 bold", bg="#0047b3", fg="white").place(x=440, y=0, width=280, height=30)

# Patient Search
tk.Label(billing_frame, text="Search by patient name:", bg="#aad7f3", font="10").place(x=320, y=50)
billing_patient_name_entry = ttk.Entry(billing_frame, width=30, font="arial 12")
billing_patient_name_entry.place(x=560, y=55)

#Generate bill button
ttk.Button(billing_frame, text="Generate Bill", command=calculate_bill, width=15, style="TButton").place(x=500, y=520)

#Save button
ttk.Button(billing_frame, text="Save Bill ", command=print_bill, width=15, style="TButton").place(x=500, y=570)


show_frame(home_frame)

top.mainloop()
