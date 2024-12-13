import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

# Load preprocessed data
user_data = pd.read_json('user_data_cleaned.json', lines=True)
video_metadata = pd.read_json('video_metadata_cleaned.json', lines=True)
user_interactions = pd.read_json('user_interactions_cleaned.json', lines=True)

# Ensure 'user_id' column exists in user_data
if 'user_id' not in user_data.columns:
    user_data.rename(columns={'id': 'user_id'}, inplace=True)

# Cold-Start Recommendation Function
def cold_start_recommendation(video_metadata, mood=None, category_id=None, top_n=10):
    if mood:
        # Filter videos by mood
        mood_videos = video_metadata[video_metadata['mood'] == mood]
    else:
        mood_videos = video_metadata

    if category_id:
        # Filter by category
        category_videos = mood_videos[mood_videos['category_id'] == category_id]
    else:
        category_videos = mood_videos

    # Return top N popular videos
    return category_videos.sort_values('popularity', ascending=False).head(top_n)['post_id'].tolist()

# Content-Based Recommendation Function
def content_based_recommendation(user_interactions, video_metadata, top_n):
    video_features = video_metadata[['popularity', 'engagement']].fillna(0)
    similarity_matrix = cosine_similarity(video_features)

    recommendations = {}
    for user_id in user_interactions['user_id'].unique():
        user_videos = user_interactions[user_interactions['user_id'] == user_id]['post_id']
        user_similarities = similarity_matrix[user_videos.index].mean(axis=0)

        top_indices = np.argsort(user_similarities)[::-1][:top_n]
        recommended_videos = video_metadata.iloc[top_indices]['post_id'].tolist()
        recommendations[user_id] = recommended_videos

    return recommendations

# Collaborative Filtering Recommendation Function
def collaborative_filtering(user_interactions, video_metadata, top_n):
    interaction_matrix = user_interactions.pivot_table(index='user_id', columns='post_id', values='engagement', fill_value=0)
    similarity_matrix = cosine_similarity(interaction_matrix)
    user_similarity_df = pd.DataFrame(similarity_matrix, index=interaction_matrix.index, columns=interaction_matrix.index)

    recommendations = {}
    for user_id in interaction_matrix.index:
        similar_users = user_similarity_df[user_id].sort_values(ascending=False).iloc[1:]
        top_users = similar_users.index[:top_n]

        recommended_videos = (
            interaction_matrix.loc[top_users].sum(axis=0).sort_values(ascending=False).head(top_n).index.tolist()
        )
        recommendations[user_id] = recommended_videos

    return recommendations

# Hybrid Recommendation Function
def hybrid_recommendation(user_interactions, video_metadata, alpha, top_n):
    content_based_rec = content_based_recommendation(user_interactions, video_metadata, top_n)
    collaborative_rec = collaborative_filtering(user_interactions, video_metadata, top_n)

    recommendations = {}
    for user_id in user_interactions['user_id'].unique():
        cb_rec = content_based_rec.get(user_id, [])
        cf_rec = collaborative_rec.get(user_id, [])

        combined_rec = list(
            set(cb_rec[:int(alpha * top_n)]) | set(cf_rec[:int((1 - alpha) * top_n)])
        )
        recommendations[user_id] = combined_rec

    return recommendations

# Generate Recommendations
def generate_recommendations(user_interactions, video_metadata, user_data, top_n=5, alpha=0.5):
    # Handle cold-start users
    cold_start_users = user_data[~user_data['user_id'].isin(user_interactions['user_id'])]
    recommendations = {}

    for user_id in cold_start_users['user_id']:
        recommendations[user_id] = cold_start_recommendation(video_metadata, top_n=top_n)

    # Handle existing users with hybrid recommendation
    existing_user_recommendations = hybrid_recommendation(user_interactions, video_metadata, alpha, top_n)
    recommendations.update(existing_user_recommendations)

    return recommendations

# Generate recommendations
recommendations = generate_recommendations(user_interactions, video_metadata, user_data, top_n=5, alpha=0.5)

# Convert recommendation keys to standard int before saving
recommendations = {int(k): v for k, v in recommendations.items()}

# Save recommendations to JSON file
with open('recommendations.json', 'w') as f:
    json.dump(recommendations, f)

print("Recommendations saved to 'recommendations.json'")
