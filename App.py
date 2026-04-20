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
            
            # --- NEW: REDEEM REWARDS SECTION ---
            st.markdown("### 🎁 Available Rewards")
            if cust['points'] >= 100:
                st.balloons()
                st.success("This customer is eligible for a reward!")
                if st.button("Redeem 100 Points ($10 Discount)"):
                    new_val = cust['points'] - 100
                    doc_ref.update({"points": new_val})
                    st.toast("Points Deducted!", icon="✅")
                    st.rerun() # Refresh to show the new lower balance
            else:
                points_needed = 100 - cust['points']
                st.write(f"Keep going! Only **{points_needed}** more points until a free reward.")
            # Preset Prices for Henry's Services
            services = {
                "Standard Shine ($15)": 15,
                "Heel Repair ($40)": 40,
                "Full Resole ($100)": 100,
                "Stretching ($20)": 20,
                "Custom Amount": 0
            }
            
            selected_service = st.selectbox("Select Service", list(services.keys()))
            
            if selected_service == "Custom Amount":
                amount = st.number_input("Enter Amount ($)", min_value=1)
            else:
                amount = services[selected_service]
                st.write(f"Points to add: **{amount}**")
            
            if st.button("Apply Points & Complete"):
                new_points = cust['points'] + amount
                doc_ref.update({
                    "points": new_points,
                    "repairs": firestore.ArrayUnion([selected_service])
                })
                st.balloons()
                st.success(f"Success! {cust['name']} now has {new_points} points.")
                # Add a Reward Section
            if cust['points'] >= 100:
                st.warning("🎉 Reward Available: 100 Points for $10 off!")
                if st.button("Redeem 100 Points"):
                    doc_ref.update({"points": cust['points'] - 100})
                    st.success("Reward Redeemed! $10 applied to total.")
                    st.rerun() # Refresh the page to show new balance
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