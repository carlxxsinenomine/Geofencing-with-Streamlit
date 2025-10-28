from branca.element import MacroElement, Template

class GPSTrackingControl(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
            // Blue dot on map
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
                        
                        // Removes marker everytime the user coordinates updated
                        // So that there is only one marker that moves
                        // this._parent = The map that contains this control; the current folium map instance
                        // When you create the map in Python; m = folium.Map(zoom_start=12)
                        // Internally, Folium assigns it a unique JavaScript variable name like; var map_abc123 = L.map(...);
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
                        }).addTo({{ this._parent.get_name() }}); // Add to the map; the m instance created in python

                        // This one's for the accuracy circle
                        accuracyCircle_{{ this.get_name() }} = L.circle([lat, lng], {
                            radius: accuracy,
                            color: '#136AEC',
                            fillColor: '#2A93EE',
                            fillOpacity: 0.15,
                            weight: 2
                        }).addTo({{ this._parent.get_name() }}); // Same as before, add to map

                        // Store user coordinate in array; gagamitin for trailing or pathLine
                        pathCoordinates_{{ this.get_name() }}.push([lat, lng]);
                        // Remove old point layers from map
                        // Then redraw kasama nung old points to create a trail or path
                        if (pathLine_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                        }
                        if (pathCoordinates_{{ this.get_name() }}.length > 1) { // Meaning there are multiple points
                            pathLine_{{ this.get_name() }} = L.polyline(pathCoordinates_{{ this.get_name() }}, { // Create a polyline layer on the map, pass the pathCoordinate array
                                color: 'blue', // Color of trail or pathLine
                                weight: 3, // Weight HAHAHAH
                                opacity: 0.7 // Opacity
                            }).addTo({{ this._parent.get_name() }}); // Add layer to map
                        }
                        
                        // Move map to center on user position
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
    
                isTracking_{{ this.get_name() }} = false;
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
            // L.Control.extend() is leaflet's way to create a custom map controls
            var GPSControl_{{ this.get_name() }} = L.Control.extend({
                options: {
                    position: 'bottomleft' // Where to place on map
                },
                onAdd: function(map) { // Function to create the UI
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
                    // Without this clicking buttons would also click the map behind them
                    L.DomEvent.disableClickPropagation(container);
                    return container;
                }
            });
            // Creates instance of the control then adds it to the map
            {{ this._parent.get_name() }}.addControl(new GPSControl_{{ this.get_name() }}());
        {% endmacro %}
    """)

    def __init__(self):
        # Calls the parent class and passed GPSTrackingControl as argument(the Element)
        super(GPSTrackingControl, self).__init__()
        self._name = 'GPSTrackingControl' # This gets called when using this.get_name(); I'm assuming this is a field of the parent class
