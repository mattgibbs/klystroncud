# klystroncud
A continuously updating web-based Klystron display for LCLS.

This is a web-based klystron display for LCLS.  It consists of a python-based backend, and an HTML frontend.  The backend is a Bottle server, and uses the gevent-websockets library to send real-time klystron status information to the frontend.  The frontend listens for klystron updates, and transforms the page to reflect the current status of each klystron.
