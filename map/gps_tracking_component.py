import streamlit as st
import streamlit.components.v1 as components


def gps_tracking_component(drawn_shapes=None, height=150):
    """
    A Streamlit component for GPS tracking with geofencing.

    Args:
        drawn_shapes: List of shape dictionaries with geometry and properties
        height: Height of the component in pixels

    Returns:
        Dictionary with trail data when tracking stops, or None
    """

    # Convert drawn_shapes to JSON string for JavaScript
    import json
    shapes_json = json.dumps(drawn_shapes if drawn_shapes else [])

    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/@turf/turf@7/turf.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'Source Sans Pro', sans-serif;
            }}
            .control-container {{
                background: black;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            }}
            .button-group {{
                margin-bottom: 5px;
            }}
            button {{
                padding: 8px 15px;
                cursor: pointer;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 5px;
            }}
            .btn-primary {{
                background: #2A93EE;
                color: white;
            }}
            .btn-danger {{
                background: #FF6B6B;
                color: white;
            }}
            .status {{
                font-weight: bold;
                margin-top: 5px;
            }}
            .coordinates {{
                font-size: 12px;
                margin-top: 5px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="control-container">
            <div class="button-group">
                <button class="btn-primary" onclick="toggleTracking()">Start/Stop GPS</button>
                <button class="btn-danger" onclick="clearPath()">Clear Path</button>
            </div>
            <div id="trackingStatus" class="status">⚪ Not Tracking</div>
            <div id="coordinates" class="coordinates"></div>
        </div>

        <script>
            // GPS tracking variables
            var pathCoordinates = [];
            var isTracking = false;
            var watchId = null;
            var drawnShapes = {shapes_json};
            var isThereFences = drawnShapes.length > 0;
            var turfLoaded = typeof turf !== 'undefined';

            // Wait for Turf.js to load
            if (!turfLoaded) {{
                var checkTurf = setInterval(function() {{
                    if (typeof turf !== 'undefined') {{
                        turfLoaded = true;
                        clearInterval(checkTurf);
                        console.log('Turf.js loaded successfully');
                    }}
                }}, 100);
            }}

            function isPointInsideCircle(userCoordinates, shapeCoordinates, shapeRadius) {{
                var userLat = userCoordinates[0];
                var userLng = userCoordinates[1];
                var shapeLat = shapeCoordinates[1]; 
                var shapeLng = shapeCoordinates[0];

                var R = 6371000; // Earth's radius in meters
                var dLat = (shapeLat - userLat) * Math.PI / 180;
                var dLng = (shapeLng - userLng) * Math.PI / 180;

                var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                        Math.cos(userLat * Math.PI / 180) * Math.cos(shapeLat * Math.PI / 180) *
                        Math.sin(dLng/2) * Math.sin(dLng/2);

                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                var distance = R * c;

                return distance <= shapeRadius;
            }}

            function isPointInPolygon(userLat, userLng, polygonCoordinates) {{
                if (!turfLoaded || typeof turf === 'undefined') {{
                    console.log("Turf.js not loaded yet");
                    return false;
                }}

                var userCoordinates = turf.point([userLng, userLat]);

                if (polygonCoordinates[0][0] !== polygonCoordinates[polygonCoordinates.length - 1][0] ||
                    polygonCoordinates[0][1] !== polygonCoordinates[polygonCoordinates.length - 1][1]) {{
                    polygonCoordinates.push(polygonCoordinates[0]);
                }}

                var polygon = turf.polygon([polygonCoordinates]);
                var isInside = turf.booleanPointInPolygon(userCoordinates, polygon);

                return isInside;
            }}

            function isPointInsideGeofence(userLng, userLat) {{
                if (!isThereFences || !drawnShapes) {{
                    return false;
                }}

                var userLat = parseFloat(userLat);
                var userLng = parseFloat(userLng);

                for(var i = 0; i < drawnShapes.length; i++) {{
                    var shape = drawnShapes[i];
                    var geometry = shape.geometry;
                    var properties = shape.properties || {{}};

                    if (!geometry) continue;

                    var isInside = false;

                    switch(geometry.type) {{
                        case 'Point':
                            var centerLng = geometry.coordinates[0];
                            var centerLat = geometry.coordinates[1];
                            var radius = properties.radius || 0;

                            if (radius > 0) {{
                                isInside = isPointInsideCircle(
                                    [userLat, userLng], 
                                    [centerLng, centerLat], 
                                    radius
                                );
                            }}
                            break;

                        case 'Polygon':
                            var coordinates = geometry.coordinates[0];
                            isInside = isPointInPolygon(userLat, userLng, coordinates);
                            break;
                    }}

                    if (isInside) {{
                        console.log('Point is inside fence:', properties.name || 'Unnamed fence');
                        return true;
                    }}
                }}

                return false;
            }}

            function sendTrailToStreamlit(reason) {{
                if (pathCoordinates.length === 0) {{
                    console.log('No path coordinates to send');
                    return;
                }}

                var data = {{
                    pathCoordinates: pathCoordinates.map(coord => ({{lat: coord[0], lng: coord[1]}})),
                    reason: reason,
                    timestamp: new Date().toISOString(),
                    totalPoints: pathCoordinates.length
                }};

                // Send data back to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: data
                }}, '*');

                console.log('Trail data sent to Streamlit:', data);
            }}

            function startTracking() {{
                if (!navigator.geolocation) {{
                    alert('Geolocation is not supported by your browser');
                    return;
                }}

                isTracking = true;
                document.getElementById('trackingStatus').innerHTML = '🟢 Tracking Active';
                document.getElementById('trackingStatus').style.color = 'green';

                watchId = navigator.geolocation.watchPosition(
                    function(position) {{
                        var lat = position.coords.latitude;
                        var lng = position.coords.longitude;
                        var accuracy = position.coords.accuracy;

                        var isInsideFence = isPointInsideGeofence(lng, lat);

                        if (isInsideFence) {{
                            console.log("User inside fence!");
                        }}

                        pathCoordinates.push([lat, lng]);

                        document.getElementById('coordinates').innerHTML = 
                            'Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + 
                            '<br>Accuracy: ±' + accuracy.toFixed(0) + 'm';
                    }},
                    function(error) {{
                        console.error('Error getting location:', error);
                        document.getElementById('trackingStatus').innerHTML = '❌ Error: ' + error.message;
                        document.getElementById('trackingStatus').style.color = 'red';
                    }},
                    {{
                        enableHighAccuracy: true,
                        maximumAge: 0,
                        timeout: 5000
                    }}
                );
            }}

            function stopTracking() {{
                if (watchId !== null) {{
                    navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                }}

                isTracking = false;
                document.getElementById('trackingStatus').innerHTML = '🔴 Tracking Stopped';
                document.getElementById('trackingStatus').style.color = 'red';

                // Automatically send trail data to Streamlit when stopped
                sendTrailToStreamlit('user_stopped_tracking');
            }}

            function clearPath() {{
                pathCoordinates = [];
                console.log('Path cleared');
            }}

            function toggleTracking() {{
                if (isTracking) {{
                    stopTracking();
                }} else {{
                    startTracking();
                }}
            }}
        </script>
    </body>
    </html>
    """

    # Render the component and return any data it sends back
    component_value = components.html(component_html, height=height)

    return component_value