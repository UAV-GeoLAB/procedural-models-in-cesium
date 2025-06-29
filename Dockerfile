FROM ubuntu:22.04


ARG BLENDER_LOCATION="/opt/blender"

RUN apt-get update && apt install  -y \
wget cmake libx11-dev libxxf86vm-dev libxcursor-dev libxi-dev libxrandr-dev libxinerama-dev libegl-dev \
libwayland-dev wayland-protocols libxkbcommon-dev libdbus-1-dev linux-libc-dev libsm6


RUN wget https://mirror.clarkson.edu/blender/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz && \
tar -xf blender-4.2.0-linux-x64.tar.xz && \
mv blender-4.2.0-linux-x64 ${BLENDER_LOCATION}

ENV PATH="${BLENDER_LOCATION}:${PATH}"

ENTRYPOINT ["blender", "--background"]
