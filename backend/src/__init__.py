from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from collections import Counter
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load datasets
contestants_df = pd.read_csv('../dataset/contestants_cleaned.csv')
votes_df = pd.read_csv('../dataset/votes_cleaned.csv')


# Endpoint: Most Dominating Countries
#  --> adjust s.t:
# - for each year it adds the points
@app.route('/api/most_dominating_countries', methods=['GET'])
def most_dominating_countries():
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)
    print(yearRangeStart)
    print(yearRangeEnd)
    if not yearRangeStart:
        return jsonify({"error": "Year parameter is required"}), 400

    filtered = contestants_df[(contestants_df['year'] >= yearRangeStart) & (contestants_df['year'] <= yearRangeEnd)]

    dominating_countries = (
        filtered.groupby('to_country')['points_final']
        .sum()
        .reset_index()
        .rename(columns={'points_final': 'total_points'})
        .sort_values('total_points', ascending=False)
    )
    print(f"Aggregated data:\n{dominating_countries}")  # Debugging log

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
    common_words = word_counts.most_common(15)

    # Convert to JSON format
    word_cloud_data = [{"word": word, "count": count} for word, count in common_words]
    print(word_cloud_data)

    return jsonify(word_cloud_data)

# Endpoint: Countries in Favor (Heatmap Data)
@app.route('/api/countries_in_favor', methods=['GET'])
def countries_in_favor():
    # Retrieve year from query parameters
    yearRangeStart = request.args.get('yearRangeStart', type=int)
    yearRangeEnd = request.args.get('yearRangeEnd', type=int)

    if not yearRangeEnd:
        return jsonify({"error": "Year parameter is required"}), 400

    # Filter votes by the selected year
    filtered_votes = votes_df[(votes_df['year'] >= yearRangeStart) & (votes_df['year'] <= yearRangeEnd)]

    # Aggregate votes into a matrix: points given by one country to another
    heatmap_data = (
        filtered_votes.groupby(['from_country_id', 'to_country_id'])['total_points']
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

    # Convert to JSON-friendly format
    heatmap_response = {
        "countries": all_countries,
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

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
