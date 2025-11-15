FROM nginx:alpine

# Fjern default index.html og 50x.html
RUN rm -f /usr/share/nginx/html/index.html 
RUN rm -f /usr/share/nginx/html/50x.html

# Kopiér vores config
COPY nginx.conf /etc/nginx/conf.d/default.conf
