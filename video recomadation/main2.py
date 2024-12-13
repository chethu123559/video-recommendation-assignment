import pandas as pd
import json

# Load data from JSON files
viewed_posts_df = pd.read_json('viewed_posts.json')
liked_posts_df = pd.read_json('liked_posts.json')
inspired_posts_df = pd.read_json('inspired_posts.json')
rated_posts_df = pd.read_json('rated_posts.json')
all_posts_df = pd.read_json('all_posts.json')
all_users_df = pd.read_json('all_users.json')

# Step 1: Clean and Combine Data
# Remove posts with missing 'id' or 'user_id'
viewed_posts_df.dropna(subset=['id', 'user_id'], inplace=True)
liked_posts_df.dropna(subset=['id', 'user_id'], inplace=True)
inspired_posts_df.dropna(subset=['id', 'user_id'], inplace=True)
rated_posts_df.dropna(subset=['id', 'user_id'], inplace=True)

# Combine posts data into a single dataframe
combined_posts_df = pd.concat([viewed_posts_df, liked_posts_df, inspired_posts_df, rated_posts_df], ignore_index=True)

# Step 2: Normalize Fields
# Check if 'created_at' exists before performing normalization
if 'created_at' in combined_posts_df.columns:
    combined_posts_df['created_at'] = pd.to_datetime(combined_posts_df['created_at'], errors='coerce')
else:
    print("The 'created_at' column is missing. Skipping date normalization.")

# Step 3: Add Derived Features
# Calculate popularity (use 'rating_percent' for now as a proxy for popularity)
if 'rating_percent' in combined_posts_df.columns:
    combined_posts_df['popularity'] = combined_posts_df['rating_percent']
else:
    print("The 'rating_percent' column is missing. Skipping popularity calculation.")

# Calculate engagement (use 'viewed_at' and 'liked_at' to estimate engagement)
if 'viewed_at' in combined_posts_df.columns or 'liked_at' in combined_posts_df.columns:
    combined_posts_df['engagement'] = combined_posts_df['viewed_at'].notnull().astype(int) + combined_posts_df['liked_at'].notnull().astype(int)
else:
    print("The required engagement columns ('viewed_at', 'liked_at') are missing. Skipping engagement calculation.")

# Step 4: Create user interactions
# Merge user interactions with the all_users_df DataFrame
if 'user_id' in combined_posts_df.columns and 'post_id' in combined_posts_df.columns:
    user_interactions_df = pd.merge(combined_posts_df[['user_id', 'post_id', 'popularity', 'engagement']], all_users_df[['id', 'username']], left_on='user_id', right_on='id', how='left')
else:
    print("The required columns ('user_id', 'post_id') are missing. Skipping user interactions.")

# Step 5: Create Global Variables for further use
user_data = all_users_df[['id', 'username', 'email']]  # Assuming 'email' exists as an identifier

# Create video_metadata without 'created_at' column if missing
if 'created_at' in combined_posts_df.columns:
    video_metadata = combined_posts_df[['post_id', 'popularity', 'engagement', 'created_at']]  # Post metadata
else:
    video_metadata = combined_posts_df[['post_id', 'popularity', 'engagement']]  # Skip 'created_at' if missing

user_interactions = user_interactions_df  # User interactions with posts

# Debug: Check the shapes of the processed data
print(f"User data shape: {user_data.shape}")
print(f"Video metadata shape: {video_metadata.shape}")
print(f"User interactions shape: {user_interactions.shape}")

# Save the processed data for future use
user_data.to_json('user_data_cleaned.json', orient='records', lines=True)
video_metadata.to_json('video_metadata_cleaned.json', orient='records', lines=True)
user_interactions.to_json('user_interactions_cleaned.json', orient='records', lines=True)

print("Data preprocessing completed and saved.")
