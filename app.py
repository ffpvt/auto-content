import json
import streamlit as st
from PIL import Image
from google import genai
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Image to Content Generator", layout="wide")
st.title("🖼️ Image-to-Text ও কনটেন্ট জেনারেটর")

gemini_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=gemini_key)

def get_gsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(st.secrets["SHEET_ID"]).sheet1

uploaded_file = st.file_uploader("ছবি আপলোড করুন (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
content_goal = st.selectbox(
    "কোন ধরনের কনটেন্ট চান?",
    [
        "ছবির ভেতরের লেখা ও বিবরণ (Image to Text)",
        "ই-কমার্স প্রোডাক্ট ডেসক্রিপশন",
        "ফেসবুক / লিংকডইন পোস্ট ও ক্যাপশন",
        "ব্লগ আউটলাইন ও আর্টিকেল"
    ]
)
tone = st.text_input("লেখার টোন (যেমন: প্রফেশনাল, ফ্রেন্ডলি, সেলস-ফোকাসড)", value="সহজ ও প্রফেশনাল")

if uploaded_file and st.button("কনটেন্ট জেনারেট করুন"):
    image = Image.open(uploaded_file)
    st.image(image, caption="আপলোড করা ছবি", use_container_width=True)

    with st.spinner("Gemini বিশ্লেষণ করছে..."):
        prompt = (
            f"এই ছবিটি ভালোভাবে বিশ্লেষণ করো। প্রথমে ছবিতে থাকা দৃশ্য বা লেখা সংক্ষেপে বের করো, "
            f"তারপর '{content_goal}' তৈরি করো। টোন হবে: {tone}।"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt]
        )
        result_text = response.text

    st.subheader("তৈরি হওয়া কনটেন্ট")
    st.write(result_text)

    try:
        sheet = get_gsheet()
        sheet.append_row([uploaded_file.name, content_goal, result_text])
        st.success("Google Sheet-এ সফলভাবে সেভ হয়েছে!")
    except Exception as e:
        st.warning(f"Sheets-এ সেভ করতে সমস্যা হয়েছে: {e}")