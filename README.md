# Phoenix's Leading Fitness Center Analysis

## Goal

The main goal of our project is to analyze reviews of different gyms in Phoenix, Arizona. As ASU graduates looking for our next workout home now that we can no longer use the Sun Devil Fitness Complex, we thought it would be a great idea to use data science technologies to see which gyms in Phoenix (especially Maricopa County) have good reviews and to explore various characteristics that make a good gym (that people love). We use tools such but not limited to, Google Map API, Outscraper, Natural Language Processing (NLP), sentiment analysis, and matplotlib/seaborn for visualization.

## Data

### Sources / Collection Methods

We collected gym data and their Google reviews using 1."Google Map API" and 2."Outscraper".

**1. Google Map API (googlemap.py)**

* First, before using Google Map API, we go to the Google Cloud Platform and make valid Google Map API to get its API key
* Insert Google API key and query(search words:"**gym near Maricopa County, AZ**") into googlemap.py
* A) Scrape 59 gym data (**google place id, name, address, latitude, longitude, rating, rating_total**) from Google Map API(function: get_information_map)
* B) Collect details of gyms data and calculated business hours for our analysis (**weekday, Total Business hour**) from Google Map API (function: detail, calculate_hour)
* Create csv files (result_place_id.csv, result_detail.csv) that contain A and B above and Integrate them into **basic.csv** in the store directory

**2. Google Review Data (from Outscraper Website/API)**

