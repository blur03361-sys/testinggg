FROM php:8.2-apache
COPY gw.php /var/www/html/gw.php
COPY gw.php /var/www/html/index.php
EXPOSE 80
