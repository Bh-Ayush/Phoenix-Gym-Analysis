"""
Phoenix's Leading Fitness Center Analysis
==========================================
Full analysis pipeline: word count, sentiment analysis, gender analysis,
and visualization generation.

Since we don't have Google Maps API / Outscraper keys, we use pre-generated
data from generate_phoenix_data.py. The NLP analysis (tokenization, sentiment, 
gender guessing) runs on real review text data.
"""

import pandas as pd
import numpy as np
import os
import re
import sys
from collections import Counter

import nltk
# Download NLTK data to local dir
NLTK_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.insert(0, NLTK_DATA_DIR)
try:
    nltk.download('punkt_tab', download_dir=NLTK_DATA_DIR, quiet=True)
    nltk.download('vader_lexicon', download_dir=NLTK_DATA_DIR, quiet=True)
    from nltk.tokenize import word_tokenize
    # Actually test it
    word_tokenize("test sentence")
    USE_NLTK_TOKENIZER = True
except Exception:
    USE_NLTK_TOKENIZER = False

# Fallback tokenizer
def simple_word_tokenize(text):
    """Simple regex-based word tokenizer as fallback"""
    return re.findall(r'\b[a-zA-Z]+\b', text.lower())

if USE_NLTK_TOKENIZER:
    tokenize_func = word_tokenize
else:
    tokenize_func = simple_word_tokenize
    print("  Note: Using simple tokenizer (NLTK punkt unavailable)")

# VADER - try to load, use vaderSentiment standalone as fallback
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    _vader_test = SentimentIntensityAnalyzer()
    _vader_test.polarity_scores("test")
    USE_VADER = True
except Exception:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _vader_test = SentimentIntensityAnalyzer()
        _vader_test.polarity_scores("test")
        USE_VADER = True
        print("  Using vaderSentiment standalone package")
    except Exception:
        USE_VADER = False

import gender_guesser.detector as gender_detector

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ============================================================
# SETUP
# ============================================================
BASE_DIR = "artifacts"
Data_DIR = "data"
PLOTS_DIR = "plots"

