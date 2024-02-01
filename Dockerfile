### binary downloader
# Arch specific stages are required to set arg appropriately, see https://github.com/docker/buildx/issues/157#issuecomment-538048500

FROM alpine:3.19 AS builder-amd64
ARG ARCH=amd64

FROM alpine:3.19 AS builder-arm64
ARG ARCH=arm64

FROM builder-$TARGETARCH as builder

WORKDIR /tmp/ecr-credential-provider
COPY . .

ARG EFFECTIVE_VERSION

RUN wget -O ecr-credential-provider https://artifacts.k8s.io/binaries/cloud-provider-aws/$EFFECTIVE_VERSION/linux/$ARCH/ecr-credential-provider-linux-$ARCH && \
    chmod +x ecr-credential-provider

### actual container

FROM scratch

COPY --from=builder /tmp/ecr-credential-provider/ecr-credential-provider /bin/ecr-credential-provider

ENTRYPOINT ["/bin/ecr-credential-provider"]
