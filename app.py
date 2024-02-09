from flask import Flask, request
from textblob import TextBlob
import googleapiclient.discovery
import googleapiclient.errors

app = Flask(__name__)

@app.get('/analysis')
def analysis_api():
    url = request.args.get('url', '')
    video_id = url.split('=')[1]
    comments, count = get_comments(video_id)

    if count == "0":
        return count, 200
    else:
        positive = 0
        neutral = 0
        negative = 0

        for comment in comments:
            mood = get_mood(comment, threshold=0.01)
            if mood == "positive":
                positive = positive + 1
            elif mood == "negative":
                negative = negative + 1
            else:
                neutral = neutral + 1
        
        positive_score = (positive / len(comments)) * 100
        neutral_score = (neutral / len(comments)) * 100
        negative_score = (negative / len(comments)) * 100

        overall_score = str(positive_score) + "0," + str(neutral_score) + "0," + str(negative_score) + "0"

        return overall_score, 200

def get_mood(input_text, threshold):
    sentiment = TextBlob(input_text).sentiment.polarity

    friendly_threshold = threshold
    hostile_threshold = -threshold

    if sentiment >= friendly_threshold:
        return "positive"
    elif sentiment <= hostile_threshold:
        return "negative"
    else:
        return "neutral"

def get_comments(vidID):
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyBYPNUXqgnRg1-5tnZsn_lbVib-WjG6IAM"

    youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)

    comment_request = youtube.videos().list(
    part="statistics",
    id=vidID)

    comment_response = comment_request.execute()
    comment_count = comment_response.get("items")[0].get("statistics").get("commentCount")

    empty = []

    if comment_count == "0":
        return empty, comment_count
    else:
        request = youtube.commentThreads().list(
        part="snippet",
        videoId=vidID,
        maxResults=500)

        response = request.execute()

        comment_list = []

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment = comment.replace("<" , "~")
            comment = comment.replace(">" , "~")
            comment = comment.replace("&#39;", "")
            comment = comment.replace("&quot;", '"')
            commentArr = []
            commentArr = comment.split("~")
            for comment in commentArr:
                if "href" in comment:
                    commentArr.remove(comment)
                if "/a" in comment:
                    commentArr.remove(comment)
            comment = "".join(commentArr)
            comment_list.append(str(comment))
        
        return comment_list, comment_count

if __name__ == '__main__':
    app.run()
