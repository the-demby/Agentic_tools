import os, requests
from dotenv import load_dotenv

""""
Vous devez créer les variables ACCESS_TOKEN et AUTHOR_URN à partir de vos information Linkedin dans un fichier: .env

"""

load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")

def post_to_linkedin(text: str):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 201:
        print("Votre post LinkedIn est en ligne🍹\n")
    else:
        print("Erreur lors du post.")
