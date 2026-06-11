import streamlit as st

import api_client as api

st.set_page_config(page_title="Recommendations", page_icon="💡", layout="wide")
api.require_login()
st.title("💡 Recommendations")

st.write("Recommendations are generated from rule-based weakness detection.")

if st.button("Generate fresh recommendations"):
    resp = api.post("/cf/recommend/")
    if resp.status_code == 201:
        st.success("Generated!")
    else:
        st.error("Could not generate. Sync your handle first.")

st.subheader("Detected weaknesses")
for w in api.get("/cf/analytics/weaknesses/").json():
    st.write(f"- {w['message']}")

st.subheader("Recommendation history")
recs = api.get("/planner/recommendations/").json()
results = recs.get("results", recs) if isinstance(recs, dict) else recs
if not results:
    st.info("No recommendations generated yet.")
for r in results:
    with st.container(border=True):
        st.markdown(f"**{r['topic']}**")
        st.write(r["message"])
        st.caption(r["created_at"][:10])
