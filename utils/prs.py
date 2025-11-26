def calculate_prs(df):
    prs = {}
    if df.empty:
        return prs
    prs["longest"] = df["distance"].max()
    return prs