import streamlit as st
import yt_dlp
import os
import glob

st.set_page_config(page_title="YouTube to TikTok Clipper", page_icon="🎬")

st.title("🎬 TikTok Clipper")
st.write("Entre un lien YouTube pour générer automatiquement un clip TikTok !")

url = st.text_input("URL YouTube :")
duration = st.slider("Durée du clip (secondes) :", min_value=10, max_value=180, value=60)

if st.button("🚀 Générer le clip"):
    if not url:
        st.warning("Veuillez entrer une URL valide.")
    else:
        status = st.empty()
        status.info("⏳ Traitement en cours...")
        
        # Nettoyage des anciens fichiers
        for f in glob.glob("downloaded_video.*") + glob.glob("output_clip.*"):
            try:
                os.remove(f)
            except Exception:
                pass

        ydl_opts = {
            'format': 'b/m4a/mp4',
            'outtmpl': 'downloaded_video.%(ext)s',
            'overwrites': True,
            'quiet': True,
            'no_warnings': True,
            'check_formats': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                    'player_skip': ['webpage', 'configs']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        try:
            status.info("📥 Téléchargement de la vidéo...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                ext = info.get('ext', 'mp4')
                downloaded_file = f"downloaded_video.{ext}"

            if not os.path.exists(downloaded_file) or os.path.getsize(downloaded_file) == 0:
                st.error("Erreur : Le fichier téléchargé est vide. YouTube a bloqué la requête.")
            else:
                status.info("✂️ Découpage du clip avec ffmpeg...")
                output_file = "output_clip.mp4"
                
                # Commande FFmpeg pour découper
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
                    st.error("Erreur lors de la création du clip vidéo.")

        except Exception as e:
            st.error(f"Erreur : {e}")
