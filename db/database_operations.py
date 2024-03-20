import sqlite3

def get_all_mapped_channels():
    # Connect to the SQLite database
    conn = sqlite3.connect('youBOT.db')
    cursor = conn.cursor()

    # Execute SQL query to retrieve all mapped channels
    #query = 'SELECT * FROM map_channels'
    query = '''
        SELECT 
            channels.name AS channels_name,
            my_channels.name AS my_channels_name
        FROM map_channels
        LEFT JOIN my_channels ON map_channels.my_channels_id = my_channels.id
        LEFT JOIN channels ON map_channels.channels_id = channels.id'''
    cursor.execute(query)

    # Fetch all rows
    all_mapped_channels = cursor.fetchall()

    cursor.close()
    # Close the connection
    conn.close()

    return all_mapped_channels

def get_channel(channel_name):
    conn = sqlite3.connect('youBOT.db')
    cursor = conn.cursor()

    query = '''
        SELECT language AS language, video_description AS video_description, shorts AS shorts
        FROM channels
        WHERE channels.name = ?;
    '''

    cursor.execute(query, (channel_name,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return result

def get_my_channels(my_channel_name):
    conn = sqlite3.connect('youBOT.db')
    cursor = conn.cursor()

    query = '''
        SELECT 
            my_channels.id, my_channels.language, my_channels.action, my_channels.translate_tags, google_accounts.account_email, 
            google_accounts.account_password, google_accounts.country, google_accounts.profile
        FROM my_channels
        JOIN google_accounts ON my_channels.google_account_id = google_accounts.id
        WHERE my_channels.name = ?
    '''

    cursor.execute(query, (my_channel_name,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def get_video_by_url(url, my_channel_id):
    conn = sqlite3.connect('youBOT.db')
    cursor = conn.cursor()

    query = '''
        SELECT EXISTS (
            SELECT 1
            FROM videos
            WHERE video_url = ? AND my_channels_id = ?
        ) AS video_exists;
    '''

    cursor.execute(query, (url, my_channel_id))

    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return bool(result)

def videos_uploaded_current_day(my_channel_id):
    conn = sqlite3.connect('youBOT.db')
    cursor = conn.cursor()

    query = """
        SELECT COUNT(*) AS total_videos_today
        FROM videos
        WHERE my_channels_id = ? AND DATE(upload_date) = DATE('now');
    """

    cursor.execute(query, (my_channel_id,))
    results = cursor.fetchone()[0]
    print("videos_uploaded_current_day result: ", results)
    cursor.close()
    conn.close()
    
    return results

def insert_video(video_id, video_title, video_url, my_channels_id, my_video_url):
    try:
        conn = sqlite3.connect('youBOT.db')
        cursor = conn.cursor()

        query = '''
            INSERT INTO videos (video_id, video_title, video_url, my_channels_id, my_video_url)
            VALUES (?, ?, ?, ?, ?);
        '''

        cursor.execute(query, (video_id, video_title, video_url, my_channels_id, my_video_url))

        conn.commit()

        cursor.close()
        conn.close()

    except sqlite3.Error as e:
        # Handle SQLite errors
        print(f"SQLite error: {e}")

    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")
    