from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from collections import Counter
import re

import requests
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load datasets
contestants_df = pd.read_csv('../dataset/contestants_cleaned.csv')
votes_df = pd.read_csv('../dataset/votes_cleaned.csv')
countries_regions_df = pd.read_csv('../dataset/countries.csv')
country_df = pd.read_csv('../dataset/country_mapping_iso.csv')
country_df['Code'] = country_df['Code'].str.lower()

voting_matrix = votes_df.pivot_table(
    index='from_country_id',
    columns='to_country_id',
    values='perc_of_max',  # Replace with your relevant value column
    aggfunc='sum',
    fill_value=0
)
all_columns = voting_matrix.columns.tolist()

# Standardize the voting matrix
scaler = StandardScaler()
standardized_matrix = scaler.fit_transform(voting_matrix)

# global PCA for stable plotting
pca = PCA(n_components=2)
pca.fit(standardized_matrix)

initial_centroids = np.random.RandomState(42).rand(6, 2)  # Adjust dimensions to match your data

# Endpoint: Most Dominating Countries
#  --> adjust s.t:
# - for each year it adds the points
@app.route('/api/most_dominating_countries', methods=['GET'])
def most_dominating_countries():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400

    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]

    dominating_countries = (
        filtered.groupby('to_country')['per_of_pot_max']
        .sum()
        .reset_index()
        .rename(columns={'per_of_pot_max': 'total_points'})
        .sort_values('total_points', ascending=False)
    )
    return jsonify(dominating_countries.to_dict(orient='records'))

# Endpoint: returns all countries
@app.route('/api/available_countries', methods=['GET'])
def get_available_countries():
    years = countries_regions_df['country_name'].unique().tolist()
    years.sort(reverse=True)  # Optional: Sort years in descending order
    return jsonify(years)

# Endpoint: Get all available years from dataset
@app.route('/api/available_years', methods=['GET'])
def get_available_years():
    years = contestants_df['year'].unique().tolist()
    years.sort(reverse=True)  # Optional: Sort years in descending order
    return jsonify(years)

# Endpoint: Yearly Rankings (ranking 0 = not participated)
@app.route('/api/yearly_rankings', methods=['GET'])
def yearly_rankings():
    # Filter by year if provided
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400


    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]

    yearly_rankings = (
        filtered.groupby(['year', 'to_country'])['place_contest']
        .min()  # If there are multiple entries per country per year, take the best rank (smallest value)
        .reset_index()
        .pivot(index='year', columns='to_country', values='place_contest')
        .fillna(0)  # Fill NaN values with 0 to indicate no participation
        .astype(int)  # Convert rankings to integers
    )

    return jsonify(yearly_rankings.to_dict())

# Endpoint: Word Cloud Data
@app.route('/api/word_cloud', methods=['GET'])
def word_cloud():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    
    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400

    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]

    # Combine all lyrics into a single string
    all_lyrics = " ".join(filtered['lyrics_token'].dropna())

    # Preprocess lyrics: remove non-alphanumeric characters and convert to lowercase
    processed_lyrics = re.sub(r'[^a-zA-Z\s]', '', all_lyrics).lower()

    # Split into words and count occurrences
    word_counts = Counter(processed_lyrics.split())

    # Get the 15 most common words
    common_words = word_counts.most_common(30)

    # Convert to JSON format
    word_cloud_data = [{"word": word, "count": count} for word, count in common_words]

    return jsonify(word_cloud_data)

