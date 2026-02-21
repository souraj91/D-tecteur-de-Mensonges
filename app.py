import streamlit as st
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral

# Configuration de la page
st.set_page_config(page_title="AIO Core - Auditeur Sémantique", page_icon="🛡️", layout="wide")

# --- BARRE LATÉRALE : CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration AIO")
    mistral_key = st.text_input("Clé API Mistral :", type="password", help="Obligatoire pour l'analyse IA")
    
    st.divider()
    
    st.header("🛡️ Contournement Anti-Bot")
    st.markdown("Nécessaire pour les sites comme Conforama, Fnac, Amazon...")
    use_proxy = st.checkbox("Activer le mode Anti-Bot (ScrapingBee)")
    scrapingbee_key = st.text_input("Clé API ScrapingBee :", type="password", disabled=not use_proxy)

# --- CONTENU PRINCIPAL ---
st.title("🛡️ AIO Core : Détecteur d'Hallucination")
st.markdown("Analysez n'importe quel site web (même protégé) pour auditer la donnée visible vs la donnée cachée.")

url_input = st.text_input("Entrez l'URL à auditer :", "https://hotaru2.netlify.app/produit.html")

if st.button("Lancer l'Audit AIO", type="primary"):
    if not mistral_key:
        st.error("⚠️ Veuillez entrer votre clé API Mistral dans la barre latérale.")
        st.stop()
        
    if use_proxy and not scrapingbee_key:
        st.error("⚠️ Vous avez activé le mode Anti-Bot. Veuillez entrer votre clé ScrapingBee.")
        st.stop()

    with st.spinner("Aspiration du site en cours (peut prendre 10s sur les sites protégés)..."):
        try:
            # 1. LOGIQUE D'ASPIRATION (Classique vs Anti-Bot)
            if use_proxy:
                # On utilise le blindé (ScrapingBee) pour exécuter le JS et contourner Cloudflare
                api_url = "https://app.scrapingbee.com/api/v1/"
                params = {
                    "api_key": scrapingbee_key,
                    "url": url_input,
                    "render_js": "True", # Exécute le JavaScript (vital pour Conforama)
                    "premium_proxy": "True" # Contourne les gros pare-feux
                }
                response = requests.get(api_url, params=params)
            else:
                # Mode classique (pour ton site Netlify)
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
                response = requests.get(url_input, headers=headers)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 2. EXTRACTION DES DONNÉES
            json_ld_data = "Aucun JSON-LD trouvé."
            scripts = soup.find_all('script', type='application/ld+json')
            if scripts:
                json_ld_data = scripts[0].string 

            for script in soup(["script", "style"]):
                script.extract()
            visible_text = soup.get_text(separator='\n', strip=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🕵️ Données Cachées (JSON-LD)")
                st.code(json_ld_data[:800] + "...", language="json")
            with col2:
                st.subheader("👁️ Texte Visible (HTML)")
                st.text(visible_text[:800] + "...")

            # 3. ANALYSE IA PAR MISTRAL
            with st.spinner("Analyse des contradictions par l'IA..."):
                client = Mistral(api_key=mistral_key) 
                prompt = f"""
                Tu es l'IA principale d'un outil d'audit nommé "AIO Core".
                Voici les données cachées dans le code (JSON-LD) destinées aux robots :
                {json_ld_data}
                
                Voici le texte réellement affiché aux humains sur le site :
                {visible_text[:3000]}
                
                MISSION : Compare les informations clés (Prix, Stock, Dates). Identifie les contradictions MAJEURES entre le JSON-LD et le texte visible. Rédige un "RAPPORT D'ALERTE AIO" professionnel. Sois direct et concis.
                """

                chat_response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.error("🚨 VERDICT DE L'AUDIT AIO 🚨")
                st.markdown(chat_response.choices[0].message.content)

        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse : {e}")
