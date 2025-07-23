import json

def analyze_posts(file_path):
    """Reads a JSON file of LinkedIn posts, finds the top 10 most liked,
    and prints the author and like count.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
        return None
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None

    analyzed_posts = []
    for post in posts_data:
        # Safely get author name
        author_name = post.get('author', {}).get('name', 'Unknown Author')

        # Safely get likes count, default to 0 if engagement is None or likes key is missing
        engagement = post.get('engagement')
        if engagement:
            likes = engagement.get('likes', 0)
        else:
            likes = 0

        analyzed_posts.append({
            'author': author_name,
            'likes': likes
        })

    # Sort the posts by likes in descending order
    sorted_posts = sorted(analyzed_posts, key=lambda x: x['likes'], reverse=True)

    # Get the top 20
    top_20_posts = sorted_posts[:20]

    print("Top 20 Most-Liked Posts:")
    print("-------------------------")
    if not top_20_posts:
        print("No posts with engagement data found.")
    else:
        for i, post in enumerate(top_20_posts, 1):
            print(f"{i}. Author: {post['author']}, Likes: {post['likes']}")
    
    return posts_data

def extract_top_content(posts_data, output_file_path, top_n=20):
    """Extracts the content from the top N most-liked posts
    and saves it to a new JSON file.
    """
    if not posts_data:
        return

    # Create a list of posts with their like counts
    posts_with_likes = []
    for post in posts_data:
        engagement = post.get('engagement')
        likes = engagement.get('likes', 0) if engagement else 0
        posts_with_likes.append({'content': post.get('content'), 'likes': likes})

    # Sort by likes and get the top N
    sorted_posts = sorted(posts_with_likes, key=lambda x: x['likes'], reverse=True)
    top_posts = sorted_posts[:top_n]

    # Extract just the content from the top posts
    top_content = [post['content'] for post in top_posts if post['content']]

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(top_content, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully extracted {len(top_content)} posts to {output_file_path}")
    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}")


if __name__ == "__main__":
    # Define file paths
    json_file_path = 'c:\\Users\\ic\\OneDrive\\Desktop\\Other Things\\Content - My Articles\\Apify\\dataset_linkedin-post-search_2025-07-14_19-45-22-492.json'
    output_file_path = 'c:\\Users\\ic\\OneDrive\\Desktop\\Other Things\\Content - My Articles\\Apify\\top_content.json'

    # --- Task 1: Analyze and print top 20 posts ---
    posts_data = analyze_posts(json_file_path)

    # --- Task 2: Extract content of top 20 posts ---
    if posts_data:
        extract_top_content(posts_data, output_file_path, top_n=20)
