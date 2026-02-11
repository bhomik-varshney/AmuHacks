import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/crisis-support"

st.set_page_config(
    page_title="Crisis Support AI",
    page_icon="🆘",
    layout="centered"
)

st.title("🆘 Crisis Support AI")
st.write("Share what's happening. Support options will appear below.")

user_text = st.text_area(
    "Your situation",
    placeholder="e.g. I lost my job and I am panicking"
)

if st.button("Get Support"):

    if not user_text.strip():
        st.warning("Please enter some text")

    else:
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"user_text": user_text},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    # 🔍 DEBUG: show raw backend response
                    st.subheader("RAW RESPONSE (Debug)")
                    st.json(data)

                    # ✅ Normal guidance steps
                    if "steps" in data and data["steps"]:
                        st.subheader("Guidance")
                        for step in data["steps"]:
                            msg = step.get("message")
                            if msg:
                                st.info(msg)

                    # 🚨 Emergency block
                    if data.get("status") == "emergency":
                        st.error("🚨 Emergency Support")
                        st.write(data.get("message", ""))

                        for action in data.get("actions", []):
                            if action.get("type") == "call":
                                st.button(
                                    f"📞 {action['label']} ({action['value']})"
                                )
                            else:
                                st.write("•", action.get("label", ""))

                else:
                    st.error(f"Server error: {response.status_code}")

            except Exception as e:
                st.error(f"Unable to connect to backend API: {e}")
