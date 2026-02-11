### binary downloader
# Arch specific stages are required to set arg appropriately, see https://github.com/docker/buildx/issues/157#issuecomment-538048500

FROM golang:1.24.12 AS builder-amd64
ARG ARCH=amd64

FROM golang:1.24.12 AS builder-arm64
ARG ARCH=arm64

FROM builder-$TARGETARCH AS builder

ARG EFFECTIVE_VERSION
WORKDIR /tmp/ecr-credential-provider

RUN git clone https://github.com/kubernetes/cloud-provider-aws.git -b $EFFECTIVE_VERSION .

RUN GO111MODULE=on CGO_ENABLED=0 GOOS=linux GOARCH="$ARCH" GOPROXY="$GOPROXY" go build \
    		-trimpath \
    		-ldflags="$LDFLAGS" \
    		-o=ecr-credential-provider \
    		cmd/ecr-credential-provider/*.go

### actual container

FROM scratch

COPY --from=builder /tmp/ecr-credential-provider/ecr-credential-provider /bin/ecr-credential-provider

ENTRYPOINT ["/bin/ecr-credential-provider"]
