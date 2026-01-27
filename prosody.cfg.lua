-- Prosody Configuration for Testing (No SSL/TLS)

admins = { "admin@localhost" }

-- Disable TLS completely
c2s_require_encryption = false
s2s_require_encryption = false
s2s_secure_auth = false

-- CRITICAL: Allow plaintext authentication
allow_unencrypted_plain_auth = true

-- Enable in-band registration (auto-register users)
allow_registration = true

-- Modules
modules_enabled = {
    "roster";
    "saslauth";
    "dialback";
    "disco";
    "posix";
    "register";
    "ping";
    "time";
    "uptime";
    "version";
}

modules_disabled = {
    "tls";
}

-- Use plaintext authentication
authentication = "internal_plain"

-- Registration settings
registration_open = true
min_seconds_between_registrations = 0

-- SASL mechanisms - explicitly enable PLAIN
sasl_mechanisms = { "PLAIN" }

log = {
    info = "*console";
}

-- Empty ssl config to prevent certificate loading
ssl = {}

VirtualHost "localhost"
    enabled = true
    ssl = {}
    allow_registration = true
    authentication = "internal_plain"
    c2s_require_encryption = false
    allow_unencrypted_plain_auth = true

Component "conference.localhost" "muc"
    ssl = {}
