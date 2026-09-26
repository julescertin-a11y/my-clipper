import streamlit as st
from pytubefix import YouTube
import os
import glob

st.set_page_config(page_title="YouTube to TikTok Clipper", page_icon="🎬")

st.title("🎬 TikTok Clipper")
st.write("Entre un lien YouTube pour générer automatiquement un clip TikTok !")

url_input = st.text_input("URL YouTube :")
duration = st.slider("Durée du clip (secondes) :", min_value=10, max_value=180, value=60)

if st.button("🚀 Générer le clip"):
    if not url_input:
        st.error("Veuillez entrer une URL valide.")
    else:
        status = st.empty()
        status.info("⏳ Traitement en cours...")
        
        # Nettoyage des anciens fichiers
        for f in glob.glob("downloaded_video.*") + glob.glob("output_clip.*"):
            try:
                os.remove(f)
            except Exception:
                pass

        try:
            status.info("📥 Connexion à YouTube via PyTubeFix...")
            
            # Essai avec le client ANDROID_VR qui passe outre la connexion obligatoire
            try:
                yt = YouTube(url_input, client='ANDROID_VR')
                stream = yt.streams.filter(file_extension='mp4').first()
            except Exception:
                # Client de secours MWEB
                yt = YouTube(url_input, client='MWEB')
                stream = yt.streams.filter(file_extension='mp4').first()

            status.info("📥 Téléchargement de la vidéo...")
            downloaded_file = stream.download(filename="downloaded_video.mp4")

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
                st.error("Le fichier téléchargé est vide.")

        except Exception as e:
            st.error(f"Erreur lors de la récupération : {e}")
