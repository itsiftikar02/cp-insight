import pandas as pd
import plotly.express as px
import streamlit as st

import api_client as api

st.set_page_config(page_title="Topic Analysis", page_icon="🧩", layout="wide")
api.require_login()
st.title("🧩 Topic-wise Analysis")

data = api.get("/cf/analytics/topics/").json()
per_topic = data.get("per_topic", {})
if not per_topic or sum(per_topic.values()) == 0:
    st.warning("No solved problems yet. Sync your handle on the Home page.")
    st.stop()

df = pd.DataFrame({"Topic": list(per_topic.keys()),
                   "Solved": list(per_topic.values())}).sort_values("Solved", ascending=False)

fig = px.bar(df, x="Topic", y="Solved", title="Problems Solved per Topic",
             color="Solved", color_continuous_scale="Blues")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.pie(df[df["Solved"] > 0], names="Topic", values="Solved",
              title="Topic Distribution")
st.plotly_chart(fig2, use_container_width=True)

c1, c2 = st.columns(2)
c1.subheader("Most practiced")
c1.write(", ".join(data.get("most_practiced", [])) or "—")
c2.subheader("Least practiced")
c2.write(", ".join(data.get("least_practiced", [])) or "—")
