from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load datasets
contestants_df = pd.read_csv('../dataset/contestants_cleaned.csv')
votes_df = pd.read_csv('../dataset/votes_cleaned.csv')

# Endpoint: Most Dominating Countries
@app.route('/api/most_dominating_countries', methods=['GET'])
def most_dominating_countries():
    # Get year from query params
    year = request.args.get('year', default=None, type=int)

    # Filter by year if provided
    filtered = contestants_df
    if year:
        filtered = contestants_df[contestants_df['year'] == year]

    # Aggregate data to sum points_final by country
    dominating_countries = (
        filtered.groupby('to_country')['points_final']
        .sum()
        .reset_index()
        .rename(columns={'points_final': 'total_points'})
        .sort_values('total_points', ascending=False)
    )

    # Return the result as JSON
    return jsonify(dominating_countries.to_dict(orient='records'))

# Endpoint: Get all available years from dataset
@app.route('/api/available_years', methods=['GET'])
def get_available_years():
    years = contestants_df['year'].unique().tolist()
    years.sort(reverse=True)  # Optional: Sort years in descending order
    return jsonify(years)



# Endpoint: Yearly Rankings
@app.route('/api/yearly_rankings', methods=['GET'])
def yearly_rankings():
    # Filter by year if provided
    year = request.args.get('year', default=None, type=int)
    if year:
        filtered = contestants_df[contestants_df['year'] == year]
    else:
        filtered = contestants_df

    yearly_rankings = (
        filtered.groupby(['year', 'to_country'])
        .size()
        .reset_index(name='count')
        .pivot(index='year', columns='to_country', values='count')
        .fillna(0)
    )
    return jsonify(yearly_rankings.to_dict())

# Endpoint: Word Cloud Data
@app.route('/api/word_cloud', methods=['GET'])
def word_cloud():
    # Analyze words in song lyrics or descriptions
    lyrics = contestants_df['lyric'].dropna().str.cat(sep=' ').lower()
    words = pd.Series(lyrics.split()).value_counts().head(50)
    return jsonify(words.to_dict())

# Endpoint: Countries in Favor (Heatmap Data)
@app.route('/api/countries_in_favor', methods=['GET'])
def countries_in_favor():
    # Aggregate votes from one country to another
    heatmap_data = (
        votes_df.groupby(['from_country', 'to_country'])
        .size()
        .reset_index(name='vote_count')
    )
    return jsonify(heatmap_data.to_dict(orient='records'))

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
