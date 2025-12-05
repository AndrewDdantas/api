# 🔒 Configurar HTTPS com Let's Encrypt

## Pré-requisitos

✅ Domínio apontando para o servidor Lightsail (já feito)
✅ Nginx instalado e funcionando (já feito)
✅ API rodando corretamente (já feito)

**Seu domínio:** `api-sst.bg-eng-treinamentos.com.br`
**IP do servidor:** `200.225.235.218`

---

## Passo 1: Verificar DNS

Antes de configurar SSL, confirme que o DNS está propagado:

```bash
# Do seu computador
nslookup api-sst.bg-eng-treinamentos.com.br

# Ou
ping api-sst.bg-eng-treinamentos.com.br
```

Deve retornar: `200.225.235.218`

---

## Passo 2: Instalar Certbot

No servidor Lightsail:

```bash
ssh ubuntu@200.225.235.218

# Atualizar sistema
sudo apt update

# Instalar Certbot e plugin do Nginx
sudo apt install -y certbot python3-certbot-nginx

# Verificar instalação
certbot --version
```

---

## Passo 3: Configurar Nginx com Domínio

Antes de rodar o Certbot, precisamos configurar o `server_name` no nginx:

```bash
# Editar configuração
sudo nano /etc/nginx/sites-available/sst-api
```

**Alterar a linha 2 de:**
```nginx
server_name _;
```

**Para:**
```nginx
server_name api-sst.bg-eng-treinamentos.com.br;
```

**Configuração completa deve ficar assim:**

```nginx
server {
    listen 80;
    server_name api-sst.bg-eng-treinamentos.com.br;

    client_max_body_size 20M;

    # Logs
    access_log /var/log/nginx/sst-api-access.log;
    error_log /var/log/nginx/sst-api-error.log;

    # Responder OPTIONS (preflight) rapidamente
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    # Proxy para a API
    location / {
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        add_header 'Access-Control-Max-Age' '3600' always;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Upload de fotos
    location /uploads/ {
        alias /home/ubuntu/api/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable" always;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Testar configuração
sudo nginx -t

# Se OK, recarregar
sudo systemctl reload nginx
```

---

## Passo 4: Obter Certificado SSL

Agora sim, rodar o Certbot:

```bash
sudo certbot --nginx -d api-sst.bg-eng-treinamentos.com.br
```

**O Certbot vai perguntar:**

1. **Email:** Informe um email válido para avisos de expiração
2. **Termos de serviço:** Digite `Y` para aceitar
3. **Compartilhar email com EFF:** Digite `N` (opcional)
4. **Redirect HTTP para HTTPS:** Digite `2` para redirecionar automaticamente

**Saída esperada:**
```
Congratulations! You have successfully enabled HTTPS on 
https://api-sst.bg-eng-treinamentos.com.br

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/api-sst.bg-eng-treinamentos.com.br/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/api-sst.bg-eng-treinamentos.com.br/privkey.pem
   Your certificate will expire on 2025-03-05. To obtain a new or
   tweaked version of this certificate in the future, simply run
   certbot again with the "certonly" option. To non-interactively
   renew *all* of your certificates, run "certbot renew"
```

---

## Passo 5: Verificar HTTPS

```bash
# Verificar configuração do Nginx (Certbot modificou automaticamente)
sudo cat /etc/nginx/sites-available/sst-api

# Recarregar Nginx
sudo systemctl reload nginx

# Testar certificado
curl https://api-sst.bg-eng-treinamentos.com.br/health
```

**Do seu computador:**
```bash
# Testar HTTPS
curl https://api-sst.bg-eng-treinamentos.com.br/health

# Abrir no navegador
https://api-sst.bg-eng-treinamentos.com.br/docs
```

---

## Passo 6: Renovação Automática

O Certbot já configura renovação automática. Verificar:

```bash
# Ver timer de renovação
sudo systemctl status certbot.timer

# Testar renovação (dry-run, não renova de verdade)
sudo certbot renew --dry-run
```

Se o teste der OK, a renovação automática está funcionando! 🎉

---

## 🔥 Firewall (Lightsail)

**IMPORTANTE:** Certifique-se que a porta 443 está aberta no Lightsail:

1. Acesse o console do Lightsail
2. Vá em sua instância
3. Clique na aba **Networking**
4. Em **Firewall**, adicione regra:
   - **Application:** HTTPS
   - **Protocol:** TCP
   - **Port:** 443
   - Clicar em **Add rule**

---

## Configuração Final do Nginx (Após Certbot)

O Certbot vai modificar automaticamente o nginx.conf. A configuração final ficará assim:

```nginx
# HTTP - Redireciona para HTTPS
server {
    listen 80;
    server_name api-sst.bg-eng-treinamentos.com.br;
    
    # Certbot validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirecionar tudo para HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name api-sst.bg-eng-treinamentos.com.br;

    # Certificados SSL (adicionados pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/api-sst.bg-eng-treinamentos.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api-sst.bg-eng-treinamentos.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 20M;

    # Logs
    access_log /var/log/nginx/sst-api-access.log;
    error_log /var/log/nginx/sst-api-error.log;

    # Responder OPTIONS (preflight) rapidamente
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    # Proxy para a API
    location / {
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        add_header 'Access-Control-Max-Age' '3600' always;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Upload de fotos
    location /uploads/ {
        alias /home/ubuntu/api/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable" always;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

---

## 🐛 Troubleshooting

### Erro: "Failed authorization procedure"

**Causa:** DNS não está apontando corretamente ou porta 80 não está acessível.

**Solução:**
```bash
# Verificar se porta 80 está aberta
sudo netstat -tulpn | grep :80

# Verificar DNS
nslookup api-sst.bg-eng-treinamentos.com.br

# Verificar se Nginx está respondendo
curl http://api-sst.bg-eng-treinamentos.com.br/health
```

### Erro: "Certificate expired"

**Solução:**
```bash
# Forçar renovação
sudo certbot renew --force-renewal

# Recarregar Nginx
sudo systemctl reload nginx
```

### Erro: "Too many certificates"

**Causa:** Let's Encrypt tem limite de 5 certificados por semana por domínio.

**Solução:** Aguardar 1 semana ou usar subdomínio diferente.

### Verificar logs do Certbot

```bash
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

---

## ✅ Checklist Final

Após configurar HTTPS, verificar:

```bash
# 1. Certificado válido
curl -I https://api-sst.bg-eng-treinamentos.com.br/health

# 2. HTTP redireciona para HTTPS
curl -I http://api-sst.bg-eng-treinamentos.com.br/health

# 3. API funcionando
curl https://api-sst.bg-eng-treinamentos.com.br/api/v1/auth/login

# 4. Swagger acessível
# Abrir no navegador: https://api-sst.bg-eng-treinamentos.com.br/docs

# 5. Timer de renovação ativo
sudo systemctl status certbot.timer
```

---

## 📝 Resumo dos Comandos

```bash
# SSH no servidor
ssh ubuntu@200.225.235.218

# Instalar Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Editar nginx para adicionar server_name
sudo nano /etc/nginx/sites-available/sst-api
# Mudar: server_name api-sst.bg-eng-treinamentos.com.br;

# Testar e recarregar nginx
sudo nginx -t
sudo systemctl reload nginx

# Obter certificado SSL
sudo certbot --nginx -d api-sst.bg-eng-treinamentos.com.br

# Verificar
curl https://api-sst.bg-eng-treinamentos.com.br/health
```

**🎉 Pronto! Sua API agora tem HTTPS!**
