import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore # Ensure this import is at the top

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        key_dict = dict(st.secrets["firebase_config"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Setup Error: {e}")

# FORCE THE DATABASE TO USE REST INSTEAD OF GRPC
db = firestore.Client(project="henrysshoerepair-4a96e", database="(default)")
# --- 2. STYLE (Same "Leather & Cream" vibe) ---
st.set_page_config(page_title="Henry's Rewards", page_icon="👞")
st.markdown("""
    <style>
    .stApp { background-color: #Fdf5e6; }
    h1, h2, h3 { color: #5D4037 !important; font-family: 'Georgia', serif; }
    .stButton>button { background-color: #8D6E63; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CUSTOMER INTERFACE ---
st.title("👞 Henry's Quality Shoe Repair")
st.subheader("Loyalty Rewards Portal")

phone = st.text_input("Enter your Phone Number to see your rewards:")

if phone:
    doc_ref = db.collection("customers").document(phone)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        st.markdown(f"## Welcome back, {data['name']}!")
        
        # Big Point Display
        st.metric(label="Your Current Points", value=data['points'])
        
        # Progress Bar to next reward
        progress = min(data['points'] / 250, 1.0)
        st.progress(progress)
        
        if data['points'] >= 250:
            st.balloons()
            st.success("🎉 You have a reward waiting! Show this screen to Henry.")
        else:
            st.info(f"You're just {250 - data['points']} points away from a $10 discount.")
            
        # Optional: Show repair history
        with st.expander("View your repair history"):
            for repair in data.get('repairs', []):
                st.write(f"✅ {repair}")
    else:
        st.error("Phone number not found. Please register at the shop next time you visit!")
