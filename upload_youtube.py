import os
import json
import google.auth.transport.requests
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from loguru import logger 

def youtube_authenticate(creds_file, token_file):
    """
    Authenticate with YouTube API using OAuth2.
    - If token is valid → use it.
    - If token expired → try refresh.
    - If refresh fails → delete and reauthenticate.
    """
    scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly"
    ]
    creds = None

    # 1️⃣ Try to load existing token file
    if os.path.exists(token_file):
        logger.info(f"🔑 Loading token from {token_file}")
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    # 2️⃣ If creds missing or invalid → handle refresh or full login
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired access token...")
                creds.refresh(google.auth.transport.requests.Request())
            else:
                raise RefreshError("Token missing or invalid")

        except RefreshError as e:
            logger.warning(f"⚠️ Token refresh failed: {e}")
            # Delete invalid token file and reauthenticate
            if os.path.exists(token_file):
                os.remove(token_file)
                logger.info("🗑️ Deleted expired or revoked token file")

            if not creds_file or not os.path.exists(creds_file):
                raise FileNotFoundError(
                    "❌ Google API credentials file not found. "
                    "Set GOOGLE_API_CREDS_JSON_PATH in .env"
                )

            # Start new OAuth flow
            logger.info("🌐 Starting new OAuth authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            creds = flow.run_local_server(port=0)

        # 3️⃣ Save new or refreshed token
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
            logger.info(f"✅ Token saved to {token_file}")

    # 4️⃣ Return authenticated YouTube client
    return build("youtube", "v3", credentials=creds)



def read_text_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")




def upload(youtube, video_path, title, description, keywords, channel_id, category_id, language="None", thumbnail_path=""):

    iso_lang_code = None
    
    request_body = {
        "snippet": {
            "channelId": channel_id,
            #"categoryId": str(category_id),
            "title": title,
            #"description": description,
            #"tags": keywords,
            #"defaultLanguage": iso_lang_code,        
            #"defaultAudioLanguage": iso_lang_code 
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        },
    }
    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media)

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading... {int(status.progress() * 100)}%")

        logger.info(f"✅ Upload complete {video_path}!")
        print("📺Upload complete! Video ID:", response["id"])
        #return response["id"]
    
        video_id = response["id"]

        # --- Upload custom thumbnail if provided ---
        if os.path.exists(thumbnail_path):
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                print("🖼️ Thumbnail uploaded successfully!")
            except Exception as e:
                print("⚠️ Thumbnail upload failed:", e)

        return video_id

    except HttpError as e:
        error_str = str(e)
        # Handle different cases
        if e.resp.status == 400 and "uploadLimitExceeded" in error_str:
            logger.error("🚨 Upload limit exceeded. Try again after 24 hours.")
            return None
        elif e.resp.status == 403 and "quotaExceeded" in error_str:
            logger.error("🚨 YouTube API quota exceeded. Wait until quota resets or request more quota.")
            return None
        else:
            logger.error(f"❌ Unexpected error: {error_str}")




def upload_video(api_json, channel_id, video_path, thumbnail_path="",
                vid_title = None, vid_desription=None, keywords=None):
    """
    Uploads a video to YouTube
    """
    youtube = youtube_authenticate(api_json, "auth.token")
    category_id ="22"
    video_id = upload(youtube, video_path, vid_title, vid_desription, keywords, channel_id, category_id, thumbnail_path=thumbnail_path)

    return video_id

if __name__ == "__main__":
    pass