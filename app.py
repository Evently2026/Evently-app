import streamlit as st
import os
import json
from PIL import Image
from datetime import datetime

# --- CONFIGURATION & DATABASE ---
STORAGE_DIR = 'event_photos'
DATA_FILE = 'metadata.json'
ADMIN_PASSWORD = 'Evently.2026@'

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def load_metadata():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# --- UI ENHANCEMENTS (CSS) ---
st.set_page_config(page_title='EventShare Pro+', layout='wide', page_icon='✨')

# Advanced Styling for a "Pro" look
st.markdown('''
    <style>
    .main { background-color: #f0f2f6; }
    .stImage { 
        border-radius: 20px; 
        transition: transform .2s; 
    }
    .stImage:hover { transform: scale(1.02); }
    .stButton>button { 
        border-radius: 50px; 
        background-color: #2E86C1; 
        color: white;
    }
    div[data-testid="stExpander"] {
        border: none;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
    }
    </style>
    ''', unsafe_allow_html=True)

# --- SIDEBAR & IDENTITY ---
st.sidebar.title("✨ EventShare Elite")
user_name = st.sidebar.text_input("Attendee Name:", placeholder="How should we call you?")
admin_key = st.sidebar.text_input("Staff Access:", type="password")
is_admin = (admin_key == ADMIN_PASSWORD)

# --- UPLOAD WITH FEEDBACK ---
if user_name:
    st.sidebar.success(f"Ready to share, {user_name}!")
    files = st.sidebar.file_uploader("Capture a Highlight", type=["jpg","png","jpeg"], accept_multiple_files=True)
    if st.sidebar.button("🚀 Publish to Live Feed"):
        if files:
            for f in files:
                ts = datetime.now().strftime("%H%M%S_%f")
                fname = f"{ts}_{user_name}_{f.name}"
                with open(os.path.join(STORAGE_DIR, fname), 'wb') as out:
                    out.write(f.getbuffer())
            st.toast(f"Successfully shared {len(files)} photos!", icon='✅') # New Feature: Feedback
            st.rerun()

# --- MAIN INTERFACE ---
st.title("Live Event Gallery")
metadata = load_metadata()
all_photos = [f for f in os.listdir(STORAGE_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

if not all_photos:
    st.info("The gallery is currently empty. Be the first to post!")
else:
    # FEATURE: Sort by Popularity or Recency
    sort_option = st.selectbox("Sort By:", ["Newest First", "Most Popular"])
    
    if sort_option == "Most Popular":
        all_photos.sort(key=lambda x: metadata.get(x, {}).get('likes', 0), reverse=True)
    else:
        all_photos.sort(reverse=True)

    cols = st.columns(2)
    for idx, fname in enumerate(all_photos):
        col = cols[idx % 2]
        with col:
            photo_path = os.path.join(STORAGE_DIR, fname)
            sender = fname.split("_")[1] if "_" in fname else "Guest"
            photo_data = metadata.get(fname, {"likes": 0, "comments": []})
            
            # Card Container
            st.image(Image.open(photo_path), use_container_width=True)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button(f"❤️ {photo_data['likes']}", key=f"lk_{idx}"):
                    photo_data['likes'] += 1
                    metadata[fname] = photo_data
                    save_metadata(metadata)
                    st.rerun()
            with c2:
                st.markdown(f"**Posted by:** {sender}")

            with st.expander(f"💬 View Discussions ({len(photo_data['comments'])})"):
                msg = st.text_input("Write a comment...", key=f"msg_{idx}")
                if st.button("Submit", key=f"btn_{idx}"):
                    if user_name and msg:
                        photo_data['comments'].append(f"{user_name}: {msg}")
                        metadata[fname] = photo_data
                        save_metadata(metadata)
                        st.rerun()
                for c in photo_data['comments']:
                    st.markdown(f"> {c}")
            
            if is_admin:
                if st.button("🗑️ Remove Entry", key=f"del_{idx}"):
                    os.remove(photo_path)
                    if fname in metadata: del metadata[fname]
                    save_metadata(metadata)
                    st.rerun()
            st.divider()
