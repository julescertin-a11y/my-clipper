import streamlit as st
import os
import glob

st.set_page_config(page_title="TikTok Video Clipper", page_icon="🎬", layout="centered")

st.title("🎬 TikTok Video Clipper")
st.write("Importe ton fichier vidéo (MP4/MOV) pour le découper instantanément au format TikTok !")

# 1. Zone d'importation de fichier vidéo
uploaded_file = st.file_uploader("Choisissez un fichier vidéo", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    st.subheader("⚙️ Paramètres du clip")
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.number_input("Temps de début (en secondes) :", min_value=0, value=0, step=1)
    with col2:
        duration = st.number_input("Durée du clip (en secondes) :", min_value=1, max_value=300, value=60, step=1)

    if st.button("🚀 Générer le clip"):
        status = st.empty()
        status.info("⏳ Nettoyage des anciens fichiers...")
        
        # Nettoyage des fichiers temporaires
        for f in glob.glob("input_video.*") + glob.glob("output_clip.*"):
            try:
                os.remove(f)
            except Exception:
                pass

        # Sauvegarde du fichier importé
        file_extension = os.path.splitext(uploaded_file.name)[1]
        input_filename = f"input_video{file_extension}"
        output_filename = "output_clip.mp4"
        
        with open(input_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        status.info("✂️ Découpage de la vidéo avec FFmpeg...")

        # Commande FFmpeg pour découper la vidéo sans réencodage rapide
        cmd = f'ffmpeg -y -ss {start_time} -i "{input_filename}" -t {duration} -c copy "{output_filename}"'
        exit_code = os.system(cmd)

        if exit_code == 0 and os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
            status.success("🎉 Clip généré avec succès !")
            
            # Affichage du résultat
            st.video(output_filename)
            
            # Bouton de téléchargement
            with open(output_filename, "rb") as file:
                st.download_button(
                    label="⬇️ Télécharger le clip MP4",
                    data=file,
                    file_name="tiktok_clip.mp4",
                    mime="video/mp4"
                )
        else:
            status.error("❌ Erreur lors du découpage de la vidéo avec FFmpeg. Vérifie le format de ton fichier.")