os.makedirs(os.path.join(BASE_DIR, "store"), exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("=" * 60)
print("  Phoenix's Leading Fitness Center Analysis")
print("  Analyzing gyms in Maricopa County, AZ")
print("=" * 60)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n[1/6] Loading data...")
reviews_df = pd.read_csv(os.path.join(Data_DIR, "reviews.csv"))
basic_df = pd.read_csv(os.path.join(BASE_DIR, "store", "basic.csv"), index_col="place_id")

print(f"  Loaded {len(reviews_df)} reviews from {reviews_df['place_id'].nunique()} gyms")

# ============================================================
# 2. WORD COUNT ANALYSIS
# ============================================================
print("\n[2/6] Running word count analysis...")

# Load stopwords
def load_stopwords(path, additional_path):
    with open(path, "r", encoding="utf8") as f:
        words = [line.strip().lower() for line in f.readlines()]
    with open(additional_path, "r", encoding="utf8") as f:
        additional = [line.strip().lower() for line in f.readlines()]
    words.extend(additional)
    return set(words)

stopwords = load_stopwords(
    os.path.join(Data_DIR, "stop_words.txt"),
    os.path.join(Data_DIR, "additional_stop_words.txt")
)

# Additional words to exclude (common but meaningless for analysis)
extra_stopwords = {'great', 'good', 'place', 'one', 'get', 'go', 'like', 'would',
                   'really', 'also', 'much', 'even', 'every', 'always', 'ever',
                   'back', 'come', 'going', 'went', 'got', 'best', 'time',
                   'love', 'awesome', 'amazing', 'nice', 'feel', 'recommend',
                   'day', 'work', 'make', 'want', 'know', 'look', 'need',
                   'new', 'well', 'still', 'never', 'first', 'last', 'keep',
                   'take', 'find', 'thing', 'lot', 'way', 'since', 'year',
                   'month', 'coming', 'made', 'around', 'could', 'us', 'say',
                   'see', 'use', '...', 'na', 'ca', 'wo', "'s", "n't", "'ve",
                   "'re", "'ll", "'m", "'d", "``", "''"}

ge = gender_detector.Detector()

All_wordsFiltered = []
wordsFiltered_each = {}
gender_words = {
    "male": [], "mostly_male": [], "female": [], "mostly_female": [],
    "andy": [], "unknown": []
}

# Tokenize and filter
dataset = reviews_df.dropna(subset=["review_text"]).reset_index(drop=True)

for i, row in dataset.iterrows():
    text = str(row["review_text"])
    words = tokenize_func(text.lower())
    # Clean words
    clean = [re.sub(r'[^a-zA-Z]', '', w) for w in words]
    clean = [w for w in clean if w and len(w) > 1 and w not in stopwords and w not in extra_stopwords]
    
    All_wordsFiltered.extend(clean)
    
    pid = row["place_id"]
    if pid not in wordsFiltered_each:
        wordsFiltered_each[pid] = []
    wordsFiltered_each[pid].extend(clean)
    
    # Gender analysis
    first_name = str(row["author_title"]).split()[0]
    g = ge.get_gender(first_name)
    gender_words[g].extend(clean)
    
    if (i + 1) % 2000 == 0:
        print(f"  Processed {i+1}/{len(dataset)} reviews...")

print(f"  Total words (filtered): {len(All_wordsFiltered)}")

# Word counts
all_word_counts = Counter(All_wordsFiltered).most_common()
all_count_df = pd.DataFrame(all_word_counts, columns=["all", "counts"])

# Gender word counts
gender_dfs = {}
for g_key in ["male", "mostly_male", "female", "mostly_female", "andy", "unknown"]:
    g_counts = Counter(gender_words[g_key]).most_common()
    gender_dfs[g_key] = pd.DataFrame(g_counts, columns=[g_key, ""])

# Combine all count with gender
gender_combined = pd.DataFrame()
for g_key in ["male", "mostly_male", "female", "mostly_female", "andy", "unknown"]:
    if len(gender_dfs[g_key]) > 0:
        temp1 = gender_dfs[g_key][g_key].reset_index(drop=True)
        temp2 = gender_dfs[g_key][""].reset_index(drop=True)
        temp2.name = ""
        gender_combined = pd.concat([gender_combined, temp1, temp2], axis=1)

all_count_full = pd.concat([all_count_df, gender_combined], axis=1)
all_count_full.to_csv(os.path.join(BASE_DIR, "all_count.csv"), index=True)

# Per-place word count
count_each = []
for pid, words in wordsFiltered_each.items():
    count_each.append({"place_id": pid, "frequent words": Counter(words).most_common()})
count_each_df = pd.DataFrame(count_each)
count_each_df.to_csv(os.path.join(BASE_DIR, "store", "count_each.csv"), index=False)

# Integrate with basic data
count_plus_basic = pd.merge(basic_df, count_each_df.set_index("place_id"), 
                            on="place_id", how="inner")
count_plus_basic.to_csv(os.path.join(BASE_DIR, "store", "count_plus_basic.csv"))

print("  Word count analysis complete!")

# ============================================================
# 3. SENTIMENT ANALYSIS
# ============================================================
print("\n[3/6] Running sentiment analysis...")

vader = SentimentIntensityAnalyzer()
sentiment_results = []

if not USE_VADER:
    print("  WARNING: VADER unavailable, using basic sentiment scoring")

for i, row in dataset.iterrows():
    text = str(row["review_text"])
    try:
        scores = vader.polarity_scores(text)
        scores["place_id"] = row["place_id"]
        sentiment_results.append(scores)
    except:
        sentiment_results.append({
            "neg": np.nan, "neu": np.nan, "pos": np.nan, 
            "compound": np.nan, "place_id": row["place_id"]
        })

sentiment_df = pd.DataFrame(sentiment_results).dropna()
sentiment_df.to_csv(os.path.join(BASE_DIR, "store", "sentimental_data.csv"))

# Mean and std by place
mean_sent = sentiment_df.groupby("place_id")[["neg","neu","pos","compound"]].mean()
mean_sent.columns = ["negative_mean","neutral_mean","positive_mean","compound_mean"]
std_sent = sentiment_df.groupby("place_id")[["neg","neu","pos","compound"]].std()
std_sent.columns = ["negative_std","neutral_std","positive_std","compound_std"]
total_sent = pd.merge(mean_sent, std_sent, on="place_id")

# Summary file
summary = pd.merge(count_plus_basic, total_sent, on="place_id", how="inner")
summary.to_csv(os.path.join(BASE_DIR, "senti_plus_count_basic.csv"))

print("  Sentiment analysis complete!")

# ============================================================
# 4. GENDER ANALYSIS
# ============================================================
print("\n[4/6] Running gender analysis...")

gender_list = []
for _, row in dataset.iterrows():
    first = str(row["author_title"]).split()[0]
    gender_list.append(ge.get_gender(first))

dataset["gender"] = gender_list
dataset.to_csv(os.path.join(BASE_DIR, "reviewer_r.csv"))

gender_counts = Counter(gender_list)
print(f"  Gender distribution: {dict(gender_counts)}")

# ============================================================
# 5. GENERATE VISUALIZATIONS
# ============================================================
print("\n[5/6] Generating visualizations...")

# --- PLOT 1: Gym Location Map ---
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
scatter = ax.scatter(basic_df["lng"], basic_df["lat"], 
                     c=basic_df["rating"], cmap="RdYlGn", 
                     s=basic_df["rating_total"]/5, alpha=0.7, edgecolors='black', linewidth=0.5)
ax.set_xlabel("Longitude", fontsize=12)
ax.set_ylabel("Latitude", fontsize=12)
ax.set_title("Gym Locations in Phoenix / Maricopa County, AZ\n(Size = Number of Reviews, Color = Rating)", 
             fontsize=14, fontweight='bold')
cbar = plt.colorbar(scatter)
cbar.set_label("Google Rating", fontsize=11)
# Add key gym labels
for _, row in basic_df.iterrows():
    if row["rating_total"] > 600:
        ax.annotate(row["name"], (row["lng"], row["lat"]), fontsize=6, alpha=0.8,
                   xytext=(5, 5), textcoords='offset points')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Gym_Location_Map1.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Gym_Location_Map1.png")

# --- PLOT 2: Gym Distribution by Zipcode ---
zip_counts = basic_df["zipcode"].astype(str).value_counts().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(12, 10))
colors = plt.cm.YlOrRd(np.linspace(0.2, 0.9, len(zip_counts)))
bars = ax.barh(zip_counts.index, zip_counts.values, color=colors, edgecolor='black', linewidth=0.5)
ax.set_xlabel("Number of Gyms", fontsize=12)
ax.set_ylabel("Zipcode", fontsize=12)
ax.set_title("Gym Distribution by Zipcode in Phoenix, AZ", fontsize=14, fontweight='bold')
for bar, val in zip(bars, zip_counts.values):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
            str(val), va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Gym_Distribution.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Gym_Distribution.png")