# Endpoint with filtered countries
# To Do:
# - finish logic here as specified below
# - add dropdown in frontend
# - add watcher in dropdown that saves the selected filter (default = All)
# - pass it as a param and get the correct data returned, rest stays the same
@app.route('/api/word_cloud_filter', methods=['GET'])
def word_cloud_filter():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    selectedFilter = request.args.get('filter', type=str)
    print(selectedFilter)
    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400
    
    if selectedFilter == "All":
        filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]

    if selectedFilter == "Top 5":
        # find the top 5 countries by calling mostdomcountries here and save in topFiveCountries
        response = requests.get(
                "http://127.0.0.1:5000/api/most_dominating_countries",
                params={"yearRangeStart": yearRangeStart, "yearRangeEnd": yearRangeEnd},
        )
        
        dominating_countries = response.json()
        print(dominating_countries)
        topFiveCountries = [item['to_country'] for item in dominating_countries[:5]]

        filtered = contestants_df[
        (contestants_df['year'] >= yearRangeStart) &
        (contestants_df['year'] <= yearRangeEnd) &
        (contestants_df['to_country'].isin(topFiveCountries))     
        ]

    if selectedFilter == "Worst 5":
         # find the worst 5 countries by calling mostdomcountries here and save in worstFiveCountries

        response = requests.get(
            "http://127.0.0.1:5000/api/most_dominating_countries",
            params={"yearRangeStart": yearRangeStart, "yearRangeEnd": yearRangeEnd},
        )

        print(response)
        
        dominating_countries = response.json()
        worstFiveCountries = [item['to_country'] for item in dominating_countries[-5:]]

        filtered = contestants_df[
        (contestants_df['year'] >= yearRangeStart) &
        (contestants_df['year'] <= yearRangeEnd) &
        (contestants_df['to_country'].isin(worstFiveCountries))     
        ]


    # Combine all lyrics into a single string
    all_lyrics = " ".join(filtered['lyrics_token'].dropna())

    # Preprocess lyrics: remove non-alphanumeric characters and convert to lowercase
    processed_lyrics = re.sub(r'[^a-zA-Z\s]', '', all_lyrics).lower()

    # Split into words and count occurrences
    word_counts = Counter(processed_lyrics.split())

    # Get the 15 most common words
    common_words = word_counts.most_common(30)

    # Convert to JSON format
    word_cloud_data = [{"word": word, "count": count} for word, count in common_words]

    return jsonify(word_cloud_data)

# Endpoint: Countries in Favor (Heatmap Data)
@app.route('/api/countries_in_favor', methods=['GET'])
def countries_in_favor():
    # Retrieve year from query parameters
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeEnd:
        return jsonify({"error": "Year parameter is required"}), 400

    # Load country names and codes
    code_to_name = dict(zip(country_df["Code"], country_df["Name"]))

    # Filter votes by the selected year
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]
    # Aggregate votes into a matrix: points given by one country to another
    heatmap_data = (
        filtered_votes.groupby(['from_country_id', 'to_country_id'])['perc_of_max']
        .sum()
        .reset_index(name='vote_count')  # Summing the points exchanged
    )

    # Ensure all combinations are represented (even if some have zero points)
    all_countries = sorted(
        set(filtered_votes['from_country_id']) | set(filtered_votes['to_country_id'])
    )
    heatmap_matrix = pd.DataFrame(index=all_countries, columns=all_countries).fillna(0)
    heatmap_matrix = heatmap_matrix.astype(float)

    for _, row in heatmap_data.iterrows():
        heatmap_matrix.at[row['from_country_id'], row['to_country_id']] = float(row['vote_count'])

    # Replace codes with names for rows and columns
    heatmap_matrix.index = heatmap_matrix.index.map(code_to_name)
    heatmap_matrix.columns = heatmap_matrix.columns.map(code_to_name)
    all_countries_names = [code_to_name.get(code, f"Unknown ({code})") for code in all_countries]

    # Convert to JSON-friendly format
    heatmap_response = {
        "countries": all_countries_names,
        "matrix": heatmap_matrix.values.tolist(),
    }

    return jsonify(heatmap_response)


# Endpoint: Songs List
@app.route('/api/songs_list', methods=['GET'])
def songs_list():
    # Filter songs based on year or country
    year = request.args.get('year', default=None, type=int)
    country = request.args.get('country', default=None, type=str)

    filtered = contestants_df
    if year:
        filtered = filtered[filtered['year'] == year]
    if country:
        filtered = filtered[filtered['to_country'] == country]

    songs = filtered[['year', 'song', 'to_country', 'place_contest']].sort_values('year', ascending=False)
    return jsonify(songs.to_dict(orient='records'))

# Endpoint: Song Details
@app.route('/api/song_details', methods=['GET'])
def song_details():
    # Fetch details of a song by song name
    song_name = request.args.get('song', default=None, type=str)
    if not song_name:
        return jsonify({'error': 'Song name is required'}), 400

    song_details = contestants_df[contestants_df['song'] == song_name].to_dict(orient='records')
    return jsonify(song_details[0] if song_details else {'error': 'Song not found'})


