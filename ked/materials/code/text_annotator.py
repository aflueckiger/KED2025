import jscatter
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

        self.size = 5

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
            axes=False,
            size=self.size,
        )

        # query input
        self.text_query = Text(
            value="", placeholder="Search for similar texts", description="Query:"
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
        self.label_drpdwn.observe(self.annotate)

        self.scatter.widget.observe(lambda d: self.update(), ["selection"])

    def init_labeling(self):
        if self.labels is not None and "label" not in self.dataf.columns:
            self.dataf["label"] = "unlabeled"

    def color_by_label(self):
        self.scatter.color(by=self.dataf["label"])

    def annotate(self, change):
        # filter as event gets triggered multiple times
        if change["new"] in self.labels:
            self.dataf.loc[self.selected_idx, "label"] = change["new"]
            self.color_by_label()
            self.update()

    def show(self):
        return self.elem

    def update(self):
        if len(self.selected_idx) > 10:
            rows = self.dataf.iloc[self.selected_idx].sample(10)
        else:
            rows = self.dataf.iloc[self.selected_idx]

        texts = [
            f"""<p style="margin: 0px">
                    <b>{m} (<span style="color: darkblue">{l}</span>):</b> 
                    {t}
                </p>"""
            for t, l, m in zip(rows["text"], rows["label"], rows["meta"])
        ]
        n_selected_text = f"<p><b>Number of selected texts: {len(self.selected_idx)}</b></p>"
        self.html.value = n_selected_text + "".join(sorted(texts))

    def update_query(self, change):
        if self.text_query.value:
            X_tfm = self.encoder.encode([self.text_query.value])
            dists = cosine_similarity(self.X, X_tfm).reshape(1, -1)
            self.scatter.color(by=dists[0], map='magma')
            # self.scatter.size(by=dists[0])

            # self.scatter.opacity(by=dists[0])

            self.scatter.color(labeling={
                "variable": "cosine similarity",
                "minValue": "min",
                "maxValue": "max", 
            })
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
        return list(self.dataf.iloc[self.selected_idx]["text"])

    @property
    def selected_dataframe(self):
        return self.dataf.iloc[self.selected_idx]

    def _repr_html_(self):
        return display(self.elem)

    def save_data(self, path):
        self.dataf.to_csv(path, index=False)
