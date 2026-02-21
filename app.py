import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from mistralai import Mistral # <-- NOUVELLE SYNTAXE ICI

# Configuration de la page
st.set_page_config(page_title="AIO Core - Auditeur Sémantique", page_icon="🛡️", layout="wide")

st.title("🛡️ AIO Core : Audit de Contradiction IA")
st.markdown("Cet outil aspire une page web, sépare les données cachées (JSON-LD) du texte visible (HTML), et détecte les failles d'hallucination pour les LLM.")

# 1. Saisie de l'URL
url_input = st.text_input("Entrez l'URL à auditer (ex: votre lien Netlify) :", "https://hotaru2.netlify.app/produit.html")

if st.button("Lancer l'Audit AIO", type="primary"):
    with st.spinner("Aspiration du site et analyse en cours..."):
        try:
            # 2. Aspiration de la page
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
            response = requests.get(url_input, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # 3. Extraction du JSON-LD (Le piège)
            json_ld_data = "Aucun JSON-LD trouvé."
            scripts = soup.find_all('script', type='application/ld+json')
            if scripts:
                json_ld_data = scripts[0].string 

            # 4. Extraction du texte visible (La vérité)
            for script in soup(["script", "style"]):
                script.extract()
            visible_text = soup.get_text(separator='\n', strip=True)

            # 5. Affichage des données brutes
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🕵️ Données Cachées (JSON-LD)")
                st.code(json_ld_data[:1000] + "...", language="json")
            with col2:
                st.subheader("👁️ Texte Visible (HTML)")
                st.text(visible_text[:1000] + "...")

            # 6. Le Super-Prompt envoyé à Mistral
            # N'OUBLIE PAS DE REMETTRE TA CLÉ API ICI 👇
            client = Mistral(api_key="GYYg0c5eMGqq9owHVjqmxVwGz1gbbzI3") 
            
            prompt = f"""
            Tu es l'IA principale d'un outil d'audit nommé "AIO Core".
            Ton but est d'analyser une page web pour détecter si les machines (LLM, Google) sont trompées par le code source.
            
            Voici les données cachées dans le code (JSON-LD) destinées aux robots :
            {json_ld_data}
            
            Voici le texte réellement affiché aux humains sur le site (HTML) :
            {visible_text[:3000]}
            
            MISSION :
            1. Compare les informations clés (Prix, Stock, Dates, ou État du service).
            2. Identifie les contradictions MAJEURES entre le JSON-LD et le texte visible.
            3. Rédige un "RAPPORT D'ALERTE AIO" professionnel et percutant.
            
            Si tu trouves une contradiction, sois très alarmiste (car cela détruit le SEO et l'ingestion IA du client).
            Si tout correspond, indique que le site est "AIO Compliant".
            """

            # 7. Appel à l'IA avec la NOUVELLE SYNTAXE
            chat_response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            )
            
            # 8. Affichage du verdict final
            st.error("🚨 VERDICT DE L'AUDIT AIO 🚨")
            st.markdown(chat_response.choices[0].message.content)

        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
