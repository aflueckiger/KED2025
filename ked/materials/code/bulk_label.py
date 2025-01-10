# %%
import spacy
import pandas as pd
from umap import UMAP
from sentence_transformers import SentenceTransformer


# load German language model
nlp = spacy.load("de_core_news_sm")

# Load dataframe with a parsed date column
df = pd.read_csv("../data/extended_swiss_media_wokeness.tsv", parse_dates=["pubtime"])

df.rename(columns={"content": "text"}, inplace=True)

# process documents efficiently (batch-wise)
df["doc"] = list(nlp.pipe(df["text"]))

df.head()

# %%

def transform_into_sentlevel_dataframe(df):
    data = []
    print("Number of documents:", len(df))
    for idx, row in df.iterrows():

        meta = row.to_dict()
        del meta["doc"]
        del meta["text"]

        for sent in row["doc"].sents:
            data_sent = {**meta}
            data_sent["text"] = sent.text
            data.append(data_sent)

    df_sent = pd.DataFrame(data)
    print("Number of sentences:", len(df_sent))

    return df_sent

# create a sentence-level dataframe
df_sent = transform_into_sentlevel_dataframe(df)

# set meta information to display in the interface (date is formatted)
df_sent["meta"] = df_sent["pubtime"].dt.strftime('%m/%d/%Y').astype(str) + ", " + df_sent["medium_code"]


# select only sentence with a particular term
# df_sent = df_sent[df_sent["text"].str.contains("woke", case=False)]

# filter out sentences with less than 15 characters
df_sent = df_sent[df_sent["text"].str.len() >= 15]
df_sent = df_sent.sample(5000, random_state=42)



# %%
# Build a sentence encoder pipeline with UMAP at the end.

# Calculate embeddings
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", trust_remote_code=True)
X_embeddings = model.encode(df_sent["text"].values)

# model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)
# task = "text-matching"
# X_embeddings = model.encode(sentences, task=task, prompt_name=task, truncate_dim=256)

# Reduce dimensions
umap = UMAP(random_state=42)
X_tfm = umap.fit_transform(X_embeddings)

# Add the reduced dimensions to the dataframe
df_sent["x"] = X_tfm[:, 0]
df_sent["y"] = X_tfm[:, 1]

# %%
import jscatter
import numpy as np
import pandas as pd
from IPython.display import display
from ipywidgets import HTML, Button, HBox, Layout, Text, VBox, Select
from sklearn.metrics.pairwise import cosine_similarity


class BaseTextAnnotator:
    """
    Interface for basic text exploration in embedded space.
    """

    def __init__(self, dataf, labels=None, X=None, encoder=None):
        self.dataf = dataf
        self.labels = labels
        self.X = X
        self.encoder = encoder

        self.init_labeling()
        self.create_widget()

    def create_widget(self):
        # scatter plot
        self.scatter = jscatter.Scatter(
            data=self.dataf,
            x="x",
            y="y",
            legend=True,
            color_by="label",
            width=500,
            height=500,
        )

        # query input
        self.text_query = Text(
            value="", placeholder="Type something", description="Query:"
        )

        # area to present texts
        self.html = HTML(
            layout=Layout(width="600px", overflow_y="scroll", height="400px")
        )

        self.sample_btn = Button(description="resample texts")

        self.label_drpdwn = Select(
            options=self.labels,
            description="Label:",
            disabled=False,
        )

        # layout
        self.elem = HBox(
            [
                VBox([self.text_query, self.scatter.show()]),
                VBox(
                    [
                        self.sample_btn,
                        self.label_drpdwn,
                        self.html,
                    ]
                ),
            ]
        )

        # event handlers
        self.text_query.observe(self.update_query)

        self.sample_btn.on_click(lambda d: self.update())
        self.label_drpdwn.observe(self.labeling)

        self.scatter.widget.observe(lambda d: self.update(), ["selection"])

    def init_labeling(self):
        if self.labels is not None and "label" not in self.dataf.columns:
            self.dataf["label"] = "unlabeled"

    def color_by_label(self):
        self.scatter.color(by=self.dataf["label"])
        self.scatter.size(1)

    def labeling(self, change):
        # filter as event gets triggered multiple times
        if change["new"] in self.labels:
            self.dataf.loc[widget.selected_idx, "label"] = change["new"]
            self.color_by_label()

    def show(self):
        return self.elem

    def update(self):
        if len(self.scatter.selection()) > 10:
            rows = self.dataf.iloc[self.scatter.selection()].sample(10)
        else:
            rows = self.dataf.iloc[self.scatter.selection()]

        texts = [
            f"""<p style="margin: 0px">
                    <b>{m} (<span style="color: darkblue">{l}</span>):</b> 
                    {t}
                </p>"""
            for t, l, m in zip(rows["text"], rows["label"], rows["meta"])
        ]
        self.html.value = "".join(sorted(texts))

    def update_query(self, change):
        if self.text_query.value:
            X_tfm = self.encoder.encode([self.text_query.value])
            dists = cosine_similarity(self.X, X_tfm).reshape(1, -1)
            self.dists = dists
            norm_dists = dists
            # norm_dists = 0.01 + (dists - dists.min()) / (
            #     0.1 + dists.max() - dists.min()
            # )
            self.scatter.color(by=norm_dists[0])
            self.scatter.size(by=norm_dists[0])
        else:
            # reset if query is empty
            self.color_by_label()

    def observe(self, func):
        self.scatter.widget.observe(func, ["selection"])

    @property
    def selected_idx(self):
        return self.scatter.selection()

    @property
    def selected_texts(self):
        return list(self.dataf.iloc[self.selection_idx]["text"])

    @property
    def selected_dataframe(self):
        return self.dataf.iloc[self.selection_idx]

    def _repr_html_(self):
        return display(self.elem)

    def save_data(self, path):
        self.dataf.to_csv(path, index=False)


labels = ["label1", "label2", "label3"]
widget = BaseTextAnnotator(df_sent, X=X_embeddings, encoder=model, labels=labels)
widget.show()

# %%
widget.save_data("labeled_data.csv")

# %%
import datamapplot

datamapplot.create_plot(
    X_tfm,
    widget.dataf["label"],
    title="Map of Embeddings",
    sub_title="Each sentence represents a point in the semantic space",
)
# %%

