FROM python:2-alpine
MAINTAINER Sherab Sangpo Dorje "po@poism.com"

RUN apk add --no-cache coreutils file imagemagick bash pngcrush optipng

COPY ./ /opt/poism/app

WORKDIR /opt/poism/app

#ENTRYPOINT ["/bin/sh"]
#CMD ["/bin/sh"]
