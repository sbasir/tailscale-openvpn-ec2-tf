FROM debian:bookworm-slim

WORKDIR /app

# Install OpenVPN
RUN apt-get update && apt-get install -y openvpn curl telnet && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the OpenVPN config file
COPY config.ovpn /app/config.ovpn

# Create a script to copy config file and start OpenVPN
RUN echo '#!/bin/bash\n\
if [ -f "/app/config.ovpn" ]; then\n\
    openvpn --disable-dco --config /app/config.ovpn\n\
else\n\
    echo "Error: config.ovpn file not found in /app directory"\n\
    exit 1\n\
fi' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]