import os
import re
import streamlit as st
import yt_dlp
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
st.set_page_config(page_title="YouTube to TikTok", page_icon="🎬")

st.title("🎬 YouTube to TikTok Clipper")
st.write("Entre un lien YouTube pour générer automatiquement un clip TikTok !")

url_input = st.text_input("URL YouTube :", placeholder="https://www.youtube.com/watch?v=...")
duree_clip = st.slider("Durée du clip (secondes) :", 15, 60, 30)

if st.button("🚀 Générer le clip", type="primary"):
    if not url_input:
        st.error("Renseigne une URL YouTube.")
    else:
        try:
            status = st.status("Traitement en cours...", expanded=True)
            
            # Téléchargement
            status.write("📥 Téléchargement de la vidéo...")
            ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', 'outtmpl': 'temp.mp4', 'quiet': True, 'overwrites': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_input])
                
            # Analyse IA
            status.write("🧠 Analyse de l'audio avec Whisper...")
            model = whisper.load_model("base")
            result = model.transcribe("temp.mp4", fp16=False)
            segments = result.get("segments", [])
            
            meilleur_debut = segments[0]['start']
            max_densite = 0
            for seg in segments:
                t_start = seg['start']
                t_end = t_start + duree_clip
                mots = sum(len(s['text'].split()) for s in segments if s['start'] >= t_start and s['end'] <= t_end)
                if mots > max_densite:
                    max_densite = mots
                    meilleur_debut = t_start
            
            meilleur_fin = meilleur_debut + duree_clip
            sous_titres = [{'start': s['start'] - meilleur_debut, 'end': s['end'] - meilleur_debut, 'text': s['text'].strip()} 
                           for s in segments if s['start'] >= meilleur_debut and s['end'] <= meilleur_fin]

            # Montage 9:16
            status.write("✂️ Recadrage TikTok & Sous-titres...")
            clip = VideoFileClip("temp.mp4").subclip(meilleur_debut, meilleur_fin)
            w, h = clip.size
            target_w = int(h * (9 / 16))
            x1 = (w - target_w) / 2
            clip_vertical = clip.crop(x1=x1, y1=0, x2=x1 + target_w, y2=h)
            
            calques = [clip_vertical]
            for sub in sous_titres:
                txt = sub['text']
                if len(txt) > 30:
                    txt = "\n".join(re.findall(r'.{1,25}(?:\s+|$)', txt)).strip()
                try:
                    txt_clip = (TextClip(txt, fontsize=40, color='yellow', font='Liberation-Sans-Bold', method='caption', size=(target_w - 60, None))
                                .set_position(('center', h * 0.75)).set_start(sub['start']).set_end(sub['end']))
                    calques.append(txt_clip)
                except Exception:
                    pass

            video_finale = CompositeVideoClip(calques)
            video_finale.write_videofile("output_tiktok.mp4", codec="libx264", audio_codec="aac", fps=30, threads=4, preset="fast")
            
            clip.close()
            clip_vertical.close()
            video_finale.close()
            if os.path.exists("temp.mp4"):
                os.remove("temp.mp4")

            status.update(label="✅ Traitement terminé !", state="complete", expanded=False)
            
            st.success("Voici ton clip !")
            st.video("output_tiktok.mp4")
            
            with open("output_tiktok.mp4", "rb") as file:
                st.download_button("💾 Télécharger le clip MP4", data=file, file_name="tiktok_clip.mp4", mime="video/mp4")

        except Exception as e:
            st.error(f"Erreur : {e}")