* Outscraper(<https://outscraper.com/>) is the website we used to get reviews data from Google Maps (you can also use their API).
* We plugged in google place id that we collected from Google Map API into Outscraper and was able to collect reviews of each gyms up to 250 recent reviews (**resulting output is 'reviews.csv', which we placed in the data directory**).
  + We resorted to using Outscraper because Google Map API only allowed us to scrape up to five reviews per location as an individual(non-business) user.
  + Using Outscraper allowed us to scrape up to 250 reviews per gym at an affordable cost.
  + We got data that includes **reviews, author_title(reviewer's name), etc.**
  + Output is 'reviews.csv' file.

* Note: We produced reviews.csv based on the Google place ids we collected at the time of analysis.
  If you collect Google place ids now, you may get slightly different data sets from what we have.

## Analysis

### Methodology

* Main outputs are under the artifacts directory
* Other outputs are under the store directory in the artifacts
* We used pandas package to read and write csv files

**1. Word Count Analysis (wordcount.py)**

* Read review.csv from Outscraper in the directory
* Used **NLTK.tokenizer** package to break reviews down into separate words
* Excluded stopwords and additional stopwords and cleaned the data (function: tokenized_without_stopwords.py)
  + stopwords are in the stopwords.txt of the data directory
  + additional stop words in the additional_stop_words.txt include extra words that we added such as "phoenix", "gym", "arizona"
* CSV files are produced as output

**1.1 All word count (all_count.csv)**

* Count the frequency of all words in the all reviews dataset
* Output is the "all_count.csv" in the artifacts directory

**1.2 Word count by each gym (count_each_place.py)**

* Count the frequency of all words by each gym in the all reviews dataset
* Output is "count_plus_basic.csv" in the store directory (integrated with basic.csv)

**1.3 Word count by each gender (count_each_gender.py) with *gender-guesser* package**

* Count the frequency of all words by each gym by gender in the all reviews dataset
* Output is included in the "all_count.csv" in the artifacts directory

* What is the Gender-Guesser package?
  + Python package to guess gender based on the first names provided
  + We plug the first name of each reviewer's name(author title in review.csv) into gender guesser function
  + This function returns six different values: unknown (name not found), andy (androgynous/unisex), male, female, mostly_male, or mostly_female

[Packages]

* NLTK (Natural Language Toolkit) : <https://www.nltk.org/index.html>
* gender-guesser: <https://pypi.org/project/gender-guesser/>

**2. Sentiment Analysis (sentiment.py)**

**2.1 Sentiment score by each review (sentiment_analysis.py)**

NLTK.Vader / vaderSentiment (Valence Aware Dictionary for Sentiment Reasoning)

* Popular Natural Language Processing tool that identifies and extracts sentiment behind texts.
* Analyzes lexicon, grammatical rules, syntactical conventions to calculate sentiment scores.
* Read review.csv from Outscraper in the directory
* Put the reviews into the function **SentimentIntensityAnalyzer** to get sentiment scores (Positive/Negative/Neutral/Compound)
* Output is "sentimental_data.csv" in the store directory that contains below scores:

  + Positive
  + Negative
  + Neutral
  + Compound: Sum of positive, negative and neutral scores, normalized between -1 (most extreme negative) and +1 (most extreme positive)

**2.2 Mean and Standard Deviation of sentiment scores by each places**

* We also get the mean and the standard deviation of these scores by *each places*
* Output is the "senti_plus_count_basic" in the artifacts, which is integrated with other results

**2.3 Creating Reviewer_r.csv**

* Run sentiment.py, which combines the data from reviews.csv and the results from gender-guesser package.
* Output is "reviewer_r.csv"

[Packages]

* NLTK.Vader: <https://www.nltk.org/_modules/nltk/sentiment/vader.html>
* vaderSentiment: <https://github.com/cjhutto/vaderSentiment>

[Visualizations]

All of our plots and figures in our findings were created via matplotlib and seaborn. We used the gym/review data ('basic.csv' and 'all_count.csv') to produce charts and graphs to visualize our analyses.

### Description and Findings

* Gym Location
![Gym Location Map](plots/Gym_Location_Map1.png)

The map shows 59 gyms across Phoenix / Maricopa County. Most of the gyms are concentrated in the Central Phoenix and North Phoenix areas, particularly around the Camelback Corridor (85016) and the I-17 corridor. The color represents Google rating and the size represents the number of reviews.

* Gym Distribution by Zipcode
![Gym Distribution](plots/Gym_Distribution.png)

This chart displays the concentration of gyms by zipcode. As you can see, most of the gyms are located in zipcode 85016 (Camelback/Biltmore area), 85032 (North Mountain), and 85027 (North Phoenix near I-17). These are some of the most populated and commercially active areas of Phoenix.

* Bar Chart Showing Total Word Count
![Bar Chart for Word](plots/Bar_Chart_for_Word.png)

The bar graph shows the top twenty-two words that appeared the most in the Google reviews. We have ruled out some words such as 'great', 'awesome', 'feel', 'nice,' 'recommend', etc which are relatively meaningless in our analysis. 'Staff', 'equipment', 'clean', 'classes' are some of the words that were highly mentioned. This shows what kind of qualities the reviewers most care about.

Top Five Words Mentioned:
1. staff - 5,272 counts
2. classes - 2,231 counts
3. equipment - 2,108 counts
4. clean - 1,827 counts
5. incredible - 1,743 counts

* Gender Ratio of Reviews
![Gender Ratio](plots/male_female_review_ratio.png)

Based on the gender-guesser package, males (males + mostly_males) make up around 60% of the reviewers. Females (females + mostly_females) make up around 32%. About 7% are androgynous names. From this, we can find out that the majority of the reviews that we scraped for this analysis are males.

* Bubble Map Showing Word Count - Male
![Bubble Map Male](plots/Bubble_Map_for_Male.png)

We produced a bubble map showing most frequent words mentioned by males. Similar to the bar graph above, we dropped off meaningless words like 'nice', 'awesome', 'work', 'day', etc.

Top Five Words Mentioned by Males:
1. staff
2. classes
3. equipment
4. clean
5. incredible

* Bubble Map Showing Word Count - Female
![Bubble Map Female](plots/Bubble_Map_for_Female.png)

Top Five Words Mentioned by Females:
1. staff
2. equipment
3. classes
4. clean
5. incredible

* Sentiment Analysis
![Sentiment Ratio](plots/Ratio_of_Sentiment_Analysis.png)

Out of nearly 11,550 reviews we analyzed, around 88% had positive sentiment, 1% neutral, and 11% negative. The high positive sentiment rate reflects that the gyms in our dataset generally have high Google ratings (3.7 to 5.0).

* Sentiment Analysis and Google Reviews
![Compound vs Rating](plots/Relationship_Between_Compound_Mean_and_Google_Rating.png)

We wanted to see how good of a job the VADER package does in analyzing sentiment. So, we compared VADER's compound mean score (overall sentiment score normalized between -1 to 1) with Google ratings (0-5). We can see the two scores are positively correlated. A gym that has a higher compound mean sentiment score is more likely to have a higher Google review, and vice versa.

* Google Ratings and Business Hours
![Rating vs Hours](plots/Relationship_Between_GoogleRating_and_Business_Hour.jpeg)

Lastly, we were curious to see if there are any interesting relationships between the Google reviews and how long the gyms are open for. Would gyms that are open longer generally have higher reviews? From above plot, we can see that many gyms are open around 80 to 170 hours a week. The range of business hours ranged from 66 hours/week to 24/7 (168 hours/week). Looking at the data, longer business hours (>120 hrs/week) don't necessarily guarantee higher reviews. There are many gyms open for less than 100 hours/week yet have Google reviews around 4.7-5.0.

### Limitations

* We were only able to collect 59 gyms from the Google Maps API search results. More comprehensive coverage would require a business license.
* If one were to scrape gym review data now, the resulting data may be slightly different from ours because of changing place ids and review content.
* The gyms we collected data on have Google review ratings from 3.7 to 5.0. So, gyms with terrible to sub-par reviews (1 to 3) are not included.
* Google Map API selected gyms based on the searcher's location, which may have caused geographic bias in our data.
* Membership fees, which may be an interesting finding, was not included in our analysis because it would require more complex data collection.
* Regarding gender ratio analysis – we have some androgynous names that may have been mis-categorized.
* The Phoenix metro area is very large and sprawling; our analysis focuses on Phoenix proper and may not fully represent the broader metro (Scottsdale, Tempe, Mesa, Chandler, etc.).
