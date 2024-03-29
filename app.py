from flask import Flask, render_template, url_for
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi as yta
from flask import request as rq
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
  return render_template("index.html")

@app.route("/summarize", methods=["GET", "POST"])
def summarize():
    if rq.method == "POST":
        # Your existing code for handling POST requests goes here
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": "Bearer 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"}
        url=rq.form["url_search"]
        id=get_youtube_video_id(url)
        data=get_transcript(id)
        minL=80
        maxL=150
        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        
        output = query({
            "inputs": data,
            "parameters":{"min_length":minL, "max_length":maxL}
        })
        return render_template("index.html", results=output)
    else:
        # Your existing code for handling GET requests goes here
        return render_template("index.html")


def get_youtube_video_id(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Check if the domain is youtube.com
    if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtube.com':
        # Extract the video ID from the query parameters
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]

        return video_id

    # Check if the domain is youtu.be
    elif parsed_url.netloc == 'youtu.be':
        # Extract the video ID from the path
        video_id = parsed_url.path[1:]

        return video_id

    else:
        # URL is not from YouTube
        return None
    
def get_transcript(video_id):
    # Initialize data variable
    data = None

    # Check if subtitles are available
    try:
        data = yta.get_transcript(video_id)
    except Exception as e:
        if "Subtitles are disabled for this video" in str(e):
            print(f"TranscriptsDisabled: Subtitles are disabled for the video {video_id}! {e}")
            # Handle the situation where subtitles are disabled (e.g., print an error message, exit the program, etc.)
            return None
        else:
            # Handle other exceptions if needed
            print(f"An error occurred: {e}")
            return None

    # Check if data is None before iterating
    if data is not None:
        transcript = ''
        for value in data:
            for key, val in value.items():
                if key == 'text':
                    transcript += val

        return transcript
    else:
        print("No transcript available for the given video.")
        return None

if __name__=='__main__':
  app.debug=True
  app.run()