@app.route('/api/voting_clusters', methods=['GET'])
def voting_clusters():
    # Get year range from the request
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    numberOfClusters = request.args.get('numberOfClusters', type=int)

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Filter the voting data based on the selected year range
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd) & (votes_df['round'] == 'final')]

    # Pivot table to create the voting matrix
    voting_matrix = filtered_votes.pivot_table(
        index='from_country_id',
        columns='to_country_id',
        values='perc_of_max',  # Replace with your relevant value column
        aggfunc='sum',
        fill_value=0
    )
    voting_matrix = voting_matrix.reindex(columns=all_columns, fill_value=0)

    # Standardize the voting matrix
    standardized_matrix = scaler.transform(voting_matrix)

    # Reduce dimensions using PCA
    voting_matrix_2d = pca.transform(standardized_matrix)
    explained_variance = pca.explained_variance_ratio_ * 100  # Convert to percentage

    # Apply K-Means clustering (you can adjust the number of clusters)
    kmeans = KMeans(n_clusters=numberOfClusters, init=initial_centroids[:numberOfClusters], n_init=1, random_state=42)
    clusters = kmeans.fit_predict(voting_matrix_2d)
    country_dict = dict(zip(country_df['Code'], country_df['Name']))
    region_dict = dict(zip(contestants_df['to_country_id'].str.lower(), contestants_df['region']))

    # Prepare data for visualization
    cluster_data = [
        {
            "country": country,
            "x": float(voting_matrix_2d[i, 0]),  # PCA Component 1
            "y": float(voting_matrix_2d[i, 1]),  # PCA Component 2
            "cluster": int(clusters[i]),  # Cluster ID
            "region": region_dict.get(country.lower(), "Non-European"), #Region for coloring
            "country_name": country_dict.get(country.lower(), country)
        }
        for i, country in enumerate(voting_matrix.index)
    ]

    return  jsonify({
        "clusters": cluster_data,
        "explained_variance": explained_variance.tolist()
    })

@app.route('/api/voting_clusters_fullname', methods=['GET'])
def voting_clusters_fullName():
    color_palette = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']  # Extend if needed

    # Get year range from the request
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    numberOfClusters = request.args.get('numberOfClusters', type=int)

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Filter the voting data based on the selected year range
    filtered_votes = votes_df[
        (votes_df['year'] >= yearRangeStart) &
        (votes_df['year'] <= yearRangeEnd) &
        (votes_df['round'] == 'final')
    ]

    # Pivot table to create the voting matrix
    voting_matrix = filtered_votes.pivot_table(
        index='from_country_id',
        columns='to_country_id',
        values='perc_of_max',  # Replace with your relevant value column
        aggfunc='sum',
        fill_value=0
    )

    # Standardize the voting matrix
    scaler = StandardScaler()
    standardized_matrix = scaler.fit_transform(voting_matrix)

    # Reduce dimensions using PCA
    pca = PCA(n_components=2)
    voting_matrix_2d = pca.fit_transform(standardized_matrix)
    explained_variance = pca.explained_variance_ratio_ * 100  # Convert to percentage

    # Apply K-Means clustering (you can adjust the number of clusters)
    kmeans = KMeans(n_clusters=numberOfClusters, random_state=42)
    clusters = kmeans.fit_predict(voting_matrix_2d)

    # Use the existing `country_df` and its dictionary mapping
    country_dict = dict(zip(country_df['Code'], country_df['Name']))

    # Assign colors to clusters
    cluster_colors = {cluster: color_palette[cluster % len(color_palette)] for cluster in range(numberOfClusters)}

    # Prepare data for visualization
    cluster_data = [
        {
            "country": country_dict.get(country.lower(), country),  # Convert abbreviation to full name
            "x": float(voting_matrix_2d[i, 0]),  # PCA Component 1
            "y": float(voting_matrix_2d[i, 1]),  # PCA Component 2
            "cluster": int(clusters[i]),  # Cluster ID
            "color": cluster_colors[clusters[i]]  # Cluster color
        }
        for i, country in enumerate(voting_matrix.index)
    ]

    # Compute regional composition
    region_info = compute_cluster_regions(cluster_data, countries_regions_df)

    return jsonify({
        "clusters": cluster_data,
        "explained_variance": explained_variance.tolist(),
        "region_info": region_info
    })



