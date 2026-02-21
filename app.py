import streamlit as st
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral

# Configuration de la page
st.set_page_config(page_title="AIO Core - Scanner de Vulnérabilité IA", page_icon="🛡️", layout="wide")

# --- BARRE LATÉRALE : CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration AIO")
    mistral_key = st.text_input("Clé API Mistral :", type="password", help="Obligatoire pour l'analyse IA")
    
    st.divider()
    
    st.header("🛡️ Contournement Anti-Bot")
    st.markdown("Nécessaire pour les sites B2B/E-commerce hyper protégés (Conforama, Fnac, Amazon...)")
    use_proxy = st.checkbox("Activer le mode Anti-Bot (ScrapingBee)")
    scrapingbee_key = st.text_input("Clé API ScrapingBee :", type="password", disabled=not use_proxy)

# --- CONTENU PRINCIPAL ---
st.title("🛡️ AIO Core : Scanner de Vulnérabilité IA")
st.markdown("Réalisez un Crash Test d'Ingestion IA sur n'importe quel site web. Découvrez ce que les LLM et agents autonomes comprennent *vraiment* de votre page.")

url_input = st.text_input("Entrez l'URL à auditer :", "https://hotaru2.netlify.app/produit.html")

if st.button("Lancer le Crash Test AIO", type="primary"):
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
                api_url = "https://app.scrapingbee.com/api/v1/"
                params = {
                    "api_key": scrapingbee_key,
                    "url": url_input,
                    "render_js": "True",
                    "premium_proxy": "True"
                }
                response = requests.get(api_url, params=params)
            else:
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
                st.subheader("🕵️ Code Machine (JSON-LD)")
                st.code(json_ld_data[:800] + "...", language="json")
            with col2:
                st.subheader("👁️ Vérité Visuelle (HTML)")
                st.text(visible_text[:800] + "...")

            # 3. ANALYSE IA PAR MISTRAL AVEC LE PROMPT AIO
            with st.spinner("Génération du Rapport AIO Readiness..."):
                client = Mistral(api_key=mistral_key) 
                
                prompt = f"""
                Tu es l'IA principale d'un outil d'audit SaaS nommé "AIO Core". 
                Ton rôle N'EST PAS de faire un audit SEO classique. Ton rôle est de réaliser un "Crash Test d'Ingestion IA". 
                Tu dois évaluer si la page web actuelle risque d'induire en erreur les moteurs de réponse (ChatGPT, Perplexity, Gemini) et les agents d'achats autonomes B2B.

                Voici le code caché (JSON-LD) actuellement destiné aux robots :
                {json_ld_data}

                Voici la vérité visuelle (le texte HTML) lue par les clients humains :
                {visible_text[:3000]}

                MISSION : Rédige un rapport "AIO Readiness" (Optimisation pour l'IA) destiné à un Directeur Marketing. Sois percutant, alarmiste si nécessaire, et orienté "Business".

                Structure OBLIGATOIRE de ton rapport :

                ### 🔴 1. Risque d'Hallucination IA : [Donne un % de 0 à 100]
                Explique en une phrase le niveau de danger. (ex: "Contradiction critique détectée entre le code machine et l'affichage humain").

                ### 🤖 2. Ce que les IA disent de vous aujourd'hui (Le Constat)
                Explique très concrètement ce que ChatGPT, Perplexity ou un agent RAG B2B va répondre à un utilisateur qui pose une question sur cette page (en te basant sur le code empoisonné). Mets en évidence le mensonge exact (Prix, Stock, Dates, etc.).

                ### 📉 3. Impact Business (La Douleur)
                Explique la conséquence directe sur les ventes, la conversion ou l'image de marque si les LLM continuent de propager ces fausses données (ex: "Désindexation par les agents d'achat, perte de trafic qualifié...").

                ### 🟢 4. Le Patch AIO (La Solution)
                Pour corriger cela, génère le bloc JSON-LD parfait et mis à jour qui reflète la VRAIE information visuelle. C'est le code que le client devra injecter pour devenir "AIO Compliant".
                """

                chat_response = client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.error("🚨 RAPPORT DE VULNÉRABILITÉ IA 🚨")
                st.markdown(chat_response.choices[0].message.content)

        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse : {e}")
