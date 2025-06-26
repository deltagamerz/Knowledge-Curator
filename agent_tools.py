# agent_tools.py
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
from datetime import datetime, timedelta
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- CONFIGURATION LOADER ---
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_video_id(youtube_url):
    if "watch?v=" in youtube_url:
        return youtube_url.split('v=')[-1].split('&')[0]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split('/')[-1].split('?')[0]
    raise ValueError("Invalid YouTube URL")

# --- YOUTUBE TOOLS ---
def get_new_videos_from_rss(channel_id):
    """Fetches new videos from a YouTube channel's RSS feed published in the last 24 hours."""
    # Every YouTube channel has a standard RSS feed URL
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    new_videos = []
    # Define our time window: the last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    
    # Go through each video entry in the RSS feed
    for entry in feed.entries:
        # The 'published_parsed' field is a structured time object
        published_time = datetime(*entry.published_parsed[:6])
        # If the video was published after our 'yesterday' timestamp, it's new
        if published_time > yesterday:
            new_videos.append({
                "title": entry.title,
                "link": entry.link,
                "id": entry.yt_videoid
            })
    return new_videos

def get_transcript(video_id):
    """Fetches the transcript and title for a given YouTube video ID."""
    try:
        # This library can fetch more than just the transcript!
        # We fetch the transcript object itself.
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # We can then access the video's metadata through the transcript object's video_id.
        # This is a bit of a library-specific trick.
        # We create a list of video IDs to pass to the list_transcripts method.
        video_metadata = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # The title is found within the metadata object.
        video_title = ""
        # We loop through the available transcripts to find the metadata, which includes the title.
        for entry in video_metadata:
            # The 'video_title' attribute exists on the transcript object.
             if hasattr(entry, 'video_title'):
                 video_title = entry.video_title
                 break

        transcript_text = " ".join([d['text'] for d in transcript])
        
        # Return both the text and the title!
        return transcript_text, video_title

    except Exception as e:
        print(f"  -> Could not fetch transcript for video ID {video_id}: {e}")
        # Return None for both if anything fails
        return None, None


# --- AI TOOLS ---
def get_notes_from_transcript(transcript, video_title):
    """Uses Gemini Pro to generate detailed notes from a transcript."""
    # This is our sophisticated prompt. It tells the AI its role, the format, and the task.
    prompt = f"""
    You are an expert academic assistant. Your task is to create detailed, high-quality notes from the transcript of an educational YouTube video titled "{video_title}".

    The notes should be structured, easy to read, and capture the core concepts, key arguments, and any important examples mentioned. Do not just summarize; explain the concepts as if you were creating a study guide.

    Here is the format you must follow:
    
    ### Core Concept
    *   **[Concept 1 Name]:** A clear and concise explanation of the first main concept.
    *   **[Concept 2 Name]:** A clear and concise explanation of the second main concept.
    
    ### Key Takeaways
    *   **[Takeaway 1]:** A bullet point summarizing a critical insight or conclusion.
    *   **[Takeaway 2]:** Another bullet point with a key piece of information.
    
    ### Notable Examples or Analogies
    *   **[Example 1]:** Describe any important examples or analogies the speaker used to clarify a point.

    Now, based on this structure, analyze the following transcript and generate the notes:

    TRANSCRIPT:
    "{transcript}"
    """
    try:
        # Send the prompt to the Gemini model and return the generated text
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  -> Gemini API error while generating notes: {e}")
        return None

# --- NOTIFICATION TOOL ---
def send_email(subject, body, recipient_email):
    """Sends an email using the credentials stored in the .env file."""
    # Get the sender's credentials from the environment variables
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")

    if not sender_email or not sender_password:
        print("  -> ERROR: Sender email or password not set in .env file. Cannot send email.")
        return

    # Create the email message object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    # Attach the main body of the email
    message.attach(MIMEText(body, "html")) # Using 'html' to allow for clickable links

    try:
        # Connect to Gmail's SMTP server over a secure connection
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # Login using the App Password
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
        # Close the connection
        server.quit()
        print(f"  -> Successfully sent digest to {recipient_email}")
    except Exception as e:
        print(f"  -> Failed to send email: {e}")