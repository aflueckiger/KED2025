

# %%

from sklearn.cluster import HDBSCAN
import numpy as np



def generate_clusters(message_embeddings,
                      n_neighbors,
                      n_components, 
                      min_cluster_size,
                      max_cluster_size,
                      random_state = 42):
    """
    Generate HDBSCAN cluster object after reducing embedding dimensionality with UMAP
    """
    np.random.seed(random_state)

    umap_embeddings = (UMAP(n_neighbors=n_neighbors, 
                                n_components=n_components, 
                                random_state=random_state)
                            .fit_transform(message_embeddings))

    clusters = HDBSCAN(min_cluster_size = min_cluster_size, max_cluster_size=max_cluster_size).fit(umap_embeddings)

    return clusters

clusters = generate_clusters(X_embeddings, n_neighbors=15, n_components=5, min_cluster_size=30, max_cluster_size=1000)

df_sent["cluster"] = clusters.labels_


# inspect clusters
print("Number of clusters:", len(clusters.labels_))
for cl in sorted(df_sent.cluster.unique()):
    n_items = len(df_sent[df_sent.cluster == cl])
    print(f"Cluster {cl} (n={n_items})")
    print(df_sent[df_sent.cluster == cl].sample(10)["text"].values)
    print("\n")


from collections import Counter

def extract_labels(category_docs):
    """
    Extract labels from documents in the same cluster by concatenating
    most common verbs, ojects, and nouns
    """

    verbs = Counter()
    dobjs = Counter()
    nouns = Counter()
    adjs = Counter()

    # for each document, append verbs, dobs, nouns, and adjectives to 
    # running lists for whole cluster
    for i in range(len(category_docs)):
        doc = nlp(category_docs[i])
        for token in doc:
            if token.is_stop==False:
                if token.dep_ == 'ROOT':
                    verbs[token.lemma_.lower()] += 1

                elif token.dep_=='da':
                    dobjs[token.lemma_.lower()] += 1

                elif token.pos_=='NOUN':
                    nouns[token.lemma_.lower()] += 1
                    
                elif token.pos_=='ADJ':
                    adjs[token.lemma_.lower()] += 1

    # add words if not zero
    label_words = []
    if verbs:
        label_words.append(verbs.most_common(1)[0][0])
    if dobjs:
        label_words.append(dobjs.most_common(1)[0][0])
    if nouns:
        for word, count in nouns.most_common(3):
            if word not in label_words:
                label_words.append(word)

    label = ', '.join(label_words) + f" ({len(category_docs)})"
    
    return label


df_auto_labels = df_sent.groupby("cluster")["text"].apply(lambda x: extract_labels(x.values)).reset_index().rename(columns={"text": "auto_label"})

# join on cluster
df_merged = df_sent.merge(df_auto_labels, on="cluster")
