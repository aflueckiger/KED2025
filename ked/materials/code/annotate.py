# %%
import spacy
import pandas as pd
from umap import UMAP
from sentence_transformers import SentenceTransformer

import datamapplot
from sklearn.feature_extraction.text import CountVectorizer

from bertopic import BERTopic
from hdbscan import HDBSCAN

from text_annotator import BaseTextAnnotator





# load German language model
nlp = spacy.load("de_core_news_sm")

# Load dataframe with a parsed date column
df = pd.read_csv("../data/extended_swiss_media_wokeness.tsv", parse_dates=["pubtime"])

df.rename(columns={"content": "text"}, inplace=True)

def clean_text(text):
    # clean up the text from newlines e.g.
    # '»\nBeim Rückgang der Abo-Erneuerungen handle es sich um einen Trend
    text = text.strip().replace("\n", " ")

    return text

df["text"] = df["text"].apply(clean_text)

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
df_sent = df_sent.sample(50, random_state=42).reset_index()

# %%
# Calculate embeddings
#"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer("Alibaba-NLP/gte-multilingual-base", trust_remote_code=True, )
X_embeddings = embedding_model.encode(df_sent["text"].values, show_progress_bar=True, normalize_embeddings=True)

# %%
# Reduce dimensions
umap = UMAP(random_state=42, n_components=2)
X_tfm = umap.fit_transform(X_embeddings)

# Add the reduced dimensions to the dataframe
df_sent["x"] = X_tfm[:, 0]
df_sent["y"] = X_tfm[:, 1]

# %%
# create the interactive widget
labels = ["your_label_1", "your_label_2", "your_label_3"]
widget = BaseTextAnnotator(df_sent, X=X_embeddings, encoder=embedding_model, labels=labels)
widget.show()

# %%
# save the current labeled data
widget.save_data("labeled_data.csv")

# %%

datamapplot.create_plot(
    X_tfm,
    widget.dataf["label"],
    title="Map of Embeddings",
    sub_title="Each sentence represents a point in the semantic space",
)




# %%
# create


docs = df_sent['text']

umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine')
hdbscan_model = HDBSCAN(min_cluster_size=30, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

topic_model = BERTopic(embedding_model=embedding_model, umap_model=umap_model, hdbscan_model=hdbscan_model)

topics, probs = topic_model.fit_transform(docs)

topic_model.get_topic_info()
topic_model.get_topics()
topic_model.topic_sizes_
topic_model.get_document_info(docs)


# %%


# refine topic descriptions

class LemmaTokenizer:
    def __call__(self, doc):
        return [tok.lemma_ for tok in nlp(doc) if tok.is_alpha and not tok.is_stop]

vectorizer_model = CountVectorizer(tokenizer=LemmaTokenizer(),  min_df=5)
topic_model.update_topics(docs, vectorizer_model=vectorizer_model)

# %%

df_tm = topic_model.get_document_info(docs)

df_merged =  pd.concat([df_sent.reset_index(), df_tm.reset_index()], axis=1)

datamapplot.create_plot(
    X_tfm,
    df_merged["Name"],
    title="Map of Embeddings",
    sub_title="Each sentence represents a point in the semantic space",
)

# %%
