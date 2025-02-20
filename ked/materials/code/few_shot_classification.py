# %%
import pandas as pd
from datasets import Dataset, load_dataset
model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
fine_tuned_model_path=model+"-fine-tuned"

train_examples = 30*[{"text": "Ich mag mein Studium", "label_text": "positive"}, {"text": "Ich hasse mein Studium", "label_text": "negative"}]
eval_examples = 30*[{"text": "Was läuft in meinem Studium nur falsch?", "label_text": "negative"}, {"text": "Ich weiss nicht, was ich in meinem Studium mache.", "label_text": "positive"}]
test_examples = 30*[{"text": "Ich liebe mein Studium", "label_text": "positive"}]

train_ds=Dataset.from_pandas(pd.DataFrame(eval_examples))
eval_ds=Dataset.from_pandas(pd.DataFrame(eval_examples))
test_ds=Dataset.from_pandas(pd.DataFrame(eval_examples))

from fastfit import FastFit, FastFitTrainer

# Load the base ST model and setup the trainer
trainer = FastFitTrainer(
    model_name_or_path=model,
    label_column_name="label_text",
    text_column_name="text",
    num_train_epochs=1,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    max_text_length=128,
    dataloader_drop_last=False,
    num_repeats=1,
    optim="adafactor",
    clf_loss_factor=0.1,
    fp16=True,
    train_dataset=train_ds,
    validation_dataset=eval_ds,
    test_dataset=test_ds,
    # encoder=None
)

model=trainer.train()

model.save_pretrained(fine_tuned_model_path)


####
from tqdm import tqdm
from sklearn.metrics import classification_report
from transformers import AutoTokenizer, pipeline

# Step 1: Load a pre-trained model from disk
model = FastFit.from_pretrained(fine_tuned_model_path)
tokenizer = AutoTokenizer.from_pretrained(model)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer) #

# Step 2: Run predictions to calculate class level metrics
predictions = []
for row in tqdm(test_ds):
    predictions.append(classifier(row["text"])[0]["label"])

# test_df["fastfit_predictions"] = predictions
# print("FastFit Class Level Metrics:")
# print(classification_report(test_df["label_text"], test_df["fastfit_predictions"]))

# %%
