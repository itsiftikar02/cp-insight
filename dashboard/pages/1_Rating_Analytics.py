import pandas as pd
import plotly.express as px
import streamlit as st

import api_client as api

st.set_page_config(page_title="Rating Analytics", page_icon="📈", layout="wide")
api.require_login()
st.title("📈 Rating Analytics")

rating = api.get("/cf/analytics/rating/").json()
contests = api.get("/cf/analytics/contests/").json()

progression = rating.get("progression", [])
if not progression:
    st.warning("No contest data yet. Sync your handle on the Home page.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Best Rating", rating.get("best_rating") or "—")
col2.metric("Avg Rating Change / Contest", rating.get("avg_change", 0))
col3.metric("Best Rank", contests.get("best_rank") or "—")

# Rating progression line chart
df = pd.DataFrame(progression)
df["date"] = pd.to_datetime(df["date"])
fig = px.line(df, x="date", y="rating", markers=True,
              title="Rating Progression Over Time")
fig.update_layout(xaxis_title="Date", yaxis_title="Rating")
st.plotly_chart(fig, use_container_width=True)

# Contests by year bar chart
by_year = contests.get("by_year", {})
if by_year:
    ydf = pd.DataFrame({"Year": list(by_year.keys()),
                        "Contests": list(by_year.values())})
    fig2 = px.bar(ydf, x="Year", y="Contests", title="Contests by Year")
    st.plotly_chart(fig2, use_container_width=True)
    st.metric("Average Rank", contests.get("avg_rank") or "—")
