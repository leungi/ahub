FROM nginx

# configure ssl with self-signed cert and set username/password
RUN apt-get update && \
	apt-get install -y apache2-utils openssl curl && \
	htpasswd -bc /etc/nginx/.htpasswd ahub ilikebigwhales && \
	openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout /etc/nginx/server.key \
		-out /etc/nginx/server.crt && \
	service nginx start
	
# ADD nginx.conf /etc/nginx/