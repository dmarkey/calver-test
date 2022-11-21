FROM alpine:3.16
RUN apk add --no-cache github-cli python3
COPY release.py /release.py
RUN git config --global --add safe.directory /github/workspace
ENTRYPOINT [ "/release.py" ]

