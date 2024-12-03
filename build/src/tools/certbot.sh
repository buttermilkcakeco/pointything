docker run -it --rm --name certbot \
            -v `pwd`/letsencrypt:/etc/letsencrypt \
            -v `pwd`/letsencrypt-lib:/var/lib/letsencrypt \
            -v /data/static:/opt/certbot/www \
            certbot/certbot $@
