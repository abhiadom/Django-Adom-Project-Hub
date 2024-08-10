FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    unzip \
    vim \
    nano \
    openocd \
    libusb-1.0-0-dev \
    libnewlib-arm-none-eabi \
    gdb-multiarch \
    gcc-arm-none-eabi \
    python3 \
    python3-pip \
    tmux \
    openssh-server \
    pkg-config \
    ca-certificates \
    usbutils \
    iputils-ping

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Install the Pico SDK
RUN mkdir -p /opt/pico-sdk
WORKDIR /opt/pico-sdk
RUN git clone https://github.com/raspberrypi/pico-sdk.git .
RUN git submodule update --init

# Set environment variables
ENV PICO_SDK_PATH=/opt/pico-sdk
ENV PATH=$PICO_SDK_PATH/bin:$PATH

# Clone and build picotool
RUN git clone https://github.com/raspberrypi/picotool.git /opt/picotool
WORKDIR /opt/picotool

# Build picotool
RUN mkdir build
WORKDIR /opt/picotool/build
RUN cmake .. && make

# Copy the built binary to /usr/local/bin
RUN cp picotool /usr/local/bin/

# Create a known password for root user
RUN echo 'root:adom@123' | chpasswd

# Configure SSH
RUN mkdir -p /root/.ssh
COPY id_ed25519.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Create config directory for code-server and disable authentication
RUN mkdir -p /root/.config/code-server
RUN echo "bind-addr: 0.0.0.0:8080\n" > /root/.config/code-server/config.yaml
RUN echo "auth: none\n" >> /root/.config/code-server/config.yaml

# Install necessary extensions
RUN /usr/lib/code-server/bin/code-server --install-extension ms-python.python \
    --install-extension twxs.cmake \
    --install-extension paulober.pico-w-go \
    --install-extension formulahendry.code-runner

# Copy settings.json and tasks.json
COPY .vscode/settings.json /root/.local/share/code-server/User/settings.json

# Create entrypoint script
RUN echo '#!/bin/sh\n\
/usr/lib/code-server/bin/code-server --bind-addr 0.0.0.0:8080 "$@"' > /usr/local/bin/code-server-entrypoint.sh
RUN chmod +x /usr/local/bin/code-server-entrypoint.sh

# Expose Ports
EXPOSE 22
EXPOSE 8080

CMD ["/bin/sh", "-c", "/usr/sbin/sshd -D & /usr/local/bin/code-server-entrypoint.sh /workspace"]