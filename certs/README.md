# SSL Certificates Directory

This directory should contain your SSL certificates for HTTPS deployment.

## Required Files for HTTPS:
- `cert.pem` - Your SSL certificate
- `key.pem` - Your private key

## Self-Signed Certificates for Testing:

You can generate self-signed certificates for testing purposes:

```bash
# Generate a self-signed certificate (for testing only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Production Certificates:

For production, obtain certificates from a trusted Certificate Authority (CA) like:
- Let's Encrypt (free)
- DigiCert
- Comodo
- GlobalSign

## Let's Encrypt with Certbot:

If using Let's Encrypt, you can use certbot to automatically obtain and renew certificates:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Obtain certificate (replace yourdomain.com)
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com

# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
# Copy them to this directory:
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./key.pem
```

## Security Notes:

1. **Never commit certificate files to version control**
2. Set proper file permissions: `chmod 600 *.pem`
3. Keep private keys secure and backed up
4. Monitor certificate expiration dates
5. Use strong encryption (RSA 2048+ bits or ECDSA)

## Docker Volume:

The certificates in this directory are mounted as read-only volumes in the Nginx container:
```yaml
volumes:
  - ./certs:/etc/nginx/certs:ro
```
