import streamlit as st
import streamlit.components.v1 as components

mermaid_chart = """
<div class="mermaid">
graph LR
    A[User Accesses the Application] --> B{Assess Area Risk};
    B --> C[Analyze Flood Likelihood];
    B --> D[Analyze Landslide Likelihood];
    B --> E[Analyze Storm Surge Likelihood];
    C --> F{Determine Risk Level};
    D --> F;
    E --> F;
    F --> |High Risk|G[Create GeoFence Boundary];
    F --> |Low Risk|H[Mark as Safe Zone];
    G --> I{Monitor Conditions};
    I --> |Threshold Met|J[Activate GeoFence Alert];
    I --> |Normal |K[Continue Monitoring];
    J --> L[Alert Individuals in Zone];
    L --> M[Send Evacuation Notice];
    M --> N[Direct user to the nearest Safe Zone];
    H --> O[Log Safe Zone Data];
    K --> I;
    N --> P[Generate Response Analytics];
    style A fill:#339999,color:#fff
    style B fill:#770737,color:#fff
    style C fill:#C63287,color:#fff
    style D fill:#C63287,color:#fff
    style E fill:#C63287,color:#fff
    style F fill:#770737,color:#fff
    style H fill:#7b529c,color:#fff
    style O fill:#7b529c,color:#fff
    style G fill:#990000,color:#fff
    style I fill:#770737,color:#fff
    style J fill:#990000,color:#fff
    style L fill:#d08c60,color:#fff
    style M fill:#d08c60,color:#fff
    style N fill:#7b529c,color:#fff
    style P fill:#FF0000,color:#fff
    style K fill:#006600,color:#fff
</div>

<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>
"""

st.markdown(
    """
    # GeoS: Enhancing Disaster Preparedness through Weather Data Analysis and Proactive Geofencing

    ## Proponents

    **Course:** *Bachelor of Science in Computer Science - 2A*

    **Team Members:**
    - Banday, Krisel
    - Bañares, Peter
    - Muñoz, Carl Johannes
    - Pili, Van Alejandrey
    - Yonzon, Raven Kae

    ---

    ## Target Problem

    **Preparedness**  

    The Philippines experiences an average of 20 tropical cyclones (typhoons) entering the Philippine Area of Responsibility (PAR) annually (PAGASA, n.d.). This results in further natural-hazardous incidents including a total of 225 floods and landslides in 2024 alone according to Philippine Statistics Authority (PSA) (Component | Philippine Statistics Authority | Republic of the Philippines, n.d.). Despite initial measurements, preparedness for an informed disaster risk management is still poorly implemented due to its systemic lack and differences. Residents struggle to find valid data due to the lack of a credible information source caused by the spread of unverified information on social media and the existence of multiple, conflicting official sources.  These gaps between disaster management have caused housing destruction, livelihood changes, and lives, contributing to the devastating consequences of disastrous events.

    ## Existing Software Solutions

    **SnapFlood**: is a real-time flood monitoring and detection system that measures flood level, flow rate, and rainfall using a variety of sensors and image processing. The results are shown via an Android app. Accurate, affordable, solar-powered monitoring for rural areas is its primary strength. However, its inability to map geographically and forecast floods restricts its ability to predict disasters more broadly. *(Lean Karlo S. Tolentino et al., 2022)*

    **Distributed Flood Monitoring System**: This software uses a distributed microservice architecture with RabbitMQ and MongoDB to collect and visualize real-time rainfall, river level, and flood history data in order to monitor floods. Scalability and the modular integration of various data sources are its key advantages. However, its capacity to deliver early, localized warnings for communities at risk is limited due to its lack of image-based flood detection and real-time predictive analytics. *(Roberto Luiz Debarba, 2020)*

    **Geofencing for Disaster Management System**: By using geofencing technology, this Android-based system warns users when they enter restricted or disaster-prone areas and gives them timely notifications and directions to nearby relief areas. Real-time, location-aware safety alerts are its primary advantage. Its applicability for offline emergency situations and early warning is limited, though, by its heavy reliance on internet connectivity and lack of weather or disaster prediction capabilities. *(Anish Deshpande et al., 2019)*

    ## Proposed Solution

    ### Core Features

    **1. Geofencing Alert System**

    With Geofencing, the system can establish virtual fences around specific areas and designate them as either high-risk zones or safe zones. When a natural disaster occurs or is imminent, alert notifications are automatically sent to all individuals within the Geofences, informing them of their current location's risk status and directing them to the nearest safe zone. This proactive approach provides users with adequate time to prepare and evacuate safely.

    **2. Intensity-Based GeoFence Activation**

    The activation of a Geofence is determined by the intensity level of a disaster. For example, if a particular area within a Geofence consistently experiences flooding at the orange rainfall warning category, the system can be configured to activate that specific fence only when the disaster intensity reaches or exceeds the orange rainfall category threshold. This ensures that alerts are precise and relevant to the actual threat level.

    **3. Automated GeoFence Deployment Using AI/ML**

    By analyzing rainfall warning datasets specific to the Philippines, the proposed system employs artificial intelligence and machine learning algorithms to automate the deployment of geofences. The system dynamically establishes and adjusts virtual boundaries around high-risk areas using real-time weather data. This automation reduces the need for manual setup, enhances the precision of risk assessment, and improves the responsiveness of early warning systems by enabling faster, data-driven disaster alerts and evacuation notifications.

    ## II. Flowchart using Mermaid:
    """
)

