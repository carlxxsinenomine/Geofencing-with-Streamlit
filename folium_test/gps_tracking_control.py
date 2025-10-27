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
                        var lat = position.coords.latitude;
                        var lng = position.coords.longitude;
                        var accuracy = position.coords.accuracy;

                        if (locationMarker_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(locationMarker_{{ this.get_name() }});
                        }
                        if (accuracyCircle_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(accuracyCircle_{{ this.get_name() }});
                        }

                        locationMarker_{{ this.get_name() }} = L.marker([lat, lng], {
                            icon: L.divIcon({
                                className: 'custom-location-marker',
                                html: '<div style="background-color: #2A93EE; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>',
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            })
                        }).addTo({{ this._parent.get_name() }});

                        accuracyCircle_{{ this.get_name() }} = L.circle([lat, lng], {
                            radius: accuracy,
                            color: '#136AEC',
                            fillColor: '#2A93EE',
                            fillOpacity: 0.15,
                            weight: 2
                        }).addTo({{ this._parent.get_name() }});

                        pathCoordinates_{{ this.get_name() }}.push([lat, lng]);

                        if (pathLine_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                        }
                        if (pathCoordinates_{{ this.get_name() }}.length > 1) {
                            pathLine_{{ this.get_name() }} = L.polyline(pathCoordinates_{{ this.get_name() }}, {
                                color: 'blue',
                                weight: 3,
                                opacity: 0.7
                            }).addTo({{ this._parent.get_name() }});
                        }

                        {{ this._parent.get_name() }}.setView([lat, lng], {{ this._parent.get_name() }}.getZoom());

                        document.getElementById('coordinates_{{ this.get_name() }}').innerHTML = 
                            'Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + 
                            '<br>Accuracy: ±' + accuracy.toFixed(0) + 'm';
                    },
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
                    navigator.geolocation.clearWatch(watchId_{{ this.get_name() }});
                    watchId_{{ this.get_name() }} = null;
                }
                isTracking_{{ this.get_name() }} = false;
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
            function toggleTracking_{{ this.get_name() }}() {
                if (isTracking_{{ this.get_name() }}) {
                    stopTracking_{{ this.get_name() }}();
                } else {
                    startTracking_{{ this.get_name() }}();
                }
            }

            // Styling for GPSControl on the map
            var GPSControl_{{ this.get_name() }} = L.Control.extend({
                options: {
                    position: 'bottomleft'
                },
                onAdd: function(map) {
                    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                    container.style.background = 'white';
                    container.style.padding = '10px';
                    container.style.borderRadius = '5px';
                    container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';

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

                    L.DomEvent.disableClickPropagation(container);
                    return container;
                }
            });

            {{ this._parent.get_name() }}.addControl(new GPSControl_{{ this.get_name() }}());
        {% endmacro %}
    """)

    def __init__(self):
        # Calls the parent class and passed GPSTrackingControl as argument(the Element)
        super(GPSTrackingControl, self).__init__()
        self._name = 'GPSTrackingControl' # This gets called when using this.get_name(); I'm assuming this is a field of the parent class
