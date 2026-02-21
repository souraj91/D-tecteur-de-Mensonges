import streamlit as st
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral
import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(page_title="AIO Core - Scanner & Radar SaaS", page_icon="🛡️", layout="wide")

# --- BARRE LATÉRALE : CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration AIO")
    mistral_key = st.text_input("Clé API Mistral :", type="password")
    
    st.divider()
    
    st.header("🛡️ Contournement Anti-Bot")
    use_proxy = st.checkbox("Activer le mode Anti-Bot (ScrapingBee)")
    scrapingbee_key = st.text_input("Clé API ScrapingBee :", type="password", disabled=not use_proxy)

# --- CONTENU PRINCIPAL ---
st.title("🛡️ AIO Core : Plateforme d'Audit & Monitoring")
st.markdown("Détectez les hallucinations IA en temps réel et monitorez votre compatibilité (AIO Readiness) sur le long terme.")

# --- ONGLETS POUR SÉPARER L'AUDIT DU MONITORING ---
tab1, tab2 = st.tabs(["🔍 Crash Test (Audit Ponctuel)", "📈 Radar AIO (Monitoring SaaS)"])

# ==========================================
# ONGLET 1 : LE CRASH TEST (Ce qu'on avait avant)
# ==========================================
with tab1:
    url_input = st.text_input("Entrez l'URL à auditer :", "https://hotaru2.netlify.app/produit.html")

    if st.button("Lancer le Crash Test AIO", type="primary"):
        if not mistral_key:
            st.error("⚠️ Veuillez entrer votre clé API Mistral à gauche.")
            st.stop()

        with st.spinner("Aspiration du site en cours..."):
            try:
                # 1. Aspiration
                if use_proxy:
                    api_url = "https://app.scrapingbee.com/api/v1/"
                    params = {"api_key": scrapingbee_key, "url": url_input, "render_js": "True", "premium_proxy": "True"}
                    response = requests.get(api_url, params=params)
                else:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(url_input, headers=headers)
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # 2. Extraction
                json_ld_data = "Aucun JSON-LD trouvé."
                scripts = soup.find_all('script', type='application/ld+json')
                if scripts:
                    json_ld_data = scripts[0].string 

                for script in soup(["script", "style"]):
                    script.extract()
                visible_text = soup.get_text(separator='\n', strip=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("🕵️ Code Machine (JSON-LD)")
                    st.code(json_ld_data[:500] + "...", language="json")
                with col_b:
                    st.subheader("👁️ Vérité Visuelle (HTML)")
                    st.text(visible_text[:500] + "...")

                # 3. Analyse IA
                with st.spinner("Génération du Rapport..."):
                    client = Mistral(api_key=mistral_key) 
                    prompt = f"""
                    Tu es l'IA principale d'un outil d'audit SaaS nommé "AIO Core".
                    Code caché aux robots : {json_ld_data}
                    Vérité visuelle HTML : {visible_text[:2000]}
                    MISSION : Rédige un rapport "AIO Readiness" percutant pour un Directeur Marketing.
                    Structure : 
                    1. Risque d'Hallucination IA (en %)
                    2. Ce que les IA disent de vous aujourd'hui (Le Constat)
                    3. Impact Business (La Douleur)
                    4. Le Patch AIO (Le code corrigé)
                    """
                    chat_response = client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.error("🚨 RAPPORT DE VULNÉRABILITÉ IA 🚨")
                    st.markdown(chat_response.choices[0].message.content)

            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse : {e}")

# ==========================================
# ONGLET 2 : LE SIMULATEUR SAAS (Le Radar)
# ==========================================
with tab2:
    st.header("📡 Simulation du Radar AIO (Monitoring 30 Jours)")
    st.markdown("Démontrez à votre client pourquoi un audit ponctuel ne suffit pas. Les sites web sont vivants, et une simple mise à jour marketing peut détruire votre compatibilité IA du jour au lendemain.")
    
    if st.button("Lancer la simulation SaaS", type="primary"):
        with st.spinner("Génération de l'historique d'ingestion IA..."):
            
            # Création de fausses données intelligentes
            dates = []
            scores = []
            current_score = 98 # Le site commence en bonne santé
            
            for i in range(30):
                # On recule dans le temps de 30 jours jusqu'à aujourd'hui
                jour = (datetime.today() - timedelta(days=30-i)).strftime("%d/%m")
                dates.append(jour)
                
                # Le Scénario catastrophe :
                if i == 12:
                    current_score = 42 # J+12 : Un dev déploie un nouveau thème, le JSON-LD est cassé
                elif i == 13 or i == 14:
                    current_score = 42 # J+13/14 : L'erreur reste en ligne, les IA hallucinent
                elif i == 15:
                    current_score = 95 # J+15 : AIO Core envoie l'alerte, l'équipe corrige !
                elif i == 24:
                    current_score = 65 # J+24 : Promo Black Friday, le prix change visuellement mais pas dans le code
                elif i == 25:
                    current_score = 99 # J+25 : AIO Core détecte la contradiction, corrigé instantanément.
                else:
                    # Bruit normal
                    current_score += random.randint(-2, 2)
                    current_score = min(100, max(0, current_score))
                
                scores.append(current_score)

            # Création du tableau de données (DataFrame pandas)
            df = pd.DataFrame({
                "Date": dates,
                "Score AIO Readiness (%)": scores
            }).set_index("Date")

            # Affichage du graphique
            st.line_chart(df, color="#dc2626", height=400)
            
            # L'explication commerciale en dessous
            st.warning("⚠️ **Analyse de l'incident majeur (Jour 12 à 14) :**")
            st.markdown("""
            * **Ce qu'il s'est passé :** L'équipe technique a mis à jour le design de la page produit. Visuellement, tout était parfait. Mais ils ont accidentellement écrasé la balise JSON-LD.
            * **Conséquence IA :** Pendant 3 jours, Google Shopping a affiché "Rupture de Stock" et ChatGPT a donné un mauvais prix à vos clients.
            * **La Valeur du Radar AIO :** Sans notre monitoring quotidien, cette erreur vous aurait coûté des milliers d'euros de ventes perdues avant qu'un humain ne s'en rende compte.
            """)