components.html(mermaid_chart)

st.markdown(
    """
    ## Overview:

    This GIS-based disaster warning system workflow begins when the user opens the application which automatically captures their location through GPS(Global Positioning System). Afterward, a comprehensive risk assessment is then taken into consideration in simultaneously analyzing three critical and natural hazards specifically; Flash Floods, Landslides, and Storm Surges based from informations gathered from various agencies that tackles area terrains, elevations and even past disaster records and immediately creates a virtual boundary called GeoFences that determines whether an area is within a Safe zone or not. After the risk assessment , the system then evaluates the severity a user could possibly be in. If the condition is high-risk the system automatically activates the GeoFence Alert that sends notifications to all the users that are in the said conditions and directly sends them exact locations for the nearest evacuation/safe zone . And if the user is not within the danger zone, the system simply marks it as a safe zone and will not be sending unnecessary alarms and will continue to monitor if ever the user steps into a marked danger zone. Finally, reports are created using a User response-based analytics that shows how well the system works, and ensures accuracy of other important data that may help improve the system.

    ## Application of Data Structure

    **Graph**: this data structure will be used to represent spatial relationships between zones, roads, and evacuation routes. By modeling these connections using nodes and edges,the system can identify areas that are at risk, and the routes that are safe.

    **Array**: this data structure will be used to store sequential data streams regarding the weather. These arrays enable efficient trend analysis and threshold detection, which the system uses to automatically activate or adjust GeoFences.

    **Maps (dictionary)**: this data structure will store each GeoFence and link it with its corresponding attributes—such as location, alert level, risk intensity, and list of affected users. 

    ## References 

    1. PAGASA. (n.d.). https://www.pagasa.dost.gov.ph/climate/tropical-cyclone-information

    2. Component | Philippine Statistics Authority | Republic of the Philippines. (n.d.). https://psa.gov.ph/statistics/environment-statistics/highlights/component-4-extreme-events-and-disaster

    3. Tolentino, L. K. S., et al. (2022, July). *Real Time Flood Detection, Alarm and Monitoring System    Using Image Processing and Multiple Linear Regression. Journal of Computational Innovations and Engineering Applications*. De La Salle University. https://www.dlsu.edu.ph/wp-content/uploads/pdf/research/journals/jciea/vol-7-1/2tolentino.pdf

    4. Deshpande, A., et al. (2019, May). *Geofencing for Disaster Management System. Journal of Emerging Technologies and Innovative Research (JETIR)*. https://www.jetir.org/view?paper=JETIRCS06006

    5. Debarba, R. L. (2020). *Distributed Flood Monitoring System [Source code]*. GitHub. https://github.com/RobertoDebarba/distributed-flood-monitoring-system
    """
)