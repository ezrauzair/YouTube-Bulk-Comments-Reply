import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.shortcuts import render
from django.contrib import messages


def home(request):
    return render(request,'home.html')





# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def process_form(request):
    if request.method == "POST":
        link = request.POST.get('link')
        reply_text = request.POST.get('text')

        # Validate the link
        expression = r'(?:youtu\.be/|youtube\.com/watch\?v=)([A-Za-z0-9_-]+)'
        match = re.search(expression, link)

        if not match:
            messages.error(request, 'Invalid YouTube link.')
            return render(request, 'home.html')

        video_id = match.group(1)

        # Authenticate and create a YouTube API client
        credentials = None
        # Load credentials from the JSON file
        if os.path.exists("C:\\Users\\PMYLS\\Desktop\\Youtube Comments Bulking\\Bulking\\credentials\\client_secret_451643327428-aisesqlb3clv2m3voek0d46h9h17r0c1.apps.googleusercontent.com.json"):
            flow = InstalledAppFlow.from_client_secrets_file("C:\\Users\\PMYLS\\Desktop\\Youtube Comments Bulking\\Bulking\\credentials\\client_secret_451643327428-aisesqlb3clv2m3voek0d46h9h17r0c1.apps.googleusercontent.com.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        else:
            messages.error(request, 'Credentials file not found.')
            return render(request, 'home.html')

        youtube = build('youtube', 'v3', credentials=credentials)

        # Get the comments for the video
        next_page_token = None

        while True:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                pageToken=next_page_token
            ).execute()

            for item in response['items']:
                comment_id = item['id']  # Get the comment ID
                try:
                    # Reply to the comment
                    youtube.comments().insert(
                        part='snippet',
                        body={
                            'snippet': {
                                'parentId': comment_id,
                                'textOriginal': reply_text
                            }
                        }
                    ).execute()
                    messages.success(request, 'Replied to all comments successfully!')
                except Exception as e:
                    messages.error(request, f'Failed to reply to comment: {str(e)}')

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return render(request, 'home.html')
    else:
        return render(request, 'home.html')