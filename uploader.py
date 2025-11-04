import upload_youtube 
from loguru import logger 

def upload_video(api_json, video_path, channel_id):
    vid_title = "This is video upload test"
    vid_desription ="test app"
    keywords = ["hello"]

    unique_vid_id = f""


    video_id = upload_youtube.upload_video(api_json, channel_id, video_path, unique_vid_id, 
                                          vid_title = vid_title, vid_desription=vid_desription, keywords=keywords)
    
    if video_id is not None:
        logger.info(f"✅✅Sucessfully uploaded {video_path}")
    
    else:
        logger.info(f"❌❌ Unable to upload {video_path}")


if __name__ == "__main__":
    api_json_path = r"D:\projects\upload_to_youtube\client_secret_247123290685-aiati5015g278cnsek7undp586r6c9bd.apps.googleusercontent.com.json"
    video_path = r"D:\projects\upload_to_youtube\video_1.mkv"
    channel_id = "UCNuldP9ua6bh4oAI6hy1-4w"
    upload_video(api_json_path, video_path, channel_id)