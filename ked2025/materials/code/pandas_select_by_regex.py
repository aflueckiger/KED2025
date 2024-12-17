# define various regular expressions here
patterns = ["umwelt.*", "nachhaltig.*"]

dfs = []
for pat in patterns:

    df_temp = df_tidy[df_tidy["term"].str.contains(pat)].groupby("year").sum().reset_index()
    df_temp["term"] = pat
    dfs.append(df_temp)

df_terms = pd.concat(dfs) 
