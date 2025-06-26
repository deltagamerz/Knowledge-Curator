# main.py (Version 3 with Improved Email Formatting)
import sys
from datetime import datetime
from worker.agent_tools import (
    load_config,
    get_new_videos_from_rss,
    get_transcript,
    get_notes_from_transcript,
    send_email,
    get_video_id
)

def build_html_email_body(notes_data):
    """Builds a styled HTML email from the collected notes data."""
    
    # --- This is our new CSS styling ---
    # It defines fonts, sizes, colors, and spacing.
    styles = """
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }
        h1 { font-size: 24px; color: #2c3e50; font-weight: 600; }
        h2 { font-size: 20px; color: #34495e; font-weight: 600; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }
        h4 { font-size: 16px; color: #34495e; font-weight: 600; margin-bottom: 5px; }
        p { font-size: 16px; margin-bottom: 10px; }
        div.notes-block { background-color: #fdfdfd; border-left: 3px solid #3498db; padding: 10px 15px; margin-top: 10px; font-family: 'Georgia', serif; }
        a { color: #3498db; text-decoration: none; }
        hr { border: 0; border-top: 1px solid #ecf0f1; }
    </style>
    """
    
    header = "<h1>🧠 Knowledge Curator Digest</h1>"
    email_content = ""

    for item in notes_data:
        # The .replace() calls are for formatting the AI's markdown-like output into proper HTML.
        formatted_notes = item['notes'].replace('###', '<h4>').replace('**', '<b>').replace('* ', '• ').replace('\n', '<br>')
        
        email_content += f"""
        <hr>
        <h2>{item['title']}</h2>
        <p><b>🔗 Link:</b> <a href="{item['link']}">{item['link']}</a></p>
        <div class="notes-block">
            {formatted_notes}
        </div>
        """
        
    return f"<html><head>{styles}</head><body>{header}{email_content}</body></html>"


def process_single_video(video_url, config):
    """Processes a single YouTube video URL on-demand."""
    print(f"--- Running in On-Demand Mode for URL: {video_url} ---")
    
    try:
        video_id = get_video_id(video_url)
    except ValueError as e:
        print(e)
        return

    # --- UPDATED LOGIC HERE ---
    # Now get_transcript returns two values
    transcript, video_title = get_transcript(video_id)
    
    # If the title wasn't found, use a fallback.
    if not video_title:
        video_title = f"On-Demand Analysis for video ID: {video_id}"

    if transcript:
        print("  -> Transcript found. Generating notes...")
        notes = get_notes_from_transcript(transcript, video_title)
        
        if notes:
            # We create a list containing a single dictionary, so we can reuse our email builder function.
            notes_data = [{
                "title": video_title,
                "link": video_url,
                "notes": notes
            }]
            email_body = build_html_email_body(notes_data)
            
            print("\nSending email with notes...")
            send_email(
                subject=f"Notes for: {video_title}", # Use the real title here!
                body=email_body,
                recipient_email=config['recipient_email']
            )
            print("  -> Email sent successfully!")
        else:
            print("  -> Could not generate notes from the transcript.")
    else:
        print("  -> FAILED: Could not retrieve a transcript for this video. It may be disabled.")


def run_daily_check(config):
    """Runs the daily automated check for new videos from channels."""
    print(f"--- Running in Daily Automated Mode ---")
    keywords = [k.lower() for k in config['keywords']]
    videos_to_summarize = []

    print("Scouting for new content from your channels...")
    for channel in config['channels']:
        print(f"  -> Checking channel: {channel['name']}")
        new_videos = get_new_videos_from_rss(channel['id'])
        
        if not new_videos:
            print(f"     No new videos found.")
            continue

        for video in new_videos:
            video_title_lower = video['title'].lower()
            if any(keyword in video_title_lower for keyword in keywords):
                print(f"     [MATCH FOUND] Video '{video['title']}' is relevant. Adding to queue.")
                videos_to_summarize.append(video)

    if not videos_to_summarize:
        print("No new relevant videos found today. Agent is going back to sleep.")
        return

    print(f"\nFound {len(videos_to_summarize)} relevant videos. Generating notes...")
    
    notes_data_for_email = []
    
    for video in videos_to_summarize:
        print(f"  -> Processing: '{video['title']}'")
        # --- UPDATED LOGIC HERE ---
        # get_transcript now returns two values, but we already have the title from RSS.
        # So we can ignore the second return value with an underscore _.
        transcript, _ = get_transcript(video['id'])
        
        if transcript:
            notes = get_notes_from_transcript(transcript, video['title'])
            if notes:
                # Add the successful notes to our list for the final email.
                notes_data_for_email.append({
                    "title": video['title'],
                    "link": video['link'],
                    "notes": notes
                })
        else:
            # If a video fails, we can still add a placeholder to the email if we want.
            notes_data_for_email.append({
                "title": video['title'],
                "link": video['link'],
                "notes": "<i>Could not process this video: Transcript not available.</i>"
            })
    
    if notes_data_for_email:
        print("\nBuilding and sending email digest...")
        email_body = build_html_email_body(notes_data_for_email)
        today_date = datetime.now().strftime('%Y-%m-%d')
        send_email(
            subject=f"🧠 Knowledge Curator Digest: {today_date}",
            body=email_body,
            recipient_email=config['recipient_email']
        )
    
    print("Email process complete.")


def main():
    """The main entry point that decides which mode to run."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Knowledge Curator agent is waking up...")
    config = load_config()

    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        process_single_video(video_url, config)
    else:
        run_daily_check(config)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Agent's work is done.")

if __name__ == "__main__":
    # We are calling the function that runs the daily check directly.
    # This makes our intent clear when we set up the server command.
    from worker.agent_tools import load_config
    
    config = load_config()
    run_daily_check(config)