def compute_cluster_regions(cluster_data, region_df):
    # Convert cluster_data to DataFrame
    region_df['country'] = region_df['country'].str.strip().str.lower()

    cluster_df = pd.DataFrame(cluster_data)

    # Map full country names to country codes
    country_name_to_code = dict(zip(country_df['Name'], country_df['Code']))
    cluster_df['country_code'] = cluster_df['country'].map(country_name_to_code)


    # Debug: Check for unmapped countries
    print("Unmapped Countries:", cluster_df[cluster_df['country_code'].isnull()])

    # Merge cluster data with region information
    cluster_df = cluster_df.merge(
        region_df[['country', 'region']],
        left_on='country_code',
        right_on='country',
        how='left'
    )

    # Debug: Check for missing regions after merge
    print("Merged Data Missing Regions:", cluster_df[cluster_df['region'].isnull()])

    # Group by cluster and calculate the percentage of each region
    region_summary = cluster_df.groupby('cluster')['region'].value_counts(normalize=True) * 100
    region_summary = region_summary.rename("percentage").reset_index()

    # Format as dictionary for easier frontend use
    region_info = {}
    for cluster in region_summary['cluster'].unique():
        cluster_regions = region_summary[region_summary['cluster'] == cluster]
        # Convert cluster ID to int explicitly
        region_info[int(cluster)] = cluster_regions[['region', 'percentage']].to_dict('records')

    return region_info



@app.route('/api/top5barchart', methods=['GET'])
def top5_ranking_data():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Fetch yearly rankings
    response = requests.get(
        "http://127.0.0.1:5000/api/yearly_rankings",
        params={"yearRangeStart": yearRangeStart, "yearRangeEnd": yearRangeEnd},
    )
    yearly_rankings = response.json()

    # Initialize region rankings
    region_rankings = {}

    # Iterate through yearly rankings
    for country, years in yearly_rankings.items():
        # Filter years to include only those in the selected range
        filtered_years = {year: value for year, value in years.items() if yearRangeStart <= int(year) <= yearRangeEnd}
        
        # Calculate the total number of top 5 rankings and number of participations
        total_top5 = sum(1 for value in filtered_years.values() if 1 <= value <= 5)
        participations = len(filtered_years)  # Count of years with an entry

        # Skip if no participations to avoid division by zero
        if participations == 0:
            continue

        # Calculate the average number of top 5 rankings for the country
        average_top5 = total_top5 / participations

        # Find the region for the country from the DataFrame
        region = countries_regions_df.loc[
            countries_regions_df['country_name'] == country, 'region'
        ].values

        if len(region) == 0:
            region = "Unknown"
        else:
            region = region[0]

        # Aggregate by region
        if region not in region_rankings:
            region_rankings[region] = 0
        region_rankings[region] += average_top5

    print(f"Top 5 rankings by region (average per competition): {region_rankings}")
    return jsonify(region_rankings)

@app.route('/api/top5barchartnormalized', methods=['GET'])
def top5_ranking_data_normalized():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Fetch yearly rankings
    response = requests.get(
        "http://127.0.0.1:5000/api/yearly_rankings",
        params={"yearRangeStart": yearRangeStart, "yearRangeEnd": yearRangeEnd},
    )
    yearly_rankings = response.json()

    # Initialize region rankings and country counts
    region_rankings = {}
    region_country_counts = countries_regions_df.groupby('region')['country_name'].count().to_dict()

    # Iterate through yearly rankings
    for country, years in yearly_rankings.items():
        # Filter years to include only those in the selected range
        filtered_years = {year: value for year, value in years.items() if yearRangeStart <= int(year) <= yearRangeEnd}
        
        # Calculate the total number of top 5 rankings and number of participations
        total_top5 = sum(1 for value in filtered_years.values() if 1 <= value <= 5)
        participations = len(filtered_years)  # Count of years with an entry

        # Skip if no participations to avoid division by zero
        if participations == 0:
            continue

        # Calculate the average number of top 5 rankings for the country
        average_top5 = total_top5 / participations

        # Find the region for the country from the DataFrame
        region = countries_regions_df.loc[
            countries_regions_df['country_name'] == country, 'region'
        ].values

        if len(region) == 0:
            region = "Unknown"
        else:
            region = region[0]

        # Aggregate by region
        if region not in region_rankings:
            region_rankings[region] = 0
        region_rankings[region] += average_top5

    # Normalize region rankings by the number of countries in each region
    normalized_region_rankings = {
        region: region_rankings[region] / region_country_counts.get(region, 1)
        for region in region_rankings
    }

    print(f"Top 5 rankings by region (normalized per country): {normalized_region_rankings}")
    return jsonify(normalized_region_rankings)






# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
