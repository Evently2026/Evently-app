import streamlit as st
import os
import json
from PIL import Image
from datetime import datetime

# --- CONFIGURATION ---
STORAGE_DIR = 'event_photos'
DATA_FILE = 'metadata.json'
ADMIN_PASSWORD = 'business2026'

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_metadata():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_metadata(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

st.set_page_config(page_title='EventShare Pro+', layout='wide', page_icon='📸')

# Custom CSS
st.markdown('''
    <style>
    .stImage { border-radius: 15px; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    ''', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("📸 EventShare Pro+")
user_name = st.sidebar.text_input("Your Name:", placeholder="Who are you?")
admin_key = st.sidebar.text_input("Admin Panel:", type="password")
is_admin = (admin_key == ADMIN_PASSWORD)

if user_name:
    st.sidebar.divider()
    files = st.sidebar.file_uploader("Upload Moments", type=["jpg","png","jpeg"], accept_multiple_files=True)
    if st.sidebar.button("🚀 Post to Gallery"):
        if files:
            for f in files:
                ts = datetime.now().strftime("%H%M%S_%f")
                fname = f"{ts}_{user_name}_{f.name}"
                with open(os.path.join(STORAGE_DIR, fname), 'wb') as out:
                    out.write(f.getbuffer())
            st.rerun()

# --- MAIN ---
st.title("Event Gallery")
metadata = load_metadata()
all_photos = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
all_photos.sort(reverse=True)

if not all_photos:
    st.info("The gallery is waiting for its first photo!")
else:
    cols = st.columns(2)
    for idx, fname in enumerate(all_photos):
        col = cols[idx % 2]
        with col:
            photo_path = os.path.join(STORAGE_DIR, fname)
            sender = fname.split("_")[1] if "_" in fname else "Guest"
            
            st.image(Image.open(photo_path), use_container_width=True)
            
            photo_data = metadata.get(fname, {"likes": 0, "comments": []})
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button(f"❤️ {photo_data['likes']}", key=f"l_{idx}"):
                    photo_data['likes'] += 1
                    metadata[fname] = photo_data
                    save_metadata(metadata)
                    st.rerun()
            with c2:
                st.write(f"**By {sender}**")

            with st.expander(f"Comments ({len(photo_data['comments'])})"):
                msg = st.text_input("Add a comment", key=f"ti_{idx}")
                if st.button("Send", key=f"tb_{idx}"):
                    if user_name and msg:
                        photo_data['comments'].append(f"{user_name}: {msg}")
                        metadata[fname] = photo_data
                        save_metadata(metadata)
                        st.rerun()
                for c in photo_data['comments']:
                    st.write(f"💬 {c}")
            
            if is_admin:
                if st.button("🗑️ Admin Delete", key=f"del_{idx}"):
                    os.remove(photo_path)
                    if fname in metadata: del metadata[fname]
                    save_metadata(metadata)
                    st.rerun()
            st.divider()
