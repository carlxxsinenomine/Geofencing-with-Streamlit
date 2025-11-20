from branca.element import MacroElement, Template

class GPSTrackingControl(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
        
            // Load Turf.js library from CDN
            var turfLoaded_{{ this.get_name() }} = false;
            var turfScript_{{ this.get_name() }} = document.createElement('script');
            turfScript_{{ this.get_name() }}.src = "https://cdn.jsdelivr.net/npm/@turf/turf@7/turf.min.js";
            turfScript_{{ this.get_name() }}.onload = function() {
                console.log('Turf.js loaded successfully');
                turfLoaded_{{ this.get_name() }} = true;
            };
            document.head.appendChild(turfScript_{{ this.get_name() }});
            
            // Blue dot on maps
            var locationMarker_{{ this.get_name() }} = null;
            // Circle showing accuracy
            var accuracyCircle_{{ this.get_name() }} = null;
            // Blue line showing user path
            var pathLine_{{ this.get_name() }} = null;
            // Array of user locations
            var pathCoordinates_{{ this.get_name() }} = [];
            // To check is GPS is currently running
            var isTracking_{{ this.get_name() }} = false;
            // ID to stop GPS tracking
            var watchId_{{ this.get_name() }} = null;
            
            var drawnShapes_{{ this.get_name() }} = null;
            var isThereFences_{{ this.get_name() }} = false;
            
            {% if this.drawn_shapes %}
            drawnShapes_{{ this.get_name() }} = {{ this.drawn_shapes | tojson }};
            isThereFences_{{ this.get_name() }} = true;
            {% endif %}
            
            function isPointInsideCircle_{{ this.get_name() }}(userCoordinates, shapeCoordinates, shapeRadius) {
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
            }
            
            function isPointInPolygon_{{ this.get_name() }}(userLat, userLng, polygonCoordinates) {
                if (!turfLoaded_{{ this.get_name() }} || typeof turf === 'undefined') {
                        console.log("Turf.js not loaded yet");
                        return false;
                    }
                
                var userCoordinates = turf.point([userLng, userLat]);
                
                if (polygonCoordinates[0][0] !== polygonCoordinates[polygonCoordinates.length - 1][0] ||
                    polygonCoordinates[0][1] !== polygonCoordinates[polygonCoordinates.length - 1][1]) {
                    polygonCoordinates.push(polygonCoordinates[0]);
                }
                
                // Create polygon
                var polygon = turf.polygon([polygonCoordinates]);
                
                // Check if point is inside polygon
                var isInside = turf.booleanPointInPolygon(userCoordinates, polygon);
                                
                return isInside;
            }
            
            function isPointInsideGeofence_{{ this.get_name() }}(userLng, userLat) {
                if (!isThereFences_{{ this.get_name() }} || !drawnShapes_{{ this.get_name() }}) {
                    return false;
                }
                
                var userLat = parseFloat(userLat);
                var userLng = parseFloat(userLng);
                
                for(var i = 0; i < drawnShapes_{{ this.get_name() }}.length; i++) {
                    var shape = drawnShapes_{{ this.get_name() }}[i];
                    var geometry = shape.geometry;
                    var properties = shape.properties || {};
                    
                    if (!geometry) continue;
                    
                    var isInside = false;
                    
                    switch(geometry.type) {
                        case 'Point':
                            var centerLng = geometry.coordinates[0];
                            var centerLat = geometry.coordinates[1];
                            var radius = properties.radius || 0;
                            var isActive = properties.is_active || false;
                            
                            if (radius > 0 && isActive) {
                                isInside = isPointInsideCircle_{{ this.get_name() }}(
                                    [userLat, userLng], 
                                    [centerLng, centerLat], 
                                    radius
                                );
                            }
                            break;
                            
                        case 'Polygon':
                            var coordinates = geometry.coordinates[0]; // First ring (exterior)
                            var isActive = properties.is_active || false;
                            if(isActive) {
                                isInside = isPointInPolygon_{{ this.get_name() }}(userLat, userLng, coordinates);
                            }
                            break;
                    }
                    if (isInside) {
                        console.log('Point is inside fence:', properties.name || 'Unnamed fence');
                        return true;
                    }
                }
                
                return false;
            }
            
            function sendDataToServer_{{ this.get_name() }}() {
                // Send data to API
                fetch('http://localhost:5000/save-tracking', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type: "Feature",
                        properties: {
                            "timestamp": new Date().toISOString(),
                            "user_id": '{{ this.user_id }}'  // Pass from Python
                        },
                        geometry: {
                            type: "LineString",
                            coordinates: [pathCoordinates_{{ this.get_name() }}]
                        } 
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Tracking data saved:', data);
                    alert('Tracking data saved successfully!');
                })
                .catch(error => {
                    console.error('Error saving tracking data:', error);
                    alert('Error saving tracking data');
                });
            }
            
            // When the user toggled the START GPS button this gets called
            function startTracking_{{ this.get_name() }}() {
                // Check if supported ba ng browser
                if (!navigator.geolocation) {
                    alert('Geolocation is not supported by your browser');
                    return;
                }
                
                // If supported
                // Set isTracking_{{ this.get_name() }} to True
                // this = the current class; this.get_name() gets the name specified in the constructor(__init__)
                isTracking_{{ this.get_name() }} = true;
                // Change the value of the element and its styling
                document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '🟢 Tracking Active';
                document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'green';

                // This is where the tracking happens
                // Some useful link(might study indepth): https://www.geeksforgeeks.org/html/html-geolocation-watchposition-method/
                watchId_{{ this.get_name() }} = navigator.geolocation.watchPosition(
                    // Params of the watchPosition explained
                    // Like setInterval() but for GPS
                    // navigator.geolocation.watchPosition(
                        // successCallback,  // Called repeatedly when location updates
                        // errorCallback,    // Called if something goes wrong
                        // options           // Settings for GPS accuracy/timing
                    // );
                    function(position) { // Success Callback
                        // Get the lat, long, and accuracy in meters
                        var lat = position.coords.latitude;
                        var lng = position.coords.longitude;
                        var accuracy = position.coords.accuracy;
                        
                        var isInsideFence = isPointInsideGeofence_{{ this.get_name() }}(lng, lat);
    
                        if (isInsideFence) {
                            alert("user inside fence");
                            fetch('http://localhost:5000/log-alert-event', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    userId: 090,
                                    timestamp: new Date().toISOString(),
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log('Event data saved:', data);
                                alert('Event data saved successfully!');
                            })
                            .catch(error => {
                                console.error('Error saving tracking data:', error);
                                alert('Error saving event data');
                            });
                        }
                        
                        
                        // Removes marker everytime the user coordinates updated
                        // So that there is only one marker that moves
                        // this._parent = The maps that contains this control; the current folium maps instance
                        // When you create the maps in Python; m = folium.Map(zoom_start=12)
                        // Internally, Folium assigns it a unique JavaScript variable name like; var map_abc123 = L.maps(...);
                        if (locationMarker_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(locationMarker_{{ this.get_name() }});
                        }
                        if (accuracyCircle_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(accuracyCircle_{{ this.get_name() }});
                        }

                        locationMarker_{{ this.get_name() }} = L.marker([lat, lng], { // Creates a leaflet marker at user coordinates
                            icon: L.divIcon({ // Custom icon
                                className: 'custom-location-marker',
                                html: '<div style="background-color: #2A93EE;width: 16px; height: 16px; border-radius: 50%; border: 3px solid white;box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>',
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            })
                        }).addTo({{ this._parent.get_name() }}); // Add to the maps; the m instance created in python

                        // This one's for the accuracy circle
                        accuracyCircle_{{ this.get_name() }} = L.circle([lat, lng], {
                            radius: accuracy,
                            color: '#136AEC',
                            fillColor: '#2A93EE',
                            fillOpacity: 0.15,
                            weight: 2
                        }).addTo({{ this._parent.get_name() }}); // Same as before, add to maps

                        // Store user coordinate in array; gagamitin for trailing or pathLine
                        pathCoordinates_{{ this.get_name() }}.push([lat, lng]);
                        // Remove old point layers from maps
                        // Then redraw kasama nung old points to create a trail or path
                        if (pathLine_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                        }
                        if (pathCoordinates_{{ this.get_name() }}.length > 1) { // Meaning there are multiple points
                            pathLine_{{ this.get_name() }} = L.polyline(pathCoordinates_{{ this.get_name() }}, { // Create a polyline layer on the maps, pass the pathCoordinate array
                                color: 'blue', // Color of trail or pathLine
                                weight: 3, // Weight HAHAHAH
                                opacity: 0.7 // Opacity
                            }).addTo({{ this._parent.get_name() }}); // Add layer to maps
                        }
                        
                        // Move maps to center on user position
                        // getZoom Keeps current zoom level
                        {{ this._parent.get_name() }}.setView([lat, lng], {{ this._parent.get_name() }}.getZoom());
                        
                        // Information of user's coordinate
                        document.getElementById('coordinates_{{ this.get_name() }}').innerHTML = 
                            'Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + 
                            '<br>Accuracy: ±' + accuracy.toFixed(0) + 'm';
                    },
                    // This gets called if:
                        // User denies location permission
                        // GPS signal lost
                        // GPS disabled on device malamang tangina
                        // Or timeout takes longer than 5 seconds as specified in the options parameter
                    function(error) { // Error Callback
                        sendDataToServer_{{ this.get_name() }}();
                        console.error('Error getting location:', error);
                        document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '❌ Error: ' + error.message;
                        document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'red';
                    },
                    { // Options
                        enableHighAccuracy: true,
                        maximumAge: 0,
                        timeout: 5000
                    }
                );
            }
            
            // This gets called when the user toggled stop tracking
            function stopTracking_{{ this.get_name() }}() {
                if (watchId_{{ this.get_name() }} !== null) {
                    // clearWatch() stops GPS updates
                    navigator.geolocation.clearWatch(watchId_{{ this.get_name() }});
                    watchId_{{ this.get_name() }} = null; // Set to null
                }
                
                if (locationMarker_{{ this.get_name() }} !== null) {
                    {{ this._parent.get_name() }}.removeLayer(locationMarker_{{ this.get_name() }});
                }
                
                if (accuracyCircle_{{ this.get_name() }} !== null) {
                    {{ this._parent.get_name() }}.removeLayer(accuracyCircle_{{ this.get_name() }});
                }
    
                isTracking_{{ this.get_name() }} = false;
                
                sendDataToServer_{{ this.get_name() }}();
                
                // Update UI
                document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '🔴 Tracking Stopped';
                document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'red';
            }

            // This is for clearing the trail of the user
            function clearPath_{{ this.get_name() }}() {
                if (pathLine_{{ this.get_name() }}) {
                    {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                    pathLine_{{ this.get_name() }} = null;
                }
                pathCoordinates_{{ this.get_name() }} = [];
            }

            // For the toggle button
            // This gets called when Start and Stop GPS button is pressed
            function toggleTracking_{{ this.get_name() }}() {
                if (isTracking_{{ this.get_name() }}) {
                    stopTracking_{{ this.get_name() }}();
                } else {
                    startTracking_{{ this.get_name() }}();
                }
            }

            // For creating the leaflet control (the buttons)
            // L.Control.extend() is leaflet's way to create a custom maps controls
            var GPSControl_{{ this.get_name() }} = L.Control.extend({
                options: {
                    position: 'bottomleft' // Where to place on maps
                },
                onAdd: function(maps) { // Function to create the UI
                    // L.DomUtil.create('div', ...) Creates a <div> element
                    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                    // Styling of the container
                    container.style.background = 'white';
                    container.style.padding = '10px';
                    container.style.borderRadius = '5px';
                    container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
                    // Add buttons and display elements
                    container.innerHTML = `
                        <div style="margin-bottom: 5px;">
                            <button onclick="toggleTracking_{{ this.get_name() }}()" 
                                    style="padding: 8px 15px; cursor: pointer; background: #2A93EE; color: white; border: none; border-radius: 3px; font-weight: bold;">
                                Start/Stop GPS
                            </button>
                            <button onclick="clearPath_{{ this.get_name() }}()" 
                                    style="padding: 8px 15px; cursor: pointer; background: #FF6B6B; color: white; border: none; border-radius: 3px; margin-left: 5px;">
                                Clear Path
                            </button>
                        </div>
                        <div id="trackingStatus_{{ this.get_name() }}" style="font-weight: bold; margin-top: 5px;">⚪ Not Tracking</div>
                        <div id="coordinates_{{ this.get_name() }}" style="font-size: 12px; margin-top: 5px; color: #666;"></div>
                    `;
                    // Without this clicking buttons would also click the maps behind them
                    L.DomEvent.disableClickPropagation(container);
                    return container;
                }
            });
            // Creates instance of the control then adds it to the maps
            {{ this._parent.get_name() }}.addControl(new GPSControl_{{ this.get_name() }}());
        {% endmacro %}
    """)

    def __init__(self, state):
        # Calls the parent class and passed GPSTrackingControl as argument(the Element)
        super(GPSTrackingControl, self).__init__()
        self._name = 'GPSTrackingControl' # This gets called when using this.get_name(); I'm assuming this is a field of the parent class
        self._state_len = len(state)
        self.drawn_shapes = state or []
        self.user_id = None