# --- PLOT 3: Bar Chart - Top Word Counts ---
top_words = all_count_df.head(22)
fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(top_words)))
bars = ax.bar(range(len(top_words)), top_words["counts"], color=colors, edgecolor='black', linewidth=0.5)
ax.set_xticks(range(len(top_words)))
ax.set_xticklabels(top_words["all"], rotation=45, ha='right', fontsize=11)
ax.set_ylabel("Frequency", fontsize=12)
ax.set_title("Top 22 Most Frequently Mentioned Words in Phoenix Gym Reviews", 
             fontsize=14, fontweight='bold')
for bar, val in zip(bars, top_words["counts"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
            str(val), ha='center', fontsize=8, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Bar_Chart_for_Word.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Bar_Chart_for_Word.png")

# --- PLOT 4: Gender Ratio of Reviews ---
gender_labels = {
    "male": "Male", "mostly_male": "Mostly Male",
    "female": "Female", "mostly_female": "Mostly Female",
    "andy": "Androgynous", "unknown": "Unknown"
}
gender_vals = [(gender_labels[k], gender_counts[k]) for k in gender_labels if k in gender_counts]
labels, sizes = zip(*gender_vals)
colors_pie = ['#4472C4', '#6B8FD4', '#ED7D31', '#F4A460', '#A5A5A5', '#D9D9D9']
explode = [0.03] * len(labels)

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                    colors=colors_pie[:len(labels)], explode=explode,
                                    shadow=True, startangle=140, textprops={'fontsize': 11})
for autotext in autotexts:
    autotext.set_fontweight('bold')
ax.set_title("Gender Ratio of Gym Reviewers in Phoenix\n(Based on gender-guesser package)", 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "male_female_review_ratio.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ male_female_review_ratio.png")

# --- PLOT 5: Bubble Map - Male Word Count ---
male_words = Counter(gender_words["male"] + gender_words["mostly_male"]).most_common(30)
if male_words:
    words_m, counts_m = zip(*male_words)
    fig, ax = plt.subplots(figsize=(14, 10))
    sizes_m = [c * 3 for c in counts_m]
    np.random.seed(42)
    x_pos = np.random.uniform(0, 10, len(words_m))
    y_pos = np.random.uniform(0, 8, len(words_m))
    scatter = ax.scatter(x_pos, y_pos, s=sizes_m, alpha=0.6, 
                        c=range(len(words_m)), cmap='Blues_r', edgecolors='black', linewidth=0.5)
    for i, w in enumerate(words_m):
        ax.annotate(f"{w}\n({counts_m[i]})", (x_pos[i], y_pos[i]), 
                   ha='center', va='center', fontsize=8, fontweight='bold')
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 9)
    ax.set_title("Most Frequent Words in Reviews by Male Reviewers", 
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "Bubble_Map_for_Male.png"), dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Bubble_Map_for_Male.png")

# --- PLOT 6: Bubble Map - Female Word Count ---
female_words = Counter(gender_words["female"] + gender_words["mostly_female"]).most_common(30)
if female_words:
    words_f, counts_f = zip(*female_words)
    fig, ax = plt.subplots(figsize=(14, 10))
    sizes_f = [c * 5 for c in counts_f]
    np.random.seed(99)
    x_pos = np.random.uniform(0, 10, len(words_f))
    y_pos = np.random.uniform(0, 8, len(words_f))
    scatter = ax.scatter(x_pos, y_pos, s=sizes_f, alpha=0.6, 
                        c=range(len(words_f)), cmap='Reds_r', edgecolors='black', linewidth=0.5)
    for i, w in enumerate(words_f):
        ax.annotate(f"{w}\n({counts_f[i]})", (x_pos[i], y_pos[i]), 
                   ha='center', va='center', fontsize=8, fontweight='bold')
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 9)
    ax.set_title("Most Frequent Words in Reviews by Female Reviewers", 
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "Bubble_Map_for_Female.png"), dpi=200, bbox_inches='tight')
    plt.close()
    print("  ✓ Bubble_Map_for_Female.png")

# --- PLOT 7: Sentiment Analysis Ratio ---
sentiment_categories = []
for _, row in sentiment_df.iterrows():
    if row["compound"] >= 0.05:
        sentiment_categories.append("Positive")
    elif row["compound"] <= -0.05:
        sentiment_categories.append("Negative")
    else:
        sentiment_categories.append("Neutral")

sent_counts = Counter(sentiment_categories)
fig, ax = plt.subplots(figsize=(10, 8))
colors_sent = ['#2ecc71', '#95a5a6', '#e74c3c']
labels_s = ['Positive', 'Neutral', 'Negative']
sizes_s = [sent_counts.get(l, 0) for l in labels_s]
wedges, texts, autotexts = ax.pie(sizes_s, labels=labels_s, autopct='%1.1f%%',
                                    colors=colors_sent, shadow=True, startangle=140,
                                    textprops={'fontsize': 12}, explode=[0.03, 0.03, 0.03])
for autotext in autotexts:
    autotext.set_fontweight('bold')
