import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    # Make sure this filename matches exactly what you renamed your JSON file
    cred = credentials.Certificate(r"C:\Users\phgam\Desktop\Reward App\key.json") 
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. APP CONFIG ---
st.set_page_config(page_title="Henry's Quality Shoe Repair", page_icon="👞")
# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Change the background color to a soft cream */
    .stApp {
        background-color: #Fdf5e6;
    }
    /* Change the headers to a deep leather brown */
    h1, h2, h3 {
        color: #5D4037 !important;
        font-family: 'Georgia', serif;
    }
    /* Style the sidebar */
    [data-testid="stSidebar"] {
        background-color: #3E2723;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Make buttons look more professional */
    .stButton>button {
        background-color: #8D6E63;
        color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
st.title("👞 Henry's Quality Shoe Repair")
st.markdown("---")

# --- 3. UI NAVIGATION ---
st.sidebar.title("Staff Menu")
choice = st.sidebar.radio("Action", ["New Customer", "Log a Repair", "View All Records"])

# --- 4. LOGIC SECTIONS ---

if choice == "New Customer":
    st.header("Register New Client")
    with st.form("reg_form"):
        name = st.text_input("Customer Full Name")
        phone = st.text_input("Phone Number")
        if st.form_submit_button("Create Account"):
            if phone and name:
                # This saves directly to the Firebase 'customers' collection
                doc_ref = db.collection("customers").document(phone)
                doc_ref.set({
                    "name": name,
                    "points": 0,
                    "repairs": []
                })
                st.success(f"Successfully registered {name}!")
            else:
                st.error("Please provide both Name and Phone.")

elif choice == "Log a Repair":
    st.header("Log a Service")
    phone_lookup = st.text_input("Enter Customer Phone")
    
    if phone_lookup:
        doc_ref = db.collection("customers").document(phone_lookup)
        doc = doc_ref.get()
        
        if doc.exists:
            cust = doc.to_dict()
            st.info(f"Customer: **{cust['name']}** | Points: {cust['points']}")
            
            # --- 1. REWARD CHECK (The 250 Point Goal) ---
            st.markdown("### 🎁 Rewards Status")
            if cust['points'] >= 250:
                st.balloons()
                st.success("🎉 This customer has earned a $10 discount!")
                if st.button("Redeem 250 Points"):
                    doc_ref.update({"points": cust['points'] - 250})
                    st.toast("250 Points Redeemed!", icon="👞")
                    st.rerun() 
            else:
                points_needed = 250 - cust['points']
                st.write(f"Status: **{points_needed}** more points until a reward.")
            
            st.markdown("---")

            # --- 2. SERVICE SELECTION ---
            services = {
                "Standard Shine ($20 up)": 20,
                "Boot Shine ($25)": 25,
                "Red Bottom Heel Tip Repair ($25)":25,
                "Heel Tip Repair ($18 - $28)": 18,
                "Men Heel Dress Shoe ($45)":45,
                "Men Boot Heel ($55)":55,
                "Reglue ($30)":30,
                "Reglue Tennis Shoe ($50)":50,
                "Heel Wrap ($55)":55,
                "Leather Full sole ($95)": 95,
                "Leather Half Sole($75)":75,
                "Rubber Full Sole($85)":85,
                "Rubber Half Sole($75)":75,
                "Stretch ($20)": 20,
                "Stretch Boot ($25)": 25,
                "Red Bottom Power Sole($50)":50,
                "Power Sole($30)":30,
                "Men Red Bottom Power Sole($50)":50,
                "Men Power sole($35)":35,
                "Custom Amount": 0
            }
            
            selected_service = st.selectbox("Select Service", list(services.keys()))
            amount = st.number_input(
           "Confirm Final Price ($)", 
            min_value=0, 
            value=services[selected_service], # This automatically fills in 18, 20, or 100
            step=1
)
            amount = st.number_input("Enter Amount ($)", min_value=1) if selected_service == "Custom Amount" else services[selected_service]
            
            # --- 3. THE MATH (0.5 points per dollar) ---
            points_to_add = amount * 0.5
            st.write(f"This service will add: **{points_to_add}** points.")

            if st.button("Apply Points & Complete"):
                new_points = cust['points'] + points_to_add
                doc_ref.update({
                    "points": new_points,
                    "repairs": firestore.ArrayUnion([selected_service])
                })
                st.success(f"Success! Added {points_to_add} points.")
                st.rerun()
        else:
            st.warning("Customer not found.")

elif choice == "View All Records":
    st.header("Business Ledger")
    # Pull all data from Firebase
    docs = db.collection("customers").stream()
    
    data_list = []
    for doc in docs:
        d = doc.to_dict()
        data_list.append({
            "Phone": doc.id,
            "Name": d['name'],
            "Points": d['points'],
            "Repairs Done": len(d.get('repairs', []))
        })
    
    if data_list:
        st.table(data_list)
    else:
        st.write("No customers in the database yet.")