import streamlit as st
import requests
import os
import glob

st.set_page_config(page_title="YouTube to TikTok Clipper", page_icon="🎬")

st.title("🎬 TikTok Clipper")
st.write("Entre un lien YouTube pour générer automatiquement un clip TikTok !")

url_input = st.text_input("URL YouTube :")
duration = st.slider("Durée du clip (secondes) :", min_value=10, max_value=180, value=60)

def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    return None

# Liste de secours des instances Invidious les plus rapides et stables
INVIDIOUS_INSTANCES = [
    "https://invidious.nerdvpn.de",
    "https://invidious.flokinet.to",
    "https://inv.tux.pizza",
    "https://invidious.drgns.space"
]

if st.button("🚀 Générer le clip"):
    video_id = extract_video_id(url_input)
    
    if not video_id:
        st.error("URL invalide. Utilise un lien du type https://youtu.be/xxx ou https://www.youtube.com/watch?v=xxx")
    else:
        status = st.empty()
        status.info("⏳ Traitement en cours...")
        
        # Nettoyage
        for f in glob.glob("downloaded_video.*") + glob.glob("output_clip.*"):
            try:
                os.remove(f)
            except Exception:
                pass

        video_url = None
        status.info("📥 Recherche d'un serveur relais disponible...")
        
        # Boucle sur les instances pour trouver la première qui répond vite
        for instance in INVIDIOUS_INSTANCES:
            try:
                api_endpoint = f"{instance}/api/v1/videos/{video_id}"
                res = requests.get(api_endpoint, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if "formatStreams" in data and len(data["formatStreams"]) > 0:
                        video_url = data["formatStreams"][-1]["url"]
                        break
            except Exception:
                continue

        if not video_url:
            st.error("Les serveurs relais sont temporairement occupés. Réessaie dans quelques secondes.")
        else:
            try:
                status.info("📥 Téléchargement du flux vidéo...")
                r = requests.get(video_url, stream=True, timeout=30)
                downloaded_file = "downloaded_video.mp4"
                
                with open(downloaded_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)

                if os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 0:
                    status.info("✂️ Découpage du clip avec ffmpeg...")
                    output_file = "output_clip.mp4"
                    
                    cmd = f'ffmpeg -y -i "{downloaded_file}" -ss 00:00:00 -t {duration} -c copy "{output_file}"'
                    os.system(cmd)

                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        status.success("🎉 Clip généré avec succès !")
                        st.video(output_file)
                        with open(output_file, "rb") as file:
                            st.download_button(
                                label="⬇️ Télécharger le clip MP4",
                                data=file,
                                file_name="tiktok_clip.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("Erreur lors du découpage vidéo.")
                else:
                    st.error("Erreur : Fichier téléchargé vide.")

            except Exception as e:
                st.error(f"Erreur lors du téléchargement : {e}")
