FROM kasmweb/chrome:1.14.0

USER root
COPY custom_startup.sh /dockerstartup/custom_startup.sh
RUN chmod +x /dockerstartup/custom_startup.sh
# Quitar o comentar la línea siguiente
USER kasm-user