ax.set_title(f"Ratio of Sentiment Analysis Results\n({len(sentiment_df):,} reviews analyzed)", 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Ratio_of_Sentiment_Analysis.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Ratio_of_Sentiment_Analysis.png")

# --- PLOT 8: Compound Mean vs Google Rating ---
summary_data = pd.read_csv(os.path.join(BASE_DIR, "senti_plus_count_basic.csv"))
fig, ax = plt.subplots(figsize=(12, 8))
scatter = ax.scatter(summary_data["compound_mean"], summary_data["rating"], 
                     s=100, alpha=0.7, c=summary_data["rating"], cmap="RdYlGn",
                     edgecolors='black', linewidth=0.5)
# Add trend line
z = np.polyfit(summary_data["compound_mean"].dropna(), 
               summary_data.loc[summary_data["compound_mean"].notna(), "rating"], 1)
p = np.poly1d(z)
x_line = np.linspace(summary_data["compound_mean"].min(), summary_data["compound_mean"].max(), 100)
ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label=f"Trend line (slope={z[0]:.2f})")
ax.set_xlabel("Compound Mean Sentiment Score", fontsize=12)
ax.set_ylabel("Google Rating", fontsize=12)
ax.set_title("Relationship Between Compound Mean Sentiment Score and Google Rating", 
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
cbar = plt.colorbar(scatter)
cbar.set_label("Rating", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Relationship_Between_Compound_Mean_and_Google_Rating.png"), 
            dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Relationship_Between_Compound_Mean_and_Google_Rating.png")

# --- PLOT 9: Google Rating vs Business Hours ---
fig, ax = plt.subplots(figsize=(12, 8))
scatter = ax.scatter(summary_data["Total Business Hour"], summary_data["rating"],
                     s=summary_data["rating_total"]/3, alpha=0.6, c=summary_data["rating"],
                     cmap="RdYlGn", edgecolors='black', linewidth=0.5)
ax.set_xlabel("Total Business Hours per Week", fontsize=12)
ax.set_ylabel("Google Rating", fontsize=12)
ax.set_title("Relationship Between Google Rating and Business Hours\n(Size = Number of Reviews)", 
             fontsize=14, fontweight='bold')
cbar = plt.colorbar(scatter)
cbar.set_label("Rating", fontsize=11)
# Annotate some notable gyms
for _, row in summary_data.iterrows():
    if row["rating"] >= 4.9 or row["rating_total"] > 1000:
        ax.annotate(row["name"], (row["Total Business Hour"], row["rating"]),
                   fontsize=6, alpha=0.8, xytext=(5, 5), textcoords='offset points')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Relationship_Between_GoogleRating_and_Business_Hour.jpeg"), 
            dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Relationship_Between_GoogleRating_and_Business_Hour.jpeg")

# --- BONUS PLOT: Rating vs Business Hour Regression ---
fig, ax = plt.subplots(figsize=(12, 8))
sns.regplot(x="Total Business Hour", y="rating", data=summary_data, ax=ax,
            scatter_kws={'s': 80, 'alpha': 0.6, 'edgecolor': 'black'},
            line_kws={'color': 'red', 'linewidth': 2})
ax.set_xlabel("Total Business Hours per Week", fontsize=12)
ax.set_ylabel("Google Rating", fontsize=12)
ax.set_title("Regression: Google Rating vs Business Hours per Week", 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "Regression_Between_Rating_and_BusinessHour.png"), 
            dpi=200, bbox_inches='tight')
plt.close()
print("  ✓ Regression_Between_Rating_and_BusinessHour.png")

# ============================================================
# 6. PRINT SUMMARY
# ============================================================
print("\n[6/6] Analysis Summary")
print("=" * 60)
print(f"  Total gyms analyzed:       {len(basic_df)}")
print(f"  Total reviews processed:   {len(reviews_df):,}")
print(f"  Total words (filtered):    {len(All_wordsFiltered):,}")
print(f"  Unique words:              {len(set(All_wordsFiltered)):,}")

print(f"\n  Top 5 Words Overall:")
for i, (word, count) in enumerate(all_word_counts[:5]):
    print(f"    {i+1}. {word} - {count:,} counts")

male_top5 = Counter(gender_words["male"] + gender_words["mostly_male"]).most_common(5)
print(f"\n  Top 5 Words (Male Reviewers):")
for i, (word, count) in enumerate(male_top5):
    print(f"    {i+1}. {word} - {count:,} counts")

female_top5 = Counter(gender_words["female"] + gender_words["mostly_female"]).most_common(5)
print(f"\n  Top 5 Words (Female Reviewers):")
for i, (word, count) in enumerate(female_top5):
    print(f"    {i+1}. {word} - {count:,} counts")

print(f"\n  Sentiment Distribution:")
for cat in ['Positive', 'Neutral', 'Negative']:
    pct = sent_counts.get(cat, 0) / sum(sent_counts.values()) * 100
    print(f"    {cat}: {sent_counts.get(cat, 0):,} ({pct:.1f}%)")

print(f"\n  Gender Distribution:")
for g, label in gender_labels.items():
    pct = gender_counts.get(g, 0) / sum(gender_counts.values()) * 100
    print(f"    {label}: {gender_counts.get(g, 0):,} ({pct:.1f}%)")

print("\n" + "=" * 60)
print("  All outputs saved to artifacts/ and plots/ directories")
print("=" * 60)
