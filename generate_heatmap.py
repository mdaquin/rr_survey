import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

labels = {
    "== Findability  ==": "Findability",
    "== Accessibility ==": "Accessibility",
    "== Interoperability ==": "Interoperability",
    "== Reusability ==": "Reusability",
    "== Engagement ==": "Engagement",
    "== Social connections ==": "Social Connections",
    "== Trust ==": "Trust"
}

max_min_scores = {
    "Findability": (-7, 7),
    "Accessibility": (-4, 6),
    "Interoperability": (-9, 9),
    "Reusability": (-3, 3),
    "Engagement": (-4, 8),
    "Social Connections": (-9, 10),
    "Trust": (-11, 14)
}

final = {}
for label in labels:
    with open(sys.argv[1], encoding="utf8") as in_file:
        paper = in_file.readlines()
        idx = [paper.index(i) for i in paper if label in i][0] + 3
        end = idx + [paper[idx:].index(i) for i in paper[idx:] if "\end{tabular}" in i][0]

        table = [row.replace("\\", "").replace("hline", "").replace("textbf{", "").replace("}", "").replace(" ", "")
                     .strip().split("&") for row in paper[idx:end]]
        df = pd.DataFrame(table[1:], columns=table[0]).dropna()
        if "Systems" not in final:
            final["Systems"] = df[df.columns[0]].tolist()
        df = df.replace({"y": 1, "n": -1, "n/a": 0, "p": 0, "-": 0,
                         "h": 2, "m": 1, "l": 0, "c": -1, "a": 2, "s": 1
                         })
        if label == "== Accessibility ==":
            d = {"open": 1, "on-request": 0, "closed": -1}
            col = df["ACA3"].tolist()
            new_col = []
            for each in col:
                each = each.split(",")
                for i in range(len(each)):
                    each[i] = d[each[i]]

                new_col.append(sum(each))
            df["ACA3"] = new_col
        elif label == "== Trust ==":
            df["TCS2"] = 0
        df[labels[label]] = df.loc[:, df.columns[1]:].sum(axis=1)
        final[labels[label]] = df[labels[label]].tolist()

df = pd.DataFrame.from_dict(final)
df = df.set_index("Systems")
for feature_name in df.columns:
    df[feature_name] = (df[feature_name] - max_min_scores[feature_name][0]) / (max_min_scores[feature_name][1] -
                                                                               max_min_scores[feature_name][0])
sns.set(rc={"figure.figsize": (5, 6)})
sns.set_theme()
ax = sns.heatmap(df, cmap="YlGnBu", cbar_kws={"orientation": "horizontal", "pad": 0.3,
                                              "ticks": [0, 0.5, 1],
                                              "label": "Adherence to principle"})
plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
cbar = ax.collections[0].colorbar
cbar.ax.set_xticklabels(['Low', 'Medium', 'High'])
plt.savefig("heatmap.pdf", bbox_inches="tight")
