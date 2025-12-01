import streamlit as st

st.set_page_config(
    page_title="GeoS - Disaster Preparedness",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for developer-style UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #34d399 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.8rem;
        color: #94a3b8;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #60a5fa;
        margin-top: 3rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #60a5fa;
        padding-left: 1rem;
    }

    .info-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .info-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 12px rgba(96, 165, 250, 0.3);
        border-color: #60a5fa;
    }

    .team-member {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 3px solid #34d399;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: #e2e8f0;
        font-weight: 500;
        transition: all 0.3s;
    }

    .team-member:hover {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        border-left-width: 5px;
        padding-left: 1.5rem;
    }

    .course-badge {
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        display: inline-block;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(124, 58, 237, 0.4);
    }

    .tech-tag {
        background: rgba(96, 165, 250, 0.2);
        border: 1px solid #60a5fa;
        color: #60a5fa;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }

    .stat-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        flex: 1;
        text-align: center;
        transition: all 0.3s;
    }

    .stat-box:hover {
        border-color: #60a5fa;
        transform: scale(1.05);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #60a5fa 50%, transparent 100%);
        margin: 3rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🌍 **GeoS Navigation**")
st.sidebar.markdown("---")
st.sidebar.info("📍 Main Page - Overview")

# Hero Section
st.markdown('<h1 class="hero-title">GeoS: Enhancing Disaster Preparedness</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Utilizing Weather APIs and Proactive Geofencing</p>', unsafe_allow_html=True)

# Stats Section
st.markdown("""
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-number">5</div>
            <div class="stat-label">Team Members</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Weather Monitoring</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">Real-time</div>
            <div class="stat-label">Data Updates</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Project Overview
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="section-header">📊 Project Overview</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-card">
            <h3 style="color: #34d399; margin-top: 0;">🎯 Mission</h3>
            <p style="color: #cbd5e1; line-height: 1.8;">
                GeoS leverages real-time weather data and intelligent geofencing technology 
                to enhance disaster preparedness and community safety. Our system provides live 
                weather monitoring, automated data collection, and  alerts to keep communities 
                informed and safe.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="info-card">
            <h3 style="color: #fbbf24; margin-top: 0;">🔧 Key Features</h3>
            <ul style="color: #cbd5e1; line-height: 2;">
                <li>Real-time weather data monitoring via API</li>
                <li>Smart geofencing for location-based alerts</li>
                <li>Automated data scraping and collection</li>
                <li>RAG-powered chatbot for Disaster Readiness, Reduction, and Preparedness</li>
                <li>Email notifications and alert system</li>
                <li>Interactive data visualization</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<h2 class="section-header">🎓 Course Information</h2>', unsafe_allow_html=True)
    st.markdown('<div class="course-badge">Bachelor of Science in Computer Science - 2A</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-card" style="margin-top: 2rem;">
            <h3 style="color: #60a5fa; margin-top: 0;">💻 Technologies</h3>
            <div>
                <span class="tech-tag">Python</span>
                <span class="tech-tag">Streamlit</span>
                <span class="tech-tag">Flask</span>
                <span class="tech-tag">MongoDB</span>
                <span class="tech-tag">Weather API</span>
                <span class="tech-tag">Geofencing</span>
                <span class="tech-tag">RAG Chatbot</span>
                <span class="tech-tag">Selenium</span>
                <span class="tech-tag">SMTP</span>
                <span class="tech-tag">Langchain</span>
                <span class="tech-tag">ChromaDB</span>                
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Team Section
st.markdown('<h2 class="section-header">👥 Team Members</h2>', unsafe_allow_html=True)

team_members = [
    "Banday, Krisel",
    "Bañares, Peter",
    "Muñoz, Carl Johannes",
    "Pili, Van Alejandrey",
    "Yonzon, Raven Kae"
]

cols = st.columns(2)
for idx, member in enumerate(team_members):
    with cols[idx % 2]:
        st.markdown(f'<div class="team-member">👨‍💻 {member}</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 2rem 0; margin-top: 3rem;">
        <p style="font-size: 0.9rem;">🌍 GeoS - Making communities safer through technology</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">Built with ❤️ using Streamlit</p>
    </div>
""", unsafe_allow_html=True)