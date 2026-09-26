import streamlit as st
import requests
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
        
        # Nettoyage
        for f in glob.glob("downloaded_video.*") + glob.glob("output_clip.*"):
            try:
                os.remove(f)
            except Exception:
                pass

        try:
            status.info("📥 Téléchargement de la vidéo via API...")
            
            # Utilisation de l'API Cobalt pour contourner le blocage anti-bot de YouTube
            api_url = "https://api.cobalt.tools/api/json"
            payload = {
                "url": url,
                "vCodec": "h264",
                "vQuality": "720"
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            res = requests.post(api_url, json=payload, headers=headers)
            data = res.json()

            if "url" in data:
                video_url = data["url"]
                video_data = requests.get(video_url).content
                downloaded_file = "downloaded_video.mp4"
                
                with open(downloaded_file, "wb") as f:
                    f.write(video_data)

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
                        st.error("Erreur lors de la création du clip.")
                else:
                    st.error("Impossible d'enregistrer la vidéo.")
            else:
                st.error("Impossible de récupérer la vidéo. Assurez-vous que le lien est valide.")

        except Exception as e:
            st.error(f"Erreur : {e}")
