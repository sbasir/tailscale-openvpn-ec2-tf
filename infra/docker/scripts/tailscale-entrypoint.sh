#!/bin/sh
set -e

apk add busybox-extras
# Wait for interfaces to be available
sleep 10

# Set up iptables rules for forwarding
echo "Setting up iptables rules..."

# Allow forwarding between Tailscale and OpenVPN interfaces
iptables -A FORWARD -i tailscale0 -o tun0 -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -i tun0 -o tailscale0 -j ACCEPT 2>/dev/null || true

# NAT traffic from Tailscale to OpenVPN
# Get Tailscale subnet (usually 100.64.0.0/10)
iptables -t nat -A POSTROUTING -s 100.64.0.0/10 -o tun0 -j MASQUERADE 2>/dev/null || true

# Allow OpenVPN forwarding
iptables -A FORWARD -i tun0 -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -o tun0 -j ACCEPT 2>/dev/null || true

echo "iptables rules set up successfully"

# Start Tailscale daemon
exec tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &

# Wait for daemon to start
sleep 5

# Bring up Tailscale with your configuration
tailscale up --authkey=$TS_AUTH_KEY --hostname=$TS_HOSTNAME $TS_EXTRA_ARGS 

# Keep container running
wait

