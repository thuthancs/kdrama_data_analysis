# Data Collection
I automatically scraped the list of K-dramas in the 2000s, 2010s, and 2020s from IMDB to get data for the following fields: `name`, `release_year`, `num_episodes`, `rating_type`, `rating_score`, `cast`, and `short_description`. Because the HTML does not include the genre tag, I need to manually export the list of those three periods and copy and paste the genre into the original file. 

For the plot, I first manually copied from Wikipedia pages for each drama, but after 15 minutes, I was too tired of repetitive copy-pasting, so I came up with an idea: 
- I asked [Perplexity](https://www.perplexity.ai/search/based-on-this-list-of-k-drama-RuM1_xkfRO2EZmNL53eZEw#0) to generate all Wikipedia links associated with each K-drama and export them as a JSON file. There was one link that was incorrect, so I had to replace it manually. The link for Empress Ki Kdrama should be https://en.wikipedia.org/wiki/Empress_Ki_(TV_series), not https://en.wikipedia.org/wiki/Empress_Gi
- Then, I defined a logic in Python to do the scraping for the `screen_writer`, `director`, `network_provider`, and `plot`.

The HTML across all the pages is not completely consistent. For example, the majority of the page used "Written by" to indicate the screenwriter, but some used "Screenplay", so the code helped me scrape 90% of the links and I had to manually fill out the remaining 10%.

All data is saved in this [Google Spreadsheet](https://docs.google.com/spreadsheets/d/1ID4lt2oMSvFeiEDxz_twjI_ElDnNDNjolfCZ5FhWzWM/edit?gid=1189053792#gid=1189053792). 

# Exploratory Data Analysis
