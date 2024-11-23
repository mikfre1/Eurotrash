from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from collections import Counter
import re

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load datasets
contestants_df = pd.read_csv('../dataset/contestants_cleaned.csv')
votes_df = pd.read_csv('../dataset/votes_cleaned.csv')
country_df = pd.read_csv('../dataset/country_mapping_iso.csv')
country_df['Code'] = country_df['Code'].str.lower()



# Endpoint: Most Dominating Countries
#  --> adjust s.t:
# - for each year it adds the points
@app.route('/api/most_dominating_countries', methods=['GET'])
def most_dominating_countries():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400

    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd)]

    dominating_countries = (
        filtered.groupby('to_country')['per_of_pot_max']
        .sum()
        .reset_index()
        .rename(columns={'per_of_pot_max': 'total_points'})
        .sort_values('total_points', ascending=False)
    )

    return jsonify(dominating_countries.to_dict(orient='records'))

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


    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd)] 

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

    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd)]

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
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd)]

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

    for _, row in heatmap_data.iterrows():
        heatmap_matrix.at[row['from_country_id'], row['to_country_id']] = row['vote_count']

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

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Filter the voting data based on the selected year range
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd)]

    # Pivot table to create the voting matrix
    voting_matrix = filtered_votes.pivot_table(
        index='from_country_id',
        columns='to_country_id',
        values='perc_of_max',  # Replace with your relevant value column
        aggfunc='sum',
        fill_value=0
    )

    # Reduce dimensions using PCA
    pca = PCA(n_components=2)
    voting_matrix_2d = pca.fit_transform(voting_matrix)

    # Apply K-Means clustering (you can adjust the number of clusters)
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(voting_matrix)

    # Prepare data for visualization
    cluster_data = [
        {
            "country": country,
            "x": float(voting_matrix_2d[i, 0]),  # PCA Component 1
            "y": float(voting_matrix_2d[i, 1]),  # PCA Component 2
            "cluster": int(clusters[i])  # Cluster ID
        }
        for i, country in enumerate(voting_matrix.index)
    ]

    return jsonify(cluster_data)

@app.route('/api/voting_clusters_fullname', methods=['GET'])
def voting_clusters_fullName():
    # Get year range from the request
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    numbersOfClusters = request.args.get('numbersOfClusters', type=int)

    if not yearRangeStart or not yearRangeEnd:
        return jsonify({"error": "Year range parameters are required"}), 400

    # Filter the voting data based on the selected year range
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd)]

    # Pivot table to create the voting matrix
    voting_matrix = filtered_votes.pivot_table(
        index='from_country_id',
        columns='to_country_id',
        values='perc_of_max',  # Replace with your relevant value column
        aggfunc='sum',
        fill_value=0
    )

    # Reduce dimensions using PCA
    pca = PCA(n_components=2)
    voting_matrix_2d = pca.fit_transform(voting_matrix)

    # Apply K-Means clustering (you can adjust the number of clusters)
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(voting_matrix)

    # Use the existing `country_df` and its dictionary mapping
    country_dict = dict(zip(country_df['Code'], country_df['Name']))

    # Prepare data for visualization
    cluster_data = [
        {
            "country": country_dict.get(country.lower(), country),  # Convert abbreviation to full name
            "x": float(voting_matrix_2d[i, 0]),  # PCA Component 1
            "y": float(voting_matrix_2d[i, 1]),  # PCA Component 2
            "cluster": int(clusters[i])  # Cluster ID
        }
        for i, country in enumerate(voting_matrix.index)
    ]

    return jsonify(cluster_data)





# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
