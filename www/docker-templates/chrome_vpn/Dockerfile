FROM kasmweb/chrome:1.14.0

USER root
COPY custom_startup.sh /dockerstartup/custom_startup.sh
COPY extensions.json /etc/opt/chrome/policies/managed/extensions.json
RUN chmod +x /dockerstartup/custom_startup.sh
USER kasm-user
