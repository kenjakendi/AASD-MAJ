#!/bin/bash
# Prosody initialization script
# Generates self-signed certificates and starts Prosody

set -e

echo "Checking for TLS certificates..."

# Check if certificates already exist
if [ ! -f "/var/lib/prosody/serverhello.crt" ] || [ ! -f "/var/lib/prosody/serverhello.key" ]; then
    echo "Generating self-signed certificates for serverhello..."
    
    # Generate self-signed certificate
    openssl req -new -x509 -days 365 -nodes \
        -out "/var/lib/prosody/serverhello.crt" \
        -newkey rsa:2048 \
        -keyout "/var/lib/prosody/serverhello.key" \
        -subj "/CN=serverhello/O=Animal Shelter MAS/C=PL"
    
    # Set proper permissions
    chown prosody:prosody /var/lib/prosody/serverhello.* 
    chmod 644 /var/lib/prosody/serverhello.crt
    chmod 600 /var/lib/prosody/serverhello.key
    
    echo "Certificates generated successfully."
else
    echo "Certificates already exist."
fi

echo "Starting Prosody..."
exec prosody

