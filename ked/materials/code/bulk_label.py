# %%
import spacy
import pandas as pd
from umap import UMAP
from sklearn.pipeline import make_pipeline

from embetter.text import SentenceEncoder



# load German language model
nlp = spacy.load("de_core_news_sm")

# Load dataframe
df = pd.read_csv("../data/dataset_speeches_federal_council_2019.csv")

# Drop rows with missing text
df = df.dropna(subset=["Text"])

# process documents efficiently (batch-wise)
df["doc"] = list(nlp.pipe(df["Text"]))

# %%

def transform_into_sentlevel_dataframe(df):
    data = []
    for idx, row in df.iterrows():

        meta = row.to_dict()
        print(meta.keys())
        meta.pop("doc").pop("Text")

        for sent in row["doc"].sents:
            data.append({"sentence": sent.text, **meta})

    return pd.DataFrame(data)

df_sent = transform_into_sentlevel_dataframe(df)
sentences = df_sent["sentence"].tolist()

# Build a sentence encoder pipeline with UMAP at the end.
enc = SentenceEncoder("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
umap = UMAP()

embedding_pipeline = make_pipeline(enc)
dim_reduction_pipeline = make_pipeline(umap)

# Calculate embeddings
X_embeddings = embedding_pipeline.fit_transform(sentences)
X_tfm = dim_reduction_pipeline.fit_transform(X_embeddings)

# Write to disk. Note! Text column must be named "text"
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

        self.html.value = "".join(
            [
                f'<p style="margin: 0px"><b>{l}:</b> {t}</p>'
                for t, l in zip(rows["text"], rows["label"])
            ]
        )

    def update_query(self, change):
        if self.text_query.value:
            X_tfm = self.encoder.transform([self.text_query.value])
            dists = cosine_similarity(self.X, X_tfm).reshape(1, -1)
            self.dists = dists
            norm_dists = 0.01 + (dists - dists.min()) / (
                0.1 + dists.max() - dists.min()
            )
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
widget = BaseTextAnnotator(df, X=X_embeddings, encoder=enc, labels=labels)
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
