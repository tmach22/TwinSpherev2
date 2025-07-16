import streamlit as st
import requests
import uuid
import pandas as pd
from collections import Counter
from io import BytesIO
from PIL import Image

st.set_page_config(layout="wide")
st.title("🌀 Twinsphere AI — Simulate Social Media Reaction")

# === INPUT FORM ===
st.subheader("📝 Create a Crisis Post")
post_text = st.text_area("Enter your post text", max_chars=280, height=150)
image_url = st.text_input("Optional Image URL (must be public)", "")

if image_url:
    try:
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        st.image(img, caption="Attached Image", width=300)
    except Exception as e:
        st.error(f"Could not load image: {e}")

if st.button("Simulate Agent Reactions"):
    if not post_text.strip():
        st.warning("Please enter some text for the post.")
    else:
        with st.spinner("Running simulation..."):
            payload = {
                "post_text": post_text,
                "post_id": str(uuid.uuid4()),
                "image_url": image_url,
            }
            response = requests.post("http://localhost:8000/simulate", data=payload)

        if response.status_code == 200:
            st.success("✅ Simulation triggered successfully!")
            results = response.json()
            st.subheader("🧠 Agent Reactions")
            st.json(results)

            # === ANALYTICS ===
            df = pd.DataFrame(results)

            st.subheader("📊 Reaction Analytics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔁 Reaction Type Distribution")
                reaction_counts = df["reaction"].value_counts()
                st.bar_chart(reaction_counts)

            with col2:
                st.markdown("### 🔐 Avg Confidence by Reaction")
                confidence_avg = df.groupby("reaction")["confidence"].mean()
                st.bar_chart(confidence_avg)

            st.markdown("### 🏷️ Most Common Tags")
            all_tags = sum(df["tags"], [])
            tag_counts = Counter(all_tags)
            tag_df = pd.DataFrame(tag_counts.items(), columns=["Tag", "Count"]).sort_values("Count", ascending=False)
            st.dataframe(tag_df, use_container_width=True)

            st.markdown("### 🧠 Agent-Level Reactions")
            st.dataframe(
                df[["agent_name", "reaction", "confidence", "tags", "final_message"]],
                use_container_width=True
            )

            st.markdown("### 🔍 View Full Response by Agent")
            selected_agent = st.selectbox("Select agent", df["agent_name"])
            full = df[df["agent_name"] == selected_agent].iloc[0]
            st.markdown(f"**Agent Name**: {full['agent_name']}")
            st.markdown(f"**Reaction**: {full['reaction']}")
            st.markdown(f"**Confidence**: {full['confidence']}")
            st.markdown(f"**Reasoning**: {full['reasoning']}")
            st.markdown(f"**Tags**: {', '.join(full['tags'])}")
            st.markdown(f"**Final Message**: {full['final_message']}")

        else:
            st.error(f"❌ Failed with {response.status_code}: {response.text}")
