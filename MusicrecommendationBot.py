import spotipy
import deepface 
from spotipy.oauth2 import SpotifyClientCredentials


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET"
))

def search_songs_by_mood(mood, limit=5):
    query = f"{mood} indian"
    results = sp.search(q=query, type='track', limit=limit)

    recommendations = []
    for track in results['tracks']['items']:
        name = track['name']
        artist = track['artists'][0]['name']
        link = track['external_urls']['spotify']
        recommendations.append(f"🎵 *{name}* by *{artist}*\n🔗 [Listen]({link})")
    
    return recommendations

from deepface import DeepFace

def detect_mood_from_image(image_path):
    analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    emotion = analysis[0]['dominant_emotion']

    # Map emotion to music mood
    if emotion in ["happy", "surprise"]:
        return "Happy"
    elif emotion in ["sad", "fear"]:
        return "Sad"
    elif emotion in ["angry", "disgust"]:
        return "Energetic"
    else:
        return "Chill"

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import os


TELEGRAM_TOKEN = "TELEGRAM TOKEN"

# Handles incoming photos
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_path = "user_photo.jpg"
    await file.download_to_drive(image_path)

    # Analyze emotion
    mood = detect_mood_from_image(image_path)
    songs = search_songs_by_mood(mood)

    await update.message.reply_text(f"🧠 Mood detected: *{mood}*\n\n🎧 Recommended Songs:", parse_mode="Markdown")
    for song in songs:
        await update.message.reply_text(song, parse_mode="Markdown")

# Launch bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.run_polling()
