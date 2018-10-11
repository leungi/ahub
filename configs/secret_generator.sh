#!/bin/bash
htpasswd -bc /configs/.htpasswd ahub ilikebigwhales && \
	openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout /configs/server.key \
		-out /configs/server.